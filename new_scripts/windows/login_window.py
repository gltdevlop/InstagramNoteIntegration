import json
import time

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QLineEdit
from PyQt5.QtGui import QFont, QRegion
from PyQt5.QtCore import Qt, QTimer, QRect, pyqtSignal
import sys
import new_scripts.nodes.variables_node as vn

from new_scripts.managers.connect_manager import login_to_server
from new_scripts.managers.connect_manager import create_account


class LoginPage(QMainWindow):
    login_successful = pyqtSignal(str, str)  # Signal for session_token and username

    def __init__(self):
        super().__init__()

        self.setWindowTitle("RankPulse")
        self._drag_pos = None


        self.is_signup_mode = False  # Track whether the user is in signup mode
        self.password_visible = False  # Track password visibility

        def toggle_mode():
            self.is_signup_mode = not self.is_signup_mode
            if self.is_signup_mode:
                self.username_input.clear()
                self.password_input.clear()
                login_button.setText("Sign Up")
                signup_text.setText("I prefer to login")
                signup_text.adjustSize()
                signup_text.move((self.width() - signup_text.width()) // 2, 420)
                login_button.clicked.disconnect()
                login_button.clicked.connect(signup_act)
            else:
                login_button.setText("Login")
                self.username_input.clear()
                self.password_input.clear()
                signup_text.setText("I prefer to sign up")
                signup_text.adjustSize()
                signup_text.move((self.width() - signup_text.width()) // 2, 420)
                login_button.clicked.disconnect()
                login_button.clicked.connect(login_act)

        def toggle_password_visibility():
            self.password_visible = not self.password_visible
            if self.password_visible:
                self.password_input.setEchoMode(QLineEdit.Normal)
                show_hide_button.setText("Hide")
            else:
                self.password_input.setEchoMode(QLineEdit.Password)
                show_hide_button.setText("Show")

        def login_act():
            def reset_fields():
                self.username_input.setReadOnly(False)
                self.password_input.setReadOnly(False)
                login_button.setEnabled(True)
            if not self.username_input.text() or not self.password_input.text():
                self.username_input.clear()
                self.password_input.clear()
                self.notification_label.setText("Both fields are required!")
                self.notification_label.adjustSize()
                self.notification_label.move((self.width() - self.notification_label.width()) // 2, 440)
                self.notification_label.show()
                QTimer.singleShot(3000, self.notification_label.hide)
            else:
                login_button.setEnabled(False)
                self.username_input.setReadOnly(True)
                self.password_input.setReadOnly(True)

                username = self.username_input.text()
                password = self.password_input.text()
                login = login_to_server(f"{vn.api_url}/login", username, password, verify_ssl=False)

                if login.get("success"):
                    session_token = login["data"].get("session_token")
                    if session_token:
                        self.save_session(session_token, username)
                        self.login_successful.emit(session_token, username)
                    else:
                        print("Error: Session token is missing in the response.")
                else:
                    print("Erreur:", login["error"])
                    self.notification_label.setText("Login failed. Try again.")
                    self.notification_label.setStyleSheet("color: red;")
                    self.notification_label.adjustSize()
                    self.notification_label.move((self.width() - self.notification_label.width()) // 2, 440)
                    self.notification_label.show()
                    reset_fields()
                    QTimer.singleShot(3000, self.notification_label.hide)

        def signup_act():
            def reset_fields():
                self.username_input.setReadOnly(False)
                self.password_input.setReadOnly(False)
                login_button.setEnabled(True)

            if not self.username_input.text() or not self.password_input.text():
                self.username_input.clear()
                self.password_input.clear()
                self.notification_label.setText("Both fields are required!")
                self.notification_label.adjustSize()
                self.notification_label.move((self.width() - self.notification_label.width()) // 2, 440)
                self.notification_label.show()
                QTimer.singleShot(3000, self.notification_label.hide)
            else:
                login_button.setEnabled(False)
                self.username_input.setReadOnly(True)
                self.password_input.setReadOnly(True)

                username = self.username_input.text()
                password = self.password_input.text()
                sgup = create_account(f"{vn.api_url}/claim", username, password, verify_ssl=False)

                if sgup.get("success"):
                    time.sleep(2)
                    login = login_to_server(f"{vn.api_url}/login", username, password, verify_ssl=False)

                    if login.get("success"):
                        session_token = login["data"].get("session_token")
                        if session_token:
                            self.save_session(session_token, username)
                            self.login_successful.emit(session_token, username)
                        else:
                            print("Error: Session token is missing in the response.")
                else:
                    print("Erreur:", sgup["error"])
                    self.notification_label.setText("Signup failed. Try again.")
                    self.notification_label.setStyleSheet("color: red;")
                    self.notification_label.adjustSize()
                    self.notification_label.move((self.width() - self.notification_label.width()) // 2, 440)
                    self.notification_label.show()
                    reset_fields()
                    QTimer.singleShot(3000, self.notification_label.hide)

        self.setFixedSize(900, 500)
        self.setStyleSheet("background-color: #1b1b1b;")
        self.setWindowFlags(Qt.FramelessWindowHint)

        title_label = QLabel("Welcome to RankPulse 👋", self)
        title_label.setFont(QFont("Rubik", 24, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.adjustSize()
        title_label.move((self.width() - title_label.width()) // 2, 80)

        username_label = QLabel("Username", self)
        username_label.setFont(QFont("Rubik", 12))
        username_label.setStyleSheet("color: white;")
        username_label.adjustSize()
        username_label.move((self.width() - 300) // 2, 180)

        self.username_input = QLineEdit(self)
        self.username_input.setFixedSize(300, 40)
        self.username_input.setStyleSheet(
            """
            QLineEdit {
                background-color: #3a3a3a;
                border: none;
                border-radius: 10px;
                color: white;
                padding-left: 10px;
            }
            """
        )
        self.username_input.move((self.width() - 300) // 2, 210)

        password_label = QLabel("Password", self)
        password_label.setFont(QFont("Rubik", 12))
        password_label.setStyleSheet("color: white;")
        password_label.adjustSize()
        password_label.move((self.width() - 300) // 2, 270)

        self.password_input = QLineEdit(self)
        self.password_input.setFixedSize(300, 40)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(
            """
            QLineEdit {
                background-color: #3a3a3a;
                border: none;
                border-radius: 10px;
                color: white;
                padding-left: 10px;
            }
            """
        )
        self.password_input.move((self.width() - 300) // 2, 300)

        show_hide_button = QPushButton("Show", self)
        show_hide_button.setFont(QFont("Rubik", 10))
        show_hide_button.setStyleSheet(
            """
            QPushButton {
                background-color: #3a3a3a;
                border: none;
                border-radius: 10px;
                color: white;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            """
        )
        show_hide_button.setFixedSize(80, 40)
        show_hide_button.move((self.width() - 300) // 2 + 310, 300)
        show_hide_button.clicked.connect(toggle_password_visibility)

        login_button = QPushButton("Login", self)
        login_button.setFont(QFont("Rubik", 12))
        login_button.setStyleSheet(
            """
            QPushButton {
                background-color: #2d2d2d;
                border: none;
                border-radius: 20px;
                color: white;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            """
        )
        login_button.setFixedSize(300, 50)
        login_button.move((self.width() - 300) // 2, 360)
        login_button.clicked.connect(login_act)

        self.notification_label = QLabel("", self)
        self.notification_label.setFont(QFont("Rubik", 10))
        self.notification_label.setStyleSheet("color: red;")
        self.notification_label.hide()

        signup_text = QLabel("I prefer to sign up", self)
        signup_text.setFont(QFont("Rubik", 10))
        signup_text.setStyleSheet("color: #2d89ef; cursor: pointer;")
        signup_text.adjustSize()
        signup_text.move((self.width() - signup_text.width()) // 2, 420)
        signup_text.mousePressEvent = lambda event: toggle_mode()

        close_button = QPushButton("X", self)
        close_button.setFont(QFont("Rubik", 12, QFont.Bold))
        close_button.setStyleSheet("color: white; background: none; border: none;")
        close_button.setFixedSize(30, 30)
        close_button.move(self.width() - 40, 10)
        close_button.clicked.connect(self.close)

    def save_session(self, session_token, username):
        with open(vn.cookie_connect, "w") as file:
            json.dump({"session_token": session_token, "username": username}, file)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = None
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Rubik", 12))

    window = LoginPage()
    window.show()

    sys.exit(app.exec_())
