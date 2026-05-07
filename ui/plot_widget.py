import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout
import numpy as np

class PowerOfTenAxis(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        if self.logMode:
            # Generate the default strings
            default_strings = super().tickStrings(values, scale, spacing)
            # Filter out non-integer labels so only powers of 10 are drawn
            return [s if float(v).is_integer() else "" for v, s in zip(values, default_strings)]
        return super().tickStrings(values, scale, spacing)

class PlotWidget(pg.PlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent, axisItems={'bottom': PowerOfTenAxis(orientation='bottom'), 'left': PowerOfTenAxis(orientation='left')})
        self.setBackground('w')
        self.showGrid(x=True, y=True, alpha=0.3)
        
        self.base_x_label = 'Ligand concentration'
        self.base_y_label = 'Observed signal'
        
        self.setLabel('left', self.base_y_label)
        self.setLabel('bottom', self.base_x_label)
        
        # Use PlotDataItem because it handles setLogMode automatically
        self.scatter = pg.PlotDataItem(pen=None, symbol='o', symbolSize=10, symbolPen='k', symbolBrush='b')
        self.plot_curve = pg.PlotDataItem(pen=pg.mkPen('r', width=2))
        
        self.addItem(self.scatter)
        self.addItem(self.plot_curve)
        
        self.log_mode_x = False
        self.log_mode_y = False

    def set_labels(self, x_label, y_label):
        if x_label:
            self.base_x_label = x_label
        if y_label:
            self.base_y_label = y_label
            
        self._update_x_label()
        self._update_y_label()

    def _update_x_label(self):
        if self.log_mode_x:
            self.setLabel('bottom', f"{self.base_x_label} (log scale)")
        else:
            self.setLabel('bottom', self.base_x_label)

    def _update_y_label(self):
        if self.log_mode_y:
            self.setLabel('left', f"{self.base_y_label} (log scale)")
        else:
            self.setLabel('left', self.base_y_label)

    def set_data(self, x, y):
        self.scatter.setData(x, y)

    def set_fit(self, x_fit, y_fit):
        self.plot_curve.setData(x_fit, y_fit)

    def toggle_log_x(self, checked):
        self.log_mode_x = checked
        self.setLogMode(x=self.log_mode_x, y=self.log_mode_y)
        self._update_x_label()
        self.getViewBox().autoRange()

    def toggle_log_y(self, checked):
        self.log_mode_y = checked
        self.setLogMode(x=self.log_mode_x, y=self.log_mode_y)
        self._update_y_label()
        self.getViewBox().autoRange()
