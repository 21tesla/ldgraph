from PyQt6.QtGui import QAction

class MenuBuilder:
    def __init__(self, main_window):
        self.mw = main_window

    def build(self):
        menubar = self.mw.menuBar()
        menubar.setNativeMenuBar(True)

        file_menu = menubar.addMenu("File")

        load_action = QAction("Load data", self.mw)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.mw.on_load)
        file_menu.addAction(load_action)

        save_fit_action = QAction("Save fit", self.mw)
        save_fit_action.setShortcut("Ctrl+S")
        save_fit_action.triggered.connect(self.mw.on_save_fit)
        file_menu.addAction(save_fit_action)

        export_action = QAction("Export plot", self.mw)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.mw.on_export)
        file_menu.addAction(export_action)

        extras_menu = menubar.addMenu("Extras")

        update_action = QAction("Check for updates...", self.mw)
        update_action.triggered.connect(self.mw.updater.check_for_updates)
        extras_menu.addAction(update_action)
