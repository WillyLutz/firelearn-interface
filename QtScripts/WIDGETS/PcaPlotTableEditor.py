from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator, QPalette, QColor
from PyQt6.QtWidgets import QTableWidget, QWidget, QSizePolicy, QPushButton, QVBoxLayout, QHeaderView, QComboBox, \
    QGridLayout, QLabel, QSlider, QLineEdit, QCheckBox, QFrame, QColorDialog

from QtScripts import params


class PcaPlotTableEditor(QWidget):
    def __init__(self, parent, combo_items: list[str] = None, ):
        super().__init__(parent)
        self.headers = ["Artist", ]
        self.view = parent
        self.combo_items = combo_items
        
        self.widgets = {}
        
        if not self.combo_items:
            self.combo_items = []
        
        self.table = QTableWidget(0, len(self.headers) + 1)
        self.table.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding))
        
        self.headers.append("")  # Add blank column for Remove buttons
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setColumnWidth(1, 30)
        self.table.resizeColumnsToContents()
        
        add_button = QPushButton("Add element")
        add_button.clicked.connect(self.add_row)
        
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(add_button)
        self.setLayout(layout)
    
    def add_row(self):
        row = self.table.rowCount()
        if row < len(self.combo_items):
            self.table.insertRow(row)
            
            row_layout = QGridLayout()
            target_label = QLabel("Target :", parent=self.view)
            target_cbbox = QComboBox(parent=self.view)
            target_cbbox.addItems([str(x) for x in self.combo_items])
            target_cbbox.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            
            fit_ckbox = QCheckBox(parent=self.view, text="Fit transform")
            fit_ckbox.setChecked(True)
            apply_ckbox = QCheckBox(parent=self.view, text="Apply transform")
            apply_ckbox.setChecked(True)
            
            markerstyle_label = QLabel("Marker style:", parent=self.view)
            markerstyle_cbbox = QComboBox(parent=self.view)
            markerstyle_cbbox.addItems(params.MARKERS)
            
            markersize_label = QLabel("Marker size:", parent=self.view)
            markersize_edit = QLineEdit(parent=self.view)
            markersize_edit.setValidator(QIntValidator())
            markersize_edit.setText(str(params.DEFAULT_MARKERSIZE))
            
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
            
            color_btn.clicked.connect(lambda _, r=row: self.select_color(r))
            
            row_layout.addWidget(target_label, 0, 0)
            row_layout.addWidget(target_cbbox, 0, 1)
            row_layout.addWidget(fit_ckbox, 1, 0)
            row_layout.addWidget(apply_ckbox, 2, 0)
            row_layout.addWidget(markerstyle_label, 3, 0)
            row_layout.addWidget(markerstyle_cbbox, 3, 1)
            row_layout.addWidget(markersize_label, 4, 0)
            row_layout.addWidget(markersize_edit, 4, 1)
            row_layout.addWidget(alpha_label, 5, 0)
            row_layout.addWidget(alpha_slider, 5, 1)
            row_layout.addWidget(color_label, 6, 0)
            row_layout.addWidget(color_btn, 6, 1)
            self.view.widgets[f"pcaplot_row_layout_{row}"] = row_layout
            self.view.widgets[f"pcaplot_target_cbbox_{row}"] = target_cbbox
            self.view.widgets[f"pcaplot_fit_ckbox_{row}"] = fit_ckbox
            self.view.widgets[f"pcaplot_apply_ckbox_{row}"] = apply_ckbox
            self.view.widgets[f"pcaplot_markerstyle_label_{row}"] = markerstyle_label
            self.view.widgets[f"pcaplot_markerstyle_cbbox_{row}"] = markerstyle_cbbox
            self.view.widgets[f"pcaplot_markersize_label_{row}"] = markersize_label
            self.view.widgets[f"pcaplot_markersize_edit_{row}"] = markersize_edit
            self.view.widgets[f"pcaplot_alpha_label_{row}"] = alpha_label
            self.view.widgets[f"pcaplot_alpha_slider_{row}"] = alpha_slider
            self.view.widgets[f"pcaplot_color_label_{row}"] = color_label
            self.view.widgets[f"pcaplot_color_btn_{row}"] = color_btn
            
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
            self.view.widgets[f"pcaplot_remove_btn_{row}"] = remove_btn
            self.table.setCellWidget(row, 1, remove_btn)
            
            self.table.resizeRowToContents(row)
            self.table.resizeColumnToContents(1)
    
    def remove_row(self, row):
        self.table.removeRow(row)
        
        # Step 1: Filter pcaplot-related keys
        pcaplot_keys = [key for key in self.view.widgets if key.startswith("pcaplot_")]
        
        # Step 2: Remove widgets for the deleted row
        keys_to_delete = [key for key in pcaplot_keys if key.endswith(f"_{row}")]
        for key in keys_to_delete:
            del self.view.widgets[key]
        
        # Step 3: Shift widgets for rows after the removed one
        updated_widgets = {}
        for key in pcaplot_keys:
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
            color_btn = self.view.widgets[f"pcaplot_color_btn_{i}"]
            if btn:
                btn.clicked.disconnect()
                btn.clicked.connect(lambda _, r=i: self.remove_row(r))
            if color_btn:
                color_btn.clicked.disconnect()
                color_btn.clicked.connect(lambda _, r=i: self.select_color(r))
    
    def update_combo_items(self, items):
        row_count = self.table.rowCount()
        for i in range(row_count):
            self.remove_row(0)
        
        self.combo_items = items
    
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
            btn = self.view.widgets[f"pcaplot_color_btn_{row}"]
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