import tkinter as tk
from tkinter import filedialog as fd
from VIEW.MainView import MainView
import pandas as pd
from pandastable import Table, TableModel


class Controller:
    def __init__(self, model, view: MainView):
        self.view = view
        self.model = model

    def print_pressed(self):
        if self.model.pressed():
            print("pressed")

    def load_dataset(self):
        filetypes = (
            ('csv files', '*.csv'),
            ('excel files', '*.xlsx'),
            ('text files', '*.txt')
        )

        f = fd.askopenfile(filetypes=filetypes)
        self.model.set_loaded_dataset(f.name)
        path = self.model.get_loaded_dataset()
        self.view.dataset_label_text.set(path)

        if path.split(".")[-1] == "csv":
            df = pd.read_csv(path, sep=",")

            self.view.datatable.updateModel(TableModel(df))
            self.redraw_dataframe()
        if path.split(".")[-1] == "xlsx":
            df = pd.read_excel(path, engine='openpyxl')

            self.view.datatable.updateModel(TableModel(df))
            self.redraw_dataframe()
            # todo: put df in datatable in view

    def redraw_dataframe(self):
        self.view.datatable.redraw()
