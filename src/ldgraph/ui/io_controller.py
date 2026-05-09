import os
import numpy as np
from PyQt6.QtWidgets import QFileDialog

class IOController:
    def __init__(self, parent=None):
        self.parent = parent

    def load_data(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent, "Open Data File", "", "Data Files (*.txt *.csv *.tsv);;All Files (*)"
        )
        if not file_path:
            return None, None, None, None, None

        return self.load_data_from_file(file_path)
        
    def load_data_from_file(self, file_path):
        x_label = None
        y_label = None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Filter out empty lines and explicit comments
            data_lines = [line.strip() for line in lines if line.strip() and not line.startswith('#')]

            if not data_lines:
                return None, None, None, None, "File is empty or contains only comments."

            # Determine delimiter based on extension or first line content
            delimiter = ',' if file_path.lower().endswith('.csv') else None
            
            first_line = data_lines[0]
            parts = first_line.split(delimiter) if delimiter else first_line.split()

            # Check if the first line is text (headers)
            has_header = False
            try:
                # If we can cast the parts to float, it's numeric data, not a header
                [float(p) for p in parts]
            except ValueError:
                has_header = True
                if len(parts) >= 2:
                    x_label = parts[0].strip()
                    y_label = parts[1].strip()

            skiprows = 1 if has_header else 0

            # Load the data using np.loadtxt
            # We pass the filtered lines to avoid np.loadtxt tripping on scattered text
            data = np.loadtxt(data_lines[skiprows:], delimiter=delimiter)

            if data.ndim != 2 or data.shape[1] < 2:
                return None, None, None, None, "File must contain at least two numeric columns."

            return data[:, 0], data[:, 1], x_label, y_label, None

        except Exception as e:
            return None, None, None, None, str(e)
