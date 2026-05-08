import sys
import os
from PyQt6.QtWidgets import QApplication
from ldgraph.ui.main_window import MainWindow
from ldgraph.core.updater import VERSION

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()



