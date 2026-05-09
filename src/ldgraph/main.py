import sys
import os
from PyQt6.QtWidgets import QApplication
from ldgraph.ui.main_window import MainWindow
from ldgraph.core.updater import VERSION

def main():
    app = QApplication(sys.argv)
    
    file_path = None
    if len(sys.argv) > 1:
        file_path = sys.argv[1]

    window = MainWindow(file_path=file_path)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()



