import os
import subprocess
import sys
import time
import json
from tkinter import messagebox
import atexit
import mysql.connector
import psutil
from threading import Thread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QComboBox, QPushButton
from PyQt5.QtCore import Qt
from pystray import Icon, Menu, MenuItem
from PIL import Image
import note_node
import gh_update
from db_credentials import TRANSLATION_DB
from session_logger import log_game_session
from load_list import load_game_data
from config_manager import ConfigManager
import variables_node as vn

last_game = vn.last_game
start_time = vn.start_time
icon = vn.icon
config_manager = ConfigManager()
translations_cache = vn.translations_cache
shutdown_flag = vn.shutdown_flag
translation_file = vn.translation_file
creds_file = vn.creds
app_name = vn.app_name
website = vn.website

if os.path.exists(creds_file):
    with open(creds_file, "r", encoding="utf-8") as f:
        creds = f.readlines()
        username = creds[0].strip()

def download_translations():
    """Download all translations from the database and save them to a JSON file."""
    global translations_cache
    try:
        conn = mysql.connector.connect(**TRANSLATION_DB)
    except mysql.connector.Error as e:
        messagebox.showerror("Connexion Error", f"Unable to connect to database. Error: {e}")
        sys.exit(1)

    try:
        cursor = conn.cursor()
        cursor.execute('SELECT language, `key`, `value` FROM translations')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        translations = {}
        for lang, key, value in rows:
            if lang not in translations:
                translations[lang] = {}
            translations[lang][key] = value

        with open(translation_file, 'w', encoding='utf-8') as f:
            json.dump(translations, f, ensure_ascii=False, indent=4)

        translations_cache = translations
        print("Translations successfully downloaded and cached.")

    except Exception as e:
        print(f"Error downloading translations: {e}")
        if os.path.exists(translation_file):
            with open(translation_file, 'r', encoding='utf-8') as f:
                translations_cache = json.load(f)


def load_translations_from_file():
    global translations_cache
    download_translations()
    try:
        with open(translation_file, 'r', encoding='utf-8') as f:
            translations_cache = json.load(f)
        print("Translations loaded from file.")
    except FileNotFoundError:
        print("Translation file not found. Downloading translations...")
        download_translations()
    except Exception as e:
        print(f"Error loading translations from file: {e}")


def t(key):
    lang = config_manager.get('language', 'EN').upper()
    if lang not in translations_cache:
        print(f"Warning: Language '{lang}' not found in translations. Falling back to key.")
        return key
    return translations_cache.get(lang, {}).get(key, key)

def on_exit():
    global shutdown_flag
    shutdown_flag = True
    note_node.del_note()

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
        try:
            game_dict, dev_apps = load_game_data()

            if game_dict or dev_apps:
                running_game = detect_running_game({**game_dict, **dev_apps})

                if running_game:
                    if running_game in dev_apps.values():
                        activity = t("Coding on")
                    else:
                        activity = t("Playing")

                    if last_game != running_game:
                        if last_game and start_time:
                            end_time = time.perf_counter()
                            try:
                                log_game_session(last_game, username, start_time, end_time)
                            except Exception as e:
                                print(f"Error logging game session: {e}")

                        start_time = time.perf_counter()
                        note_content = f"{activity} {running_game}"

                        if config_manager.get('time_update', False):
                            note_content += f" {t('since')} 0 {t('min')}"

                        try:
                            note_node.send_note(note_content, 0)
                            last_game = running_game
                            icon.menu = create_menu()

                        except Exception as e:
                            print(f"Error sending note: {e}")

                    elif config_manager.get('time_update', False):
                        end_time = time.perf_counter()
                        run_time = end_time - start_time
                        run_time_min = int(run_time / 60)

                        if run_time_min % 10 == 0:
                            try:
                                note_node.send_note(f"{activity} {running_game} {t('since')} {run_time_min} {t('min')}", 0)
                            except Exception as e:
                                print(f"Error updating note: {e}")

                else:
                    if last_game and start_time:
                        end_time = time.perf_counter()
                        try:
                            log_game_session(last_game, username, start_time, end_time)
                        except Exception as e:
                            print(f"Error logging final game session: {e}")

                    if last_game is not None:
                        try:
                            note_node.del_note()
                            last_game = None
                            print(t("Game closed"))
                        except Exception as e:
                            print(f"Error deleting note: {e}")
                    else:
                        print(t("No game is currently running"))

            else:
                print(t("Game list is empty or failed to load."))

        except Exception as e:
            print(f"Error in game monitor: {e}")

        time.sleep(1 if not config_manager.get('time_update', False) else 600)

    if last_game and start_time:
        end_time = time.perf_counter()
        try:
            log_game_session(last_game, username, start_time, end_time)
        except Exception as e:
            print(f"Error logging final session: {e}")
    try:
        note_node.del_note()
    except Exception as e:
        print(f"Error deleting final note: {e}")


