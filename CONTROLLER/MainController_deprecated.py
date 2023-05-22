import tkinter as tk
from tkinter import filedialog as fd, messagebox

import pandastable

from VIEW.MainView_deprecated import MainView
import pandas as pd
from pandastable import Table, TableModel
import data.params as p
import io


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
        )

        f = fd.askopenfile(filetypes=filetypes)

        self.model.set_loaded_dataset_path(f.name)
        path = self.model.get_loaded_dataset_path()
        df = pd.read_csv(path, sep=",")

        self.view.dataset_label_text.set(path)
        self.model.set_loaded_dataset(df)
        self.update_dataframe(df)

        self.update_target_box()

    def update_dataframe(self, df):
        buf = io.StringIO()
        df.info(buf=buf)
        lines = buf.getvalue().split("\n")
        infos = ''
        null_values = f'Null Count: {str(df.isna().sum().sum())} out of {str(len(df.index) * len(df.columns))}' \
                      f' ({df.isna().sum().sum() * (len(df.index) * len(df.columns)) / 100}%)'
        lines_to_consider = [1, 2, -2]
        for ltc in lines_to_consider:
            infos = infos + lines[ltc] + "\n"
        infos += null_values
        self.view.dataset_info.set(infos)

        self.model.set_loaded_dataset(df)
        self.view.datatable.updateModel(TableModel(df))
        self.view.datatable.redraw()

    def reset_loaded_dataset(self):
        # self.view.datatable.updateModel(TableModel(df))
        self.view.datatable.clearTable()
        self.model.set_loaded_dataset_path(p.default_dataset_path)
        self.view.dataset_label_text.set(self.model.get_loaded_dataset_path())
        self.model.set_loaded_dataset(pd.DataFrame)
        self.update_dataframe(pd.DataFrame())
        self.view.dataset_info.set("")

    def delete_dataframe_rows(self):
        cols_idx = self.view.datatable.getSelectedColumn()
        rows_idx = self.view.datatable.getSelectedRow()
        df = self.model.get_loaded_dataset()
        ask = True
        n = True
        if ask:
            n = messagebox.askyesno("Delete",
                                    "Delete Row(s)?")
        if n:
            df.drop([rows_idx, ], axis=0, inplace=True)

            self.update_dataframe(df)

    def delete_dataframe_columns(self):
        cols_idx = self.view.datatable.getSelectedColumn()
        rows_idx = self.view.datatable.getSelectedRow()
        df = self.model.get_loaded_dataset()
        ask = True
        n = True
        if ask:
            n = messagebox.askyesno("Delete",
                                    "Delete Column(s)?")
        if n:
            df.drop(columns=[df.columns[rows_idx], ], axis=1, inplace=True)

            self.update_dataframe(df)

    def select_target(self):
        selected_target = self.view.target_box.current()
        self.model.set_selected_target(selected_target)
        loaded_dataset = self.model.get_loaded_dataset_path()
        if loaded_dataset != p.default_dataset_path:
            df = self.model.get_loaded_dataset()
            self.view.current_target.set(df.columns[selected_target])

    def update_target_box(self):
        loaded_dataset = self.model.get_loaded_dataset_path()
        if loaded_dataset != p.default_dataset_path:
            df = self.model.get_loaded_dataset()
            self.view.target_box.configure(values=df.columns.tolist())
