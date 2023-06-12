import os
import pickle

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from VIEW.MainView import MainView
from MODEL.LearningModel import LearningModel
import customtkinter as ctk
from CONTROLLER import input_validation as ival
import tkinter as tk
from tkinter import ttk


class LearningController:
    def __init__(self, main_controller, model: LearningModel, view: MainView, ):
        self.model = model
        self.view = view
        self.main_controller = main_controller

    @staticmethod
    def reload_rfc_params(rfc_params_string_var):
        clf = RandomForestClassifier()
        for name, value in clf.get_params().items():
            rfc_params_string_var[name].set(value)

    def load_dataset(self, strvar, label_cbox):
        filename = self.main_controller.open_filedialog(mode='file')
        if filename:
            strvar.set(filename)
            self.model.dataset_path = filename

            df = pd.read_csv(filename, index_col=False)
            label_cbox.configure(state='normal')
            label_cbox.configure(values=[str(c) for c in df.columns])
            label_cbox.set(str(df.columns[0]))
            label_cbox.configure(state='readonly')

    def savepath_rfc(self, strvar):
        filename = self.main_controller.open_filedialog(mode='saveas')
        if filename:
            strvar.set(filename)
            self.model.save_rfc_directory = filename

    def load_rfc(self, rfc_params_string_var, strvars):
        filename = self.main_controller.open_filedialog(mode="aimodel")
        if filename:
            clf = pickle.load(open(filename, "rb"))
            self.model.rfc = clf

            for name, value in clf.get_params().items():
                rfc_params_string_var[name].set(value)

            strvars["rfc path"].set("Classifier path: " + os.path.dirname(filename))
            strvars["rfc name"].set("Classifier name: " + os.path.basename(filename))
            strvars["rfc status"].set("Trained: True")
            strvars["rfc train"].set("Train score:")
            strvars["rfc test"].set("Test score:")

    def learning(self, entries, cboxes, rfc_params_string_var, strvars):
        if self.check_params_validity(entries, cboxes):
            self.update_params(entries)
            self.update_params(cboxes)
            local_cboxes = self.model.cboxes_params

            rfc_params = {}
            for key, widget in rfc_params_string_var.items():
                if ival.isint(widget.get()):
                    rfc_params[key] = int(widget.get())
                elif ival.isfloat(widget.get()):
                    rfc_params[key] = float(widget.get())
                elif widget.get() == 'None':
                    rfc_params[key] = None
                else:
                    rfc_params[key] = widget.get()

            df = pd.read_csv(self.model.dataset_path, index_col=False)
            target_column = local_cboxes["target column"]
            y = df[target_column]
            y = self.label_encoding(y)
            X = df.loc[:, df.columns != target_column]

            if self.model.rfc:  # no training needed
                rfc = self.model.rfc
                test_size = 1
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size)

                strvars["rfc train"].set(f"Train score: {round(rfc.score(X_train, y_train), 3)}")
                strvars["rfc test"].set(f"Test score: {round(rfc.score(X_test, y_test), 3)}")
                # todo : display metrics in label + export

            else:
                rfc = RandomForestClassifier()
                rfc.set_params(**rfc_params)
                test_size = 0.3
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size)
                rfc.fit(X_train, y_train)
                strvars["rfc train"].set(f"Train score: {round(rfc.score(X_train, y_train), 3)}")
                strvars["rfc test"].set(f"Test score: {round(rfc.score(X_test, y_test), 3)}")
                # todo : display metrics in label + export

            # todo : use progressbar
            if entries["save rfc"].get():
                self.main_controller.save_object(rfc, entries["save rfc"].get())

        pass

    @staticmethod
    def label_encoding(y):
        labels = list(set(list(y)))
        corr = {}
        for l in range(len(labels)):
            corr[labels[l]] = l

        for key, value in corr.items():
            y.replace(key, value)

        return y

    def check_params_validity(self, entries, cboxes):
        # todo : check validity
        return True

    def update_params(self, widgets: dict, ):
        local_dict = {}
        for key, value in widgets.items():
            local_dict[key] = value.get()
        if type(list(widgets.values())[0]) == ctk.CTkSwitch:
            self.model.switches_params.update(local_dict)
        if type(list(widgets.values())[0]) == ctk.CTkEntry:
            self.model.entries_params.update(local_dict)
        if type(list(widgets.values())[0]) == tk.ttk.Combobox:
            self.model.cboxes_params.update(local_dict)
