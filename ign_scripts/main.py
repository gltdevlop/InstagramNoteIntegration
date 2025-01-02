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


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(t(f"Settings - IGNoteIntegration"))
        self.setFixedSize(330, 150)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.time_update_checkbox = QCheckBox(t("Time Update"))
        self.setWindowIcon(QIcon("../_internal/icon.ico"))
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
