from typing import Any

from PyQt6.QtWidgets import QApplication, QLineEdit, QCheckBox, QComboBox, QSpinBox, QSlider, QFileDialog, \
    QTableWidgetItem, QLabel
from QtScripts.CONTROLLER.AnalysisController import AnalysisController
from QtScripts.CONTROLLER.LearningController import LearningController
from QtScripts.CONTROLLER.ProcessingController import ProcessingController
from QtScripts.MODEL.MainModel import MainModel
from QtScripts.VIEW.MainView import MainView
from QtScripts.WIDGETS.ComboTableEditor import ComboTableEditor
from QtScripts.WIDGETS.TableEditor import TableEditor


class MainController:
    def __init__(self, app: QApplication):
        self.app = app
        self.view = MainView(self.app, self)
        self.model = MainModel(self)  # set model
        self.view.controller = self  # set controller to view
        
        self.processing_controller = ProcessingController(self.app, parent_controller=self)
        self.learning_controller = LearningController(self.app, parent_controller=self)
        self.analysis_controller = AnalysisController(self.app, parent_controller=self)
    
    def load_processing_config(self):
        self.processing_controller.dataset_controller.load_model()
            
    def save_processing_config(self):
        self.processing_controller.dataset_controller.save_model()
    
    def load_spike_config(self):
        self.processing_controller.spike_controller.load_model()
    
    def save_spike_config(self):
        self.processing_controller.spike_controller.save_model()
        
    def load_rfc_config(self):
        self.learning_controller.rfc_controller.load_model()

    def save_rfc_config(self):
        self.learning_controller.rfc_controller.save_model()
        
    def load_svc_config(self):
        self.learning_controller.svc_controller.load_model()

    def save_svc_config(self):
        self.learning_controller.svc_controller.save_model()
        
    @staticmethod
    def extract_table_data(table_editor) -> list[list[str]]:
        table = table_editor.table
        rows: list[list[str]] = []
        n_cols = table.columnCount() - 1  # skip last “remove” column

        for row in range(table.rowCount()):
            row_data: list[str] = []
            for col in range(n_cols):
                widget = table.cellWidget(row, col)
                if isinstance(widget, QComboBox):
                    row_data.append(widget.currentText())
                else:
                    item = table.item(row, col)
                    row_data.append(item.text() if item else "")
            rows.append(row_data)

        return rows
    
    def extract_widget_value(self, widget: Any) -> Any:
        if isinstance(widget, QLineEdit):
            return widget.text()
        elif isinstance(widget, QLabel):
            return widget.text()
        elif isinstance(widget, QCheckBox):
            return widget.isChecked()
        elif isinstance(widget, QComboBox):
            return widget.currentText()
        elif isinstance(widget, QSpinBox):
            return widget.value()
        elif isinstance(widget, QSlider):
            return widget.value()
        elif isinstance(widget, TableEditor):
            return self.extract_table_data(widget)
        elif isinstance(widget, ComboTableEditor):
            return self.extract_table_data(widget)
        return None
    
    def update_model_from_view(self, model, view):
        for name, widget in view.widgets.items():
            model.widgets_values[name] = self.extract_widget_value(widget)
        if hasattr(model, 'update_tableEditors'):
            model.update_tableEditors()
        if hasattr(model, 'update_comboTableEditors'):
            model.update_comboTableEditors()
    
    def update_view_from_model(self, view, model):
        for name, widget in view.widgets.items():
            value = model.widgets_values.get(name)
            if value is not None:
                self.set_widget_value(widget, value)
    
    def set_widget_value(self, widget: Any, value: Any) -> None:
        if isinstance(widget, QLineEdit):
            widget.setText(str(value))
        elif isinstance(widget, QCheckBox):
            widget.setChecked(bool(value))
        elif isinstance(widget, QComboBox):
            index = widget.findText(str(value))
            if index != -1:
                widget.setCurrentIndex(index)
        elif isinstance(widget, QSpinBox):
            widget.setValue(int(value))
        elif isinstance(widget, QSlider):
            widget.setValue(int(value))
        elif isinstance(widget, TableEditor):
            self.set_table_data(widget, value)
        elif isinstance(widget, ComboTableEditor):
            self.set_table_data(widget, value)
    
    @staticmethod
    def set_table_data(table_editor, data: list[list[str]]) -> None:
        table = table_editor.table
        # 1) remove all rows
        while table.rowCount() > 0:
            table_editor.remove_row(0)
        
        # 2) add as many blank rows as needed
        for _ in data:
            table_editor.add_row()
        
        # 3) fill in each cell
        n_cols = table.columnCount() - 1
        for r, row_data in enumerate(data):
            for c in range(min(n_cols, len(row_data))):
                widget = table.cellWidget(r, c)
                if isinstance(widget, QComboBox):
                    val = row_data[c]
                    # attempt to set to that text
                    idx = widget.findText(val)
                    if idx >= 0:
                        widget.setCurrentIndex(idx)
                    else:
                        # if it isn’t in the existing items, you could:
                        #   widget.addItem(val)
                        #   widget.setCurrentText(val)
                        widget.setCurrentText(val)
                else:
                    # plain text column
                    item = QTableWidgetItem(row_data[c])
                    table.setItem(r, c, item)
    
    
    @staticmethod
    def generate_harmonics(freq, nth, mode):
        harmonics = []
        step = freq
        if mode == 'All':
            for i in range(nth):
                harmonics.append(freq)
                freq = freq + step
        if mode == "Even":
            for i in range(nth):
                if i % 2 == 0:
                    harmonics.append(freq)
                    freq = freq + step
        if mode == "Odd":
            for i in range(nth):
                if i % 2 == 1:
                    harmonics.append(freq)
                    freq = freq + step
        return harmonics
        
    def load_path_and_update_edit(self, line_edit: QLineEdit, mode:'' , filter_="Dataset (*.csv *.xlsx)", directory='',
                                  extension=""):
        dialog = ""
        match mode:
            case 'getOpenFileName':
                dialog = \
                    QFileDialog().getOpenFileName(parent=self.view, caption="Open file", filter=filter_)[0]
            
            case 'getSaveFileName':
                dialog = QFileDialog.getSaveFileName(parent=self.view, caption="Save file as", directory=directory)[0]
                if extension:
                    if extension not in dialog:
                        dialog += extension
        
        if dialog:
            line_edit.setText(dialog)
            
        return dialog
    
    @staticmethod
    def has_unique_second_elements(dct):
        second_elements = {v for k, v in dct.items()}  # Extract all second elements into a set
        return len(second_elements) == len(dct.values())