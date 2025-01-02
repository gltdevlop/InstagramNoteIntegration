from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton
from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtCore import Qt, QPoint
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window size
        self.setFixedSize(900, 500)

        # Set window background color
        self.setStyleSheet("background-color: #1b1b1b;")

        # Remove window frame
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Set window title (optional, won't be visible in frameless mode)
        self.setWindowTitle("RankPulse")

        # Initialize position tracking for dragging
        self._drag_pos = None

        # Example of using a custom font
        label = QLabel("RankPulse", self)
        label.setFont(QFont("Rubik", 16, QFont.Bold))  # Set custom font (name and size)
        label.setStyleSheet("color: white;")  # Optional: Set text color
        label.adjustSize()
        label.move(15, 15)  # Position the label

        # Add custom close button
        close_button = QPushButton("X", self)
        close_button.setFont(QFont("Rubik", 12, QFont.Bold))  # Custom font for button
        close_button.setStyleSheet("color: white; background: none; border: none;")
        close_button.setFixedSize(30, 30)
        close_button.move(self.width() - 40, 10)  # Position the button in the top-right corner
        close_button.clicked.connect(self.close)  # Connect the button to the close method

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

    # Set a global custom font for the application (optional)
    app.setFont(QFont("Arial", 12))

    # Create and show the main window
    window = MainWindow()
    window.show()

    # Execute the application
    sys.exit(app.exec_())
