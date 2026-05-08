from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QCheckBox, QLabel, QMessageBox, QComboBox,
                             QGroupBox, QLineEdit, QFormLayout, QFileDialog)
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtCore import Qt
import numpy as np
from ldgraph.ui.plot_widget import PlotWidget
from ldgraph.ui.io_controller import IOController
from ldgraph.core.binding_model import AVAILABLE_MODELS, generic_fit
from ldgraph.core.config import get_model_params, save_model_params
from ldgraph.ui.menu_builder import MenuBuilder
from ldgraph.core.updater import Updater

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ldgraph - Ligand Binding Titration")
        self.resize(800, 700)
        
        self.io_controller = IOController(self)
        self.updater = Updater(self)
        self.x_data = None
        self.y_data = None
        self.popt = None
        self.param_widgets = {}
        
        self.init_ui()
        # Initialize parameters for the default selected model
        self.on_model_changed()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Build Native Menus
        self.menu_builder = MenuBuilder(self)
        self.menu_builder.build()

        # Toolbar/Button area
        controls_layout = QHBoxLayout()

        self.model_combo = QComboBox()
        self.model_combo.addItems(list(AVAILABLE_MODELS.keys()))
        self.model_combo.currentIndexChanged.connect(self.on_model_changed)
        controls_layout.addWidget(self.model_combo)
        
        self.reset_btn = QPushButton("Reset Params")
        self.reset_btn.clicked.connect(self.on_reset_params)
        controls_layout.addWidget(self.reset_btn)
        
        self.fit_btn = QPushButton("Fit Data")
        self.fit_btn.clicked.connect(self.on_fit)
        self.fit_btn.setEnabled(False)
        controls_layout.addWidget(self.fit_btn)
        
        self.export_btn = QPushButton("Export Plot")
        self.export_btn.clicked.connect(self.on_export)
        self.export_btn.setEnabled(False)
        controls_layout.addWidget(self.export_btn)
        
        self.log_x_checkbox = QCheckBox("Log X-Axis")
        self.log_x_checkbox.stateChanged.connect(self.on_toggle_log_x)
        controls_layout.addWidget(self.log_x_checkbox)
        
        self.log_y_checkbox = QCheckBox("Log Y-Axis")
        self.log_y_checkbox.stateChanged.connect(self.on_toggle_log_y)
        controls_layout.addWidget(self.log_y_checkbox)
        
        layout.addLayout(controls_layout)
        
        # Parameters Area
        self.params_group = QGroupBox("Starting Parameters (p0) & Fit Results")
        self.params_layout = QHBoxLayout()
        self.params_group.setLayout(self.params_layout)
        layout.addWidget(self.params_group)
        
        # Plot area
        self.plot_widget = PlotWidget()
        layout.addWidget(self.plot_widget)
        
        # Status area
        self.status_label = QLabel("Load data (File > Load data) to begin.")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                elif item.layout() is not None:
                    self.clear_layout(item.layout())
                    item.layout().deleteLater()
                # If it's a spacer item, taking it out is enough

    def on_model_changed(self):
        # Clear existing parameter inputs
        self.clear_layout(self.params_layout)
        
        self.param_widgets.clear()
        
        model_name = self.model_combo.currentText()
        model_config = AVAILABLE_MODELS[model_name]
        default_params = model_config["default_params"]
        
        # Load from dotfile or defaults
        saved_p0 = get_model_params(model_name, default_params)
        
        # Rebuild parameter UI
        for (param_name, _), param_data in zip(default_params.items(), saved_p0):
            val = param_data["value"]
            is_fixed = param_data.get("fixed", False)
            
            block_layout = QVBoxLayout()
            
            # Top row: Checkbox and Label
            top_row = QHBoxLayout()
            chk = QCheckBox("Fix")
            chk.setChecked(is_fixed)
            lbl = QLabel(f"<b>{param_name}</b>")
            top_row.addWidget(chk)
            top_row.addWidget(lbl)
            top_row.addStretch()
            
            # Bottom row: LineEdit and Error Label
            bot_row = QHBoxLayout()
            inp = QLineEdit(f"{val:.6g}")
            inp.setValidator(QDoubleValidator())
            inp.setFixedWidth(80)
            err_lbl = QLabel("± --")
            bot_row.addWidget(inp)
            bot_row.addWidget(err_lbl)
            bot_row.addStretch()
            
            block_layout.addLayout(top_row)
            block_layout.addLayout(bot_row)
            
            self.params_layout.addLayout(block_layout)
            self.param_widgets[param_name] = {"input": inp, "check": chk, "err": err_lbl}
            
        self.params_layout.addStretch()

    def on_load(self):
        x, y, x_label, y_label, error = self.io_controller.load_data()
        if error:
            QMessageBox.critical(self, "Error", f"Failed to load data: {error}")
            return
        if x is not None:
            self.x_data = x
            self.y_data = y
            self.plot_widget.set_data(x, y)
            self.plot_widget.set_labels(x_label, y_label)
            self.fit_btn.setEnabled(True)
            self.export_btn.setEnabled(True)
            self.status_label.setText(f"Loaded {len(x)} points.")
            # Clear previous fit
            self.plot_widget.set_fit([], [])
            self.popt = None

    def on_fit(self):
        if self.x_data is None:
            return
        
        model_name = self.model_combo.currentText()
        model_config = AVAILABLE_MODELS[model_name]
        
        # Extract p0 and free_mask from UI
        p0 = []
        free_mask = []
        param_names = []
        fixed_flags = []
        
        for name, widgets in self.param_widgets.items():
            try:
                val = float(widgets["input"].text())
                is_fixed = widgets["check"].isChecked()
                p0.append(val)
                free_mask.append(not is_fixed)
                fixed_flags.append(is_fixed)
                param_names.append(name)
            except ValueError:
                QMessageBox.warning(self, "Invalid Input", f"Please enter a valid number for {name}.")
                return
                
        # Save the new p0 and states to config
        save_model_params(model_name, param_names, p0, fixed_flags)
        
        # Fit
        popt, perr = generic_fit(
            model_config["model_func"], 
            self.x_data, 
            self.y_data, 
            p0, 
            free_mask,
            bounds=model_config.get("bounds")
        )
        
        if popt is not None:
            self.popt = popt
            self.status_label.setText("Fit successful.")
            
            # Repopulate UI with fitted values and errors
            for idx, (name, widgets) in enumerate(self.param_widgets.items()):
                widgets["input"].setText(f"{popt[idx]:.6g}")
                if not fixed_flags[idx]:
                    widgets["err"].setText(f"± {perr[idx]:.4g}")
                else:
                    widgets["err"].setText("± 0 (fixed)")
            
            # Generate fit curve
            x_min = max(self.x_data[self.x_data > 0].min(), 1e-3) if len(self.x_data[self.x_data > 0]) > 0 else 1e-3
            x_fit = np.logspace(np.log10(x_min), np.log10(self.x_data.max()), 500)
            y_fit = model_config["model_func"](x_fit, *popt)
            self.plot_widget.set_fit(x_fit, y_fit)
        else:
            self.status_label.setText("Fit failed.")
            QMessageBox.warning(self, "Fit Failed", "The curve fitting procedure failed. Try adjusting the starting parameters or fixing some values.")

    def on_save_fit(self):
        if self.popt is None:
            QMessageBox.warning(self, "No Fit", "There are no fit results to save. Please run a fit first.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Fit Results", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                model_name = self.model_combo.currentText()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Fit Results for {model_name}\n")
                    f.write("-" * 40 + "\n")
                    
                    for name, widgets in self.param_widgets.items():
                        val = widgets["input"].text()
                        err = widgets["err"].text()
                        f.write(f"{name}: {val} {err}\n")
                        
                QMessageBox.information(self, "Success", "Fit results saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save fit results: {e}")

    def on_export(self):
        if self.x_data is None:
            return
        
        # Trigger the built-in pyqtgraph export dialog
        scene = self.plot_widget.scene()
        # Set the contextMenuItem to the PlotItem so the exporter knows what to export
        scene.contextMenuItem = self.plot_widget.getPlotItem()
        scene.showExportDialog()

    def on_toggle_log_x(self, state):
        self.plot_widget.toggle_log_x(state == Qt.CheckState.Checked.value)

    def on_toggle_log_y(self, state):
        self.plot_widget.toggle_log_y(state == Qt.CheckState.Checked.value)

    def on_reset_params(self):
        model_name = self.model_combo.currentText()
        model_config = AVAILABLE_MODELS[model_name]
        default_params = model_config["default_params"]
        
        # Update UI to match defaults
        p0 = []
        param_names = []
        fixed_flags = []
        
        for param_name, default_val in default_params.items():
            if param_name in self.param_widgets:
                widgets = self.param_widgets[param_name]
                widgets["input"].setText(f"{default_val:.6g}")
                widgets["check"].setChecked(False)
                widgets["err"].setText("± --")
                
                p0.append(default_val)
                param_names.append(param_name)
                fixed_flags.append(False)
        
        # Overwrite the saved configuration
        save_model_params(model_name, param_names, p0, fixed_flags)
        
        self.status_label.setText(f"Parameters reset to defaults for {model_name}.")