def is_process_already_running(process_name):

    current_pid = os.getpid()

    # Iterate through all running processes
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'].lower() == process_name.lower() and proc.pid != current_pid:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    return False

def create_image():
    return Image.open("_internal/icon.ico")

def create_menu():
    current_version = gh_update.get_current_version()
    current_game_display = last_game if last_game else t("XXX")

    return Menu(
        MenuItem(f"{t('Current Game/IDE')}: {current_game_display}", lambda: None),
        MenuItem(t("Access the IGN Website"), web_open),
        Menu.SEPARATOR,
        MenuItem(t("Settings"), open_settings_window),
        MenuItem(t("Check updates") + t(" (actual version: ") + f"{current_version})", check_up),
        Menu.SEPARATOR,
        MenuItem(t("Quit the app"), quit_application)
    )

def quit_application(icon):
    note_node.del_note()
    icon.stop()

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(t(f"Settings - IGNoteIntegration"))
        self.setFixedSize(330, 150)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.time_update_checkbox = QCheckBox(t("Time Update"))
        self.setWindowIcon(QIcon("_internal/icon.ico"))
        self.time_update_checkbox.setChecked(config_manager.get('time_update', False))
        layout.addWidget(self.time_update_checkbox)

        self.share_data_checkbox = QCheckBox(t("Share Data"))
        self.share_data_checkbox.setChecked(config_manager.get('share_data', True))
        layout.addWidget(self.share_data_checkbox)

        language_layout = QHBoxLayout()
        language_label = QLabel(t("Language"))
        self.language_selector = QComboBox()
        self.language_selector.addItems(["EN", "FR"])
        self.language_selector.setCurrentText(config_manager.get('language', 'EN').upper())
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_selector)
        layout.addLayout(language_layout)

        save_button = QPushButton(t("Save"))
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button, alignment=Qt.AlignRight)

        self.setLayout(layout)

    def save_settings(self):
        new_config = {
            'time_update': self.time_update_checkbox.isChecked(),
            'share_data': self.share_data_checkbox.isChecked(),
            'language': self.language_selector.currentText().upper()
        }
        config_manager.update(new_config)
        download_translations()

        icon.menu = create_menu()

        messagebox.showinfo(t("Settings"), t("Settings saved successfully!"))
        self.close()

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
    subprocess.run(f"start \"\" {website}", creationflags=subprocess.CREATE_NO_WINDOW, shell=True)

def detect_process():
    process_name = vn.exe
    if is_process_already_running(process_name):
        sys.exit(0)

def main():
    global icon

    load_translations_from_file()

    # Create the initial menu
    menu = create_menu()

    icon = Icon(app_name, create_image(), app_name, menu)

    monitor_thread = Thread(target=game_monitor, daemon=True)
    monitor_thread.start()

    icon.run()

if __name__ == "__main__":
    print(f"\nWelcome to IGN, version {gh_update.get_current_version()}\n")

    atexit.register(on_exit)

    gh_update.update_application()
    detect_process()
    note_node.main()
    main()
