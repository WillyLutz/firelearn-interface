from PyQt6.QtWidgets import QTableWidget, QWidget, QSizePolicy, QPushButton, QVBoxLayout, QHeaderView, QComboBox


class ComboTableEditor(QWidget):
    def __init__(self, parent, headers: list[str], combo_items: list[str]= None):
        super().__init__(parent)
        self.headers = headers
        self.combo_items = combo_items
        if not self.combo_items:
            self.combo_items = []
        
        self.table = QTableWidget(0, len(self.headers) + 1)  # +1 for Remove column
        self.table.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding))
        headers.append("")  # Add blank column for Remove buttons
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
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
            
            # Column 0: Text item
            # self.table.setItem(row, 0, QTableWidgetItem(""))
            
            # Column 1: ComboBox item
            combo = QComboBox()
            combo.addItems([str(x) for x in self.combo_items])
            self.table.setCellWidget(row, 0, combo)
            
            # Column 2: Remove button
            remove_btn = QPushButton("Remove")
            remove_btn.clicked.connect(lambda _, r=row: self.remove_row(r))
            self.table.setCellWidget(row, 1, remove_btn)
    
    def remove_row(self, row):
        self.table.removeRow(row)
        for i in range(self.table.rowCount()):
            btn = self.table.cellWidget(i, len(self.headers) - 1)
            if btn:
                btn.clicked.disconnect()
                btn.clicked.connect(lambda _, r=i: self.remove_row(r))
                
    def update_combo_items(self, items):
        row_count = self.table.rowCount()
        for i in range(row_count):
            self.remove_row(0)
            
        self.combo_items = items

    def get_current_values(self):
        current_values = {self.headers[k]: [] for k in range(len(self.headers)-1)}
        
        for k in range(len(self.headers)-1):
            for i in range(self.table.rowCount()):
                combo = self.table.cellWidget(i, k)
                current_values[self.headers[k]].append(combo.currentText())
                
        return current_values