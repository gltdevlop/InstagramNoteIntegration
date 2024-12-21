import time
from tkinter import messagebox
import atexit
import psutil
from threading import Thread
from pystray import Icon, Menu, MenuItem
from PIL import Image
import note_node
import gh_update

last_game = None
start_time = None
icon = None
config = {}
translations = {}

# Load translations from file
def load_translations(file_path):
    global translations
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            current_lang = None
            for line in file:
                line = line.strip()
                if line.startswith("[") and line.endswith("]"):
                    current_lang = line[1:-1].lower()
                    translations[current_lang] = {}
                elif ":" in line and current_lang:
                    key, value = map(str.strip, line.split(":", 1))
                    translations[current_lang][key] = value
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")

# Get translated text
def t(key):
    lang = config.get('language', 'en').lower()
    return translations.get(lang, {}).get(key, key)

# On exit
def on_exit():
    note_node.del_note()

atexit.register(on_exit)

# Load configuration from file
def load_config(file_path):
    global config
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if ':' in line:
                    key, value = map(str.strip, line.split(':', 1))
                    config[key.lower()] = value.lower() if key.lower() == 'language' else value.lower() == 'true'
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")

# Load game list
def load_game_list(file_path):
    games = {}
    dev_apps = {}
    try:
        with open(file_path, 'r') as file:
            is_dev_section = False
            for line in file:
                if line.strip() == "---":
                    is_dev_section = True
                    continue
                if " - " in line:  # Good formatting check
                    exe, name = map(str.strip, line.split(" - ", 1))
                    if is_dev_section:
                        dev_apps[exe.lower()] = name
                    else:
                        games[exe.lower()] = name
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    return games, dev_apps

# Detect a running game
def detect_running_game(game_dict):
    for process in psutil.process_iter(attrs=['name']):
        try:
            process_name = process.info['name'].lower()
            if process_name in game_dict:
                return game_dict[process_name]  # return the game name
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return None

# Main monitoring function
def game_monitor():
    global last_game, start_time

    while True:
        # Reload configuration
        load_config('_internal/config.txt')

        game_dict, dev_apps = load_game_list('_internal/list.txt')

        if game_dict or dev_apps:
            running_game = detect_running_game({**game_dict, **dev_apps})

            if running_game:
                if last_game != running_game:
                    start_time = time.perf_counter()
                    activity = t("Coding on") if running_game in dev_apps.values() else t("Playing")
                    note_content = f"{activity} {running_game}"

                    if config.get('time_update', False):
                        note_content += f" {t('since')} 0 {t('min')}"

                    note_node.send_note(note_content, 0)
                    last_game = running_game

                elif config.get('time_update', False):
                    end_time = time.perf_counter()
                    run_time = end_time - start_time
                    run_time_min = int(run_time / 60)

                    if run_time_min % 10 == 0:  # Update every 10 minutes
                        activity = t("Coding on") if running_game in dev_apps.values() else t("Playing")
                        note_node.send_note(f"{activity} {running_game} {t('since')} {run_time_min} {t('min')}", 0)
            else:
                if last_game != "nogame":
                    note_node.del_note()
                    last_game = "nogame"
                    print(t("Game closed"))
                else:
                    print(t("No game is currently running"))

        else:
            messagebox.showerror("Error", t("Game list is empty or failed to load."))
            print(t("Game list is empty or failed to load."))
            exit()

        # Adjust sleep interval based on time_update setting
        time.sleep(60 if not config.get('time_update', False) else 600)

# Refresh configurations and translations
def refresh_all(icon, item):
    load_config('_internal/config.txt')
    load_translations('_internal/translations.txt')

# Systray
def create_image():
    return Image.open("_internal/icon.ico")

# App exit
def quit_application(icon):
    note_node.del_note()
    icon.stop()

# Main function to launch the app
def main():
    global icon

    # Load initial configuration and translations
    load_config('_internal/config.txt')
    load_translations('_internal/translations.txt')

    # Context menu
    menu = Menu(
        MenuItem(t("Refresh all"), refresh_all),  # Add Refresh All button
        MenuItem(t("Quit the app"), quit_application)
    )

    # Open icon
    icon = Icon("IGNoteIntegration", create_image(), "IGNoteIntegration", menu)

    # Start monitoring games
    monitor_thread = Thread(target=game_monitor, daemon=True)
    monitor_thread.start()

    # Start in the systray
    icon.run()

if __name__ == "__main__":
    gh_update.update_application()
    main()
