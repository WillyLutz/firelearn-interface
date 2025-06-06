from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTableWidget, QWidget, QSizePolicy, QVBoxLayout, QHeaderView, QCheckBox, QAbstractItemView


class SpikeFilterCheckTable(QWidget):
    def __init__(self, parent,items: list[str] = None):
        super().__init__(parent)
        self.headers = ["Values", ]
        self.parent = parent
        self.items = items
        if not self.items:
            self.items = []
        
        self.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding))
        self.table = QTableWidget(0, len(self.headers) )  # +1 for Remove column
        self.table.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding))
        self.table.setHorizontalHeaderLabels(self.headers)
        
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        # self.table.horizontalHeader().setStretchLastSection(False)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.table.resizeColumnsToContents()
    
    def add_row(self):
        row = self.table.rowCount()
        if row < len(self.items):
            self.table.insertRow(row)
            
            # Column 0: Text item
            # self.table.setItem(row, 0, QTableWidgetItem(""))
            # color_btn = QPushButton(parent=self, text="  ")
            # palette = color_btn.palette()
            # palette.setColor(QPalette.ColorRole.Button, QColor("#32ab38"))
            # color_btn.setPalette(palette)
            # color_btn.setAutoFillBackground(True)
            # color_btn.show()
            #
            # color_btn.clicked.connect(lambda _, r=row: self.select_color(r))
            
            # Column 1: ComboBox item
            check = QCheckBox(parent=self, text=str(self.items[row]))
            check.setChecked(True)
            # self.table.setCellWidget(row, 0, color_btn)
            self.table.setCellWidget(row, 0, check)
            
            # Column 2: Remove button
    
    def remove_row(self, row):
        self.table.removeRow(row)
    
    def update_items(self, items):
        row_count = self.table.rowCount()
        for i in range(row_count):
            self.remove_row(0)
        
        self.items = items
        for _ in self.items:
            self.add_row()
        
        self.table.resizeColumnsToContents()
    
    def get_current_values(self):
        current_values = {self.items[i]: False for i in range(len(self.items))}
        
        for r in range(self.table.rowCount()):
            check = self.table.cellWidget(r, 0)
            current_values[self.items[r]] = check.isChecked()
        
        return current_values
    
    # def get_current_colors(self):
    #     current_values = {self.items[i]: '' for i in range(len(self.items))}
    #
    #     for r in range(self.table.rowCount()):
    #         btn = self.table.cellWidget(r, 0)
    #
    #         palette = btn.palette()
    #         bg_color = palette.color(QPalette.ColorRole.Button)
    #         color = bg_color.name()
    #         current_values[self.items[r]] = color
    #
    #     return current_values
    
    def clear(self):
        row_count = self.table.rowCount()
        for i in range(row_count):
            self.remove_row(0)
            
    # def select_color(self, row):
    #     color_dialog = QColorDialog()
    #     color = color_dialog.getCo1lor(parent=self)
    #     if color :
    #         btn = self.table.cellWidget(row, 0)
    #         # btn = self.parent.widgets[f"dataplot_color_btn_{row}"]
    #         # .setStyleSheet("QPushButton{background-color:"+color.name()+";}")
    #         palette = btn.palette()
    #         palette.setColor(QPalette.ColorRole.Button, color)
    #         btn.setPalette(palette)
    #         btn.setAutoFillBackground(True)
    #         btn.show()