from PyQt6.QtWidgets import (
    QWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QVBoxLayout, QHeaderView, QSizePolicy
)


class TableEditor(QWidget):
    def __init__(self, parent, headers: list[str]):
        super().__init__(parent=parent, )
        self.headers = headers
        self.table = QTableWidget(0, len(self.headers)+1)  # 3 columns: Key, Value, Action
        self.table.setMinimumWidth(50)
        self.table.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding))
        headers.append("")  # add the columns with the remove button
        self.table.setHorizontalHeaderLabels(self.headers)  # Leave action column blank
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        add_button = QPushButton("Add element")
        add_button.clicked.connect(self.add_row)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(add_button)
        self.setLayout(layout)

    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)

        for col in range(len(self.headers)-1):
            self.table.setItem(row, col, QTableWidgetItem(""))

        # Add Remove button
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(lambda _, r=row: self.remove_row(r))
        self.table.setCellWidget(row, len(self.headers)-1, remove_btn)

    def remove_row(self, row):
        self.table.removeRow(row)
        # Optional: reassign buttons to correct row index after removal
        for i in range(self.table.rowCount()):
            btn = self.table.cellWidget(i, len(self.headers)-1)
            if btn:
                btn.clicked.disconnect()
                btn.clicked.connect(lambda _, r=i: self.remove_row(r))
                
                
