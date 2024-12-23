import os
import time
from tkinter import messagebox
import atexit
import psutil
from threading import Thread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QComboBox, QPushButton
from PyQt5.QtCore import Qt
from pystray import Icon, Menu, MenuItem
from PIL import Image
import note_node
import gh_update
from session_logger import log_game_session
from load_list import load_game_data

last_game = None
start_time = None
icon = None
config = {}
translations = {}
shutdown_flag = False

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

def t(key):
    lang = config.get('language', 'en').lower()
    return translations.get(lang, {}).get(key, key)

# On exit
def on_exit():
    global shutdown_flag
    shutdown_flag = True
    note_node.del_note()

atexit.register(on_exit)


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

def detect_running_game(game_dict):
    for process in psutil.process_iter(attrs=['name']):
        try:
            process_name = process.info['name'].lower()
            if process_name in game_dict:
                return game_dict[process_name]
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return None

def game_monitor():
    global last_game, start_time

    while not shutdown_flag:
        load_config('_internal/config.txt')

        game_dict, dev_apps = load_game_data()  # Charge les données des jeux et des IDE

        if game_dict or dev_apps:
            # Fusionner les jeux et les applications de développement pour la détection
            running_game = detect_running_game({**game_dict, **dev_apps})

            if running_game:
                # Détecter si c'est un jeu ou un IDE
                if running_game in dev_apps.values():
                    activity = t("Coding on")  # Message pour les IDE
                else:
                    activity = t("Playing")  # Message pour les jeux

                # Si le jeu/IDE a changé
                if last_game != running_game:
                    if last_game and start_time:
                        end_time = time.perf_counter()
                        log_game_session(last_game, note_node.username, start_time, end_time)

                    start_time = time.perf_counter()
                    note_content = f"{activity} {running_game}"

                    if config.get('time_update', False):
                        note_content += f" {t('since')} 0 {t('min')}"

                    note_node.send_note(note_content, 0)
                    last_game = running_game

                # Mise à jour du temps de jeu toutes les 10 minutes si activé
                elif config.get('time_update', False):
                    end_time = time.perf_counter()
                    run_time = end_time - start_time
                    run_time_min = int(run_time / 60)

                    if run_time_min % 10 == 0:
                        note_node.send_note(f"{activity} {running_game} {t('since')} {run_time_min} {t('min')}", 0)

            else:
                if last_game and start_time:
                    end_time = time.perf_counter()
                    log_game_session(last_game, note_node.username, start_time, end_time)

                if last_game != "nogame":
                    note_node.del_note()
                    last_game = None
                    print(t("Game closed"))
                else:
                    print(t("No game is currently running"))

        else:
            print(t("Game list is empty or failed to load."))

        time.sleep(1 if not config.get('time_update', False) else 600)

    if last_game and start_time:
        end_time = time.perf_counter()
        log_game_session(last_game, note_node.username, start_time, end_time)
    note_node.del_note()


def refresh_all(icon, item):
    load_config('_internal/config.txt')
    load_translations('_internal/translations.txt')

def create_image():
    return Image.open("_internal/icon.ico")

def quit_application(icon):
    note_node.del_note()
    icon.stop()

def save_config(file_path):
    try:
        with open(file_path, 'w') as file:
            for key, value in config.items():
                file.write(f"{key}: {value}\n")
    except Exception as e:
        print(f"Error saving config: {e}")

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(t("Settings - IGNoteIntegration"))
        self.setFixedSize(330, 150)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.time_update_checkbox = QCheckBox(t("Time Update"))
        self.setWindowIcon(QIcon("_internal/icon.ico"))
        self.time_update_checkbox.setChecked(config.get('time_update', False))
        layout.addWidget(self.time_update_checkbox)

        self.share_data_checkbox = QCheckBox(t("Share Data"))
        self.share_data_checkbox.setChecked(config.get('share_data', False))
        layout.addWidget(self.share_data_checkbox)

        language_layout = QHBoxLayout()
        language_label = QLabel(t("Language"))
        self.language_selector = QComboBox()
        self.language_selector.addItems(["EN", "FR"])
        self.language_selector.setCurrentText(config.get('language', 'EN').upper())
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_selector)
        layout.addLayout(language_layout)

        save_button = QPushButton(t("Save"))
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button, alignment=Qt.AlignRight)

        self.setLayout(layout)

    def save_settings(self):
        config['time_update'] = self.time_update_checkbox.isChecked()
        config['share_data'] = self.share_data_checkbox.isChecked()
        config['language'] = self.language_selector.currentText().upper()
        save_config('_internal/config.txt')
        load_config('_internal/config.txt')
        messagebox.showinfo(t("Settings"), t("Settings saved successfully!"))
        self.close()

def update_share_data_setting(share_data_enabled):
    """Update the share_data setting in the config file."""
    config_path = '_internal/config.txt'
    with open(config_path, 'r') as file:
        lines = file.readlines()

    with open(config_path, 'w') as file:
        for line in lines:
            if line.startswith('share_data:'):
                file.write(f'share_data: {str(share_data_enabled)}\n')
            else:
                file.write(line)

def open_settings_window():
    def run_window():
        app = QApplication([])
        settings_window = SettingsWindow()
        settings_window.show()
        app.exec_()

    settings_thread = Thread(target=run_window, daemon=True)
    settings_thread.start()

def check_up():
    def check():
        gh_update.update_application_wanted()

    checkup_thread = Thread(target=check, daemon=True)
    checkup_thread.start()

def web_open():
    os.system("start \"\" http://ign.edl360.fr")

def main():
    global icon
    current_version = gh_update.get_current_version()

    load_config('_internal/config.txt')
    load_translations('_internal/translations.txt')

    menu = Menu(
        MenuItem(t("Settings"), open_settings_window),
        MenuItem("IGN Website", web_open),
        MenuItem(t("Refresh all"), refresh_all),
        MenuItem(f"Version : {current_version} (click to check update)", check_up),
        MenuItem(t("Quit the app"), quit_application)
    )

    icon = Icon("IGNoteIntegration", create_image(), "IGNoteIntegration", menu)

    monitor_thread = Thread(target=game_monitor, daemon=True)
    monitor_thread.start()

    icon.run()

if __name__ == "__main__":
    gh_update.update_application()
    main()
