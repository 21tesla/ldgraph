import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QEvent
from ldgraph.ui.main_window import MainWindow
from ldgraph.core.updater import VERSION

class LDGraphApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.window = None

    def event(self, event):
        if event.type() == QEvent.Type.FileOpen:
            file_path = event.file()
            if self.window:
                self.window.load_file_directly(file_path)
            else:
                # Store the path to be loaded once the window is created
                self.initial_file = file_path
            return True
        return super().event(event)

def main():
    app = LDGraphApp(sys.argv)
    app.initial_file = None
    
    # Check CLI args
    file_path = None
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    
    # If a FileOpen event happened before the window was ready
    if app.initial_file:
        file_path = app.initial_file

    app.window = MainWindow(file_path=file_path)
    app.window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()



