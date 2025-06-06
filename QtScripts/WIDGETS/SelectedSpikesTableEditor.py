from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator, QPalette, QColor
from PyQt6.QtWidgets import QTableWidget, QWidget, QSizePolicy, QPushButton, QVBoxLayout, QHeaderView, QComboBox, \
    QGridLayout, QLabel, QSlider, QLineEdit, QFrame, QColorDialog, \
    QAbstractItemView

from QtScripts import params


class SelectedSpikesTableEditor(QWidget):
    def __init__(self, parent, ):
        super().__init__(parent)
        self.headers = ["Selected spikes", ]
        self.view = parent
        
        self.widgets = {}
        
        
        self.table = QTableWidget(0, len(self.headers) + 1)
        self.table.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding))
        self.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding))

        self.headers.append("")  # Add blank column for Remove buttons
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.table.setColumnWidth(1, 30)
        self.table.resizeColumnsToContents()
        
        clear_btn = QPushButton(parent=self, text="Clear table")
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(clear_btn)
        clear_btn.clicked.connect(self.clear)
        self.setLayout(layout)
    
    def set_spike_coord(self,   x, y):
        row = self.table.rowCount() -1
        self.view.widgets[f"spikeplot_coord_label_{row}"].setText(f"Spike coordinates: x={x}, y={y}")
        
    def set_spike_target(self, target):
        row = self.table.rowCount() -1
        self.view.widgets[f"spikeplot_target_label_{row}"].setText(f"Spike target: {target}")
        
    def set_spike_key(self, key):
        row = self.table.rowCount() -1
        self.view.widgets[f"spikeplot_key_label_{row}"].setText(f"{key}")

    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        row_layout = QGridLayout()
        coord_label = QLabel("Spike coordinates: ", parent=self.view)
        target_label = QLabel("Spike target: ", parent=self.view)

        linestyle_label = QLabel("Line style:", parent=self.view)
        linestyle_cbbox = QComboBox(parent=self.view)
        linestyle_cbbox.addItems(params.LINESTYLES)
        
        linewidth_label = QLabel("Line width:", parent=self.view)
        linewidth_edit = QLineEdit(parent=self.view)
        linewidth_edit.setValidator(QIntValidator())
        linewidth_edit.setText(str(params.DEFAULT_LINEWIDTH))
        
        alpha_label = QLabel("Alpha: 100", parent=self.view)
        alpha_slider = QSlider(parent=self.view)
        alpha_slider.setMinimum(0)
        alpha_slider.setMaximum(100)
        alpha_slider.setTickInterval(1)
        alpha_slider.setOrientation(Qt.Orientation.Horizontal)
        alpha_slider.valueChanged.connect(lambda: alpha_label.setText("Alpha: " + str(alpha_slider.value())))
        alpha_slider.setValue(100)
        
        
        color_label = QLabel("Color: ", parent=self.view)
        color_btn = QPushButton(parent=self.view, text="    ")
        palette = color_btn.palette()
        palette.setColor(QPalette.ColorRole.Button, QColor("#32ab38"))
        color_btn.setPalette(palette)
        color_btn.setAutoFillBackground(True)
        color_btn.show()
        
        key_label = QLabel("", parent=self.view)
        key_label_label = QLabel("Key: ", parent=self.view)
        
        color_btn.clicked.connect(lambda _, r=row: self.select_color(r))
        
        row_layout.addWidget(coord_label, 0, 0)
        row_layout.addWidget(target_label, 1, 0)
        row_layout.addWidget(linestyle_label, 2, 0)
        row_layout.addWidget(linestyle_cbbox, 2, 1)
        row_layout.addWidget(linewidth_label, 3, 0)
        row_layout.addWidget(linewidth_edit, 3, 1)
        row_layout.addWidget(alpha_label, 4, 0)
        row_layout.addWidget(alpha_slider, 4, 1)
        row_layout.addWidget(color_label, 5, 0)
        row_layout.addWidget(color_btn, 5, 1)
        row_layout.addWidget(key_label_label, 6, 0)
        row_layout.addWidget(key_label, 6, 1)
        self.view.widgets[f"spikeplot_row_layout_{row}"] = row_layout
        self.view.widgets[f"spikeplot_target_label_{row}"] = target_label
        self.view.widgets[f"spikeplot_coord_label_{row}"] = coord_label
        self.view.widgets[f"spikeplot_linestyle_label_{row}"] = linestyle_label
        self.view.widgets[f"spikeplot_linestyle_cbbox_{row}"] = linestyle_cbbox
        self.view.widgets[f"spikeplot_linewidth_label_{row}"] = linewidth_label
        self.view.widgets[f"spikeplot_linewidth_edit_{row}"] = linewidth_edit
        self.view.widgets[f"spikeplot_alpha_label_{row}"] = alpha_label
        self.view.widgets[f"spikeplot_alpha_slider_{row}"] = alpha_slider
        self.view.widgets[f"spikeplot_color_label_{row}"] = color_label
        self.view.widgets[f"spikeplot_color_btn_{row}"] = color_btn
        self.view.widgets[f"spikeplot_key_label_{row}"] = key_label

        wrapper = QFrame(parent=self.view)
        wrapper.setLayout(row_layout)
        # self.widgets[f"wrapper_{row}"] = wrapper
        self.table.setCellWidget(row, 0, wrapper)
        
        # Column 2: Remove button
        remove_btn = QPushButton("X")
        remove_btn.clicked.connect(lambda _, r=row: self.remove_row(r))
        remove_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        remove_btn.setMaximumWidth(30)
        # remove_btn.setMinimumWidth(15)
        self.view.widgets[f"dataplot_remove_btn_{row}"] = remove_btn
        self.table.setCellWidget(row, 1, remove_btn)
        
        self.table.resizeRowToContents(row)
        self.table.resizeColumnToContents(1)
    
    def remove_row(self, row):
        self.table.removeRow(row)
        
        spike_key_to_del = self.view.widgets[f"spikeplot_key_label_{row}"].text()
        self.view.controller.spike_keys_to_plot.remove(spike_key_to_del)
        print(self.view.controller.spike_keys_to_plot)
        # Step 1: Filter dataplot-related keys
        dataplot_keys = [key for key in self.view.widgets if key.startswith("spikeplot_")]
        
        # Step 2: Remove widgets for the deleted row
        keys_to_delete = [key for key in dataplot_keys if key.endswith(f"_{row}")]
        for key in keys_to_delete:
            del self.view.widgets[key]
        
        # Step 3: Shift widgets for rows after the removed one
        updated_widgets = {}
        for key in dataplot_keys:
            # Try to extract row index
            parts = key.rsplit("_", 1)
            if len(parts) == 2 and parts[1].isdigit():
                key_base, key_row = parts
                key_row = int(key_row)
                if key_row > row:
                    new_key = f"{key_base}_{key_row - 1}"
                    updated_widgets[new_key] = self.view.widgets[key]
        
        # Step 4: Delete old keys that were shifted
        for key in updated_widgets.values():
            for k in list(self.view.widgets.keys()):
                if self.view.widgets.get(k) == key:
                    del self.view.widgets[k]
                    break
        
        # Step 5: Add updated keys
        self.view.widgets.update(updated_widgets)
        
        # reassign remove button connection
        for i in range(self.table.rowCount()):
            btn = self.table.cellWidget(i, len(self.headers) - 1)
            color_btn = self.view.widgets[f"spikeplot_color_btn_{i}"]
            if btn:
                btn.clicked.disconnect()
                btn.clicked.connect(lambda _, r=i: self.remove_row(r))
            if color_btn:
                color_btn.clicked.disconnect()
                color_btn.clicked.connect(lambda _, r=i: self.select_color(r))
    
    
    def get_current_values(self):
        current_values = {self.headers[k]: [] for k in range(len(self.headers) - 1)}
        
        for k in range(len(self.headers) - 1):
            for i in range(self.table.rowCount()):
                combo = self.table.cellWidget(i, k)
                current_values[self.headers[k]].append(combo.currentText())
        
        return current_values
    
    def select_color(self, row):
        color_dialog = QColorDialog()
        color = color_dialog.getColor(parent=self.view)
        if color:
            btn = self.view.widgets[f"spikeplot_color_btn_{row}"]
            # .setStyleSheet("QPushButton{background-color:"+color.name()+";}")
            palette = btn.palette()
            palette.setColor(QPalette.ColorRole.Button, color)
            btn.setPalette(palette)
            btn.setAutoFillBackground(True)
            btn.show()
    
    def clear(self):
        row_count = self.table.rowCount()
        for i in range(row_count):
            self.remove_row(0)