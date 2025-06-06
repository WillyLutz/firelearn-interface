from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTableWidget, QWidget, QSizePolicy, QVBoxLayout, QHeaderView, QComboBox, QCheckBox


class ConfusionTargetTableEditor(QWidget):
    def __init__(self, parent, targets: list[str] = None, set_: str = None):
        super().__init__(parent)
        self.view = parent
        self.targets = targets
        self.widgets = {}
        self.set = set_
        if self.set not in ["train", "test"]:
            raise ValueError("set must be 'train' or 'test'")
        self.headers = ["Training class", "Index" ] if self.set == "train" else ["Testing target", "Index"]
        
        
        if not self.targets:
            self.targets = []
        
        self.table = QTableWidget(0, len(self.headers))
        self.table.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding))
        
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        # self.table.resizeColumnsToContents()
        
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)
        
        for _ in self.targets:
            self.add_row()
    
    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        ckbox = QCheckBox(str(self.targets[row]), parent=self.view)
        ckbox.setChecked(True)
        if self.set == "test":
            ckbox.setEnabled(True)
        else:
            ckbox.setEnabled(False)
            
        cbbox = QComboBox(parent=self.view)
        cbbox.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        cbbox.addItems([str(x) for x in range(len(self.targets))])
        cbbox.setCurrentText(str(row))
        
        
        self.view.widgets[f"confusion_table_{self.set}_ckbox_{row}"] = ckbox
        self.view.widgets[f"confusion_table_{self.set}_cbbox_{row}"] = cbbox
        self.table.setCellWidget(row, 0, ckbox)
        self.table.setCellWidget(row, 1, cbbox)

        self.table.resizeRowToContents(row)
        # self.table.resizeColumnsToContents()
        
    
    def remove_row(self, row):
        self.table.removeRow(row)
        
        # Step 1: Filter related keys
        conftable_keys = [key for key in self.view.widgets if key.startswith(f"confusion_table_{self.set}")]
        
        # Step 2: Remove widgets for the deleted row
        keys_to_delete = [key for key in conftable_keys if key.endswith(f"_{row}")]
        for key in keys_to_delete:
            del self.view.widgets[key]
        
        # Step 3: Shift widgets for rows after the removed one
        updated_widgets = {}
        for key in conftable_keys:
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
        
    
    def update_combo_items(self, items):
        row_count = self.table.rowCount()
        for i in range(row_count):
            self.remove_row(0)
        
        self.targets = items
        for _ in self.targets:
            self.add_row()
    
    def get_current_values(self):
        current_values = {self.headers[k]: [] for k in range(len(self.headers) - 1)}
        
        for k in range(len(self.headers) - 1):
            for i in range(self.table.rowCount()):
                combo = self.table.cellWidget(i, k)
                current_values[self.headers[k]].append(combo.currentText())
        
        return current_values
    
    
    def clear(self):
        row_count = self.table.rowCount()
        for i in range(row_count):
            self.remove_row(0)