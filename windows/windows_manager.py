import os.path
import sys
import json
from PyQt5.QtWidgets import QApplication
from windows.login_window import LoginPage
from windows.main_window import MainWindow
import nodes.variables_node as vn


class AppManager:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.login_page = LoginPage()
        self.main_window = None

        # Connect signal for successful login
        self.login_page.login_successful.connect(self.show_main_window)

    def show_login_page(self):
        self.login_page.show()

    def show_main_window(self, session_token=None, username=None):
        if not session_token or not username:
            # Load session_token and username from the file if not provided
            with open(vn.cookie_connect, "r") as file:
                data = json.load(file)
                session_token = data.get("session_token")
                username = data.get("username")

        self.login_page.close()  # Close login page
        self.main_window = MainWindow()
        self.main_window.show()

    def run(self):
        if not os.path.exists(vn.cookie_connect):
            self.show_login_page()
        else:
            self.show_main_window()  # No need to pass arguments; it will load from the file
        sys.exit(self.app.exec_())

def start_app():
    app_manager = AppManager()
    app_manager.run()

