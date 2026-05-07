import sys
import os
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from core.updater import VERSION

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
