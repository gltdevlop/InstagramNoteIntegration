import time
from tkinter import messagebox
import atexit
import psutil
from threading import Thread
from pystray import Icon, Menu, MenuItem
from PIL import Image
import note_node

# Global variables
last_game = None
start_time = None
icon = None


def on_exit():
    note_node.del_note()


atexit.register(on_exit)

# load game list func
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


# Detech a running game
def detect_running_game(game_dict):
    for process in psutil.process_iter(attrs=['name']):
        try:
            process_name = process.info['name'].lower()
            if process_name in game_dict:
                return game_dict[process_name]  # return the game name
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return None


# Main monitoring func
def game_monitor():
    global last_game, start_time

    while True:
        game_dict, dev_apps = load_game_list('list.txt')

        if game_dict or dev_apps:
            running_game = detect_running_game({**game_dict, **dev_apps})

            if running_game:
                if last_game != running_game:
                    start_time = time.perf_counter()
                    if running_game in dev_apps.values():
                        activity = "Coding on"
                    else:
                        activity = "Playing"
                    print(f"{activity} {running_game}")
                    note_node.send_note(f"{activity} {running_game} since 0 sec", 0)
                    last_game = running_game

                else:
                    end_time = time.perf_counter()
                    run_time = end_time - start_time
                    run_time_min = int(run_time / 60)

                    if running_game in dev_apps.values():
                        activity = "Coding on"
                    else:
                        activity = "Playing"

                    if run_time_min >= 60:
                        run_time_hr = round(run_time_min / 60, 0)
                        note_node.send_note(f"{activity} {running_game} since {run_time_hr}h", 0)
                    else:
                        note_node.send_note(f"{activity} {running_game} since {run_time_min} min", 0)

                    last_game = running_game
            else:
                if last_game != "nogame":
                    note_node.del_note()
                    last_game = "nogame"
                    print("Game closed")
                else:
                    print("No game is currently running")

        else:
            messagebox.showerror("Error",
                                 f"Game list is empty or failed to load.")
            print("Game list is empty or failed to load.")
            exit()

        time.sleep(120)


# Systray
def create_image():
    return Image.open("icon.ico")

# App exit
def quit_application(icon):
    note_node.del_note()
    icon.stop()
    # print("Application terminated.")

def actual_game():
    return None

# Main func to launch the app
def main():
    global icon

    # Context menu
    menu = Menu(
        MenuItem("Quitter l'app", quit_application)
    )

    # Open icon
    icon = Icon("IGNoteIntegration", create_image(), "IGNoteIntegration", menu)

    # Start monitoring games
    monitor_thread = Thread(target=game_monitor, daemon=True)
    monitor_thread.start()


    # Start in the systray
    icon.run()

if __name__ == "__main__":
    main()