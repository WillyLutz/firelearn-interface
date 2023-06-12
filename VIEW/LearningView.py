import tkinter as tk

import customtkinter
import customtkinter as ctk
from tkinter import ttk, messagebox

import fiiireflyyy.firelearn
import pandastable
import sklearn.ensemble
from PIL import ImageTk, Image
from functools import partial
from pandastable import Table, TableModel
import pandas as pd
import data.params as p
import tkterminal
from tkterminal import Terminal
import VIEW.graphic_params as gp
from sklearn.ensemble import RandomForestClassifier
from VIEW.CustomTable import CustomTable


class LearningView(ctk.CTkFrame):
    def __init__(self, app, master, controller):
        super().__init__(master=app)
        self.master = master
        self.controller = controller

        self.subtabs = ctk.CTkTabview(master=self.master, corner_radius=10)
        self.subtabs.place(relwidth=1.0, relheight=1.0)
        self.subtabs.add("RFC")

        self.manage_tab()

    def set_controller(self, controller):
        self.controller = controller

    def manage_tab(self):
        # todo : managing learning tab
        entries = {}
        buttons = {}
        cboxes = {}
        strvars = {}
        rfc_params_stringvar = {}
        textboxes = {}

        params_frame = ctk.CTkFrame(master=self.subtabs.tab("RFC"))
        params_frame.place(relx=0, rely=0, relwidth=0.30, relheight=1)
        manage_dataset_frame = ctk.CTkFrame(master=self.subtabs.tab("RFC"))
        manage_dataset_frame.place(relx=0.33, rely=0, relwidth=0.30, relheight=0.85)
        loading_frame = ctk.CTkFrame(master=self.subtabs.tab("RFC"))
        loading_frame.place(relx=0.33, rely=0.9, relwidth=0.63, relheight=0.1)
        classifier_frame = ctk.CTkFrame(master=self.subtabs.tab("RFC"))
        classifier_frame.place(relx=0.66, rely=0, relwidth=0.3, relheight=0.85)

        # ----------- PARAMETERS -----------------
        params_label = ctk.CTkLabel(master=params_frame, text="Classifier parameters")
        params_sframe = ctk.CTkScrollableFrame(master=params_frame, corner_radius=10)
        params_label.place(relx=0, rely=0)
        reload_button = ctk.CTkButton(master=params_frame, text="Reload default")
        reload_button.place(relx=0.5, rely=0)
        buttons["reload"] = reload_button

        params_sframe.place(relx=0.025, rely=0.1, relheight=0.85, relwidth=0.95)
        params_sframe.grid_columnconfigure(0, weight=1)
        params_sframe.grid_columnconfigure(1, weight=2)

        sub_paramsframe = ctk.CTkFrame(master=params_sframe, )
        sub_paramsframe.place(relx=0, rely=0, relheight=1, relwidth=1)
        sub_paramsframe.grid(row=0, column=0, sticky=ctk.NSEW)

        clf = RandomForestClassifier()

        n_param = 0
        for name, value in clf.get_params().items():
            param_label = ctk.CTkLabel(master=sub_paramsframe, text=name, justify='left')
            param_label.grid(row=n_param, column=0, pady=10, padx=0)

            param_stringvar = tk.StringVar()
            param_stringvar.set(value)
            param_entry = ctk.CTkEntry(master=sub_paramsframe, state="normal", textvariable=param_stringvar, width=100)
            param_entry.grid(row=n_param, column=1, pady=10, padx=10)
            n_param += 1
            rfc_params_stringvar[name] = param_stringvar
            entries[f"params {param_stringvar.get()}"] = param_entry

        # ------------ MANAGE DATASET ------------------
        load_dataset_button = ctk.CTkButton(master=manage_dataset_frame, text="Load dataset")
        load_dataset_button.place(relx=0, rely=0)
        buttons["load dataset"] = load_dataset_button

        load_dataset_strvar = tk.StringVar()
        load_dataset_entry = ctk.CTkEntry(master=manage_dataset_frame, state='normal', textvariable=load_dataset_strvar)
        load_dataset_entry.place(relx=0, rely=0.06, relwidth=0.8)
        entries["load dataset"] = load_dataset_entry
        strvars["load dataset"] = load_dataset_strvar

        label_column_label = ctk.CTkLabel(master=manage_dataset_frame, text="Select targets column")
        label_column_label.place(relx=0, rely=0.15)

        label_column_cbox = tk.ttk.Combobox(master=manage_dataset_frame, state='disabled', values=["None", ])
        label_column_cbox.set("None")
        label_column_cbox.place(relx=0, rely=0.2, relwidth=0.8)
        cboxes["target column"] = label_column_cbox

        save_files_label = ctk.CTkLabel(master=manage_dataset_frame, text="Save Classifier under:",
                                        text_color=gp.enabled_label_color)
        save_files_label.place(relx=0, rely=0.8)
        save_rfc_strvar = ctk.StringVar()
        save_entry = ctk.CTkEntry(master=manage_dataset_frame, textvariable=save_rfc_strvar)
        save_entry.place(relx=0, rely=0.85, relwidth=0.7)
        entries["save rfc"] = save_entry
        strvars["save rfc"] = save_rfc_strvar

        save_rfc_button = ctk.CTkButton(master=manage_dataset_frame, text="Open")
        save_rfc_button.place(relx=0.8, rely=0.85, relwidth=0.15)
        buttons["save rfc"] = save_rfc_button

        # ----------- DISPLAY CLASSIFIER -----------------

        rfc_path_sv = tk.StringVar()
        rfc_path_sv.set("Classifier path:")
        strvars["rfc path"] = rfc_path_sv
        rfc_path_label = ctk.CTkLabel(master=classifier_frame, textvariable=rfc_path_sv)
        rfc_path_label.place(relx=0, rely=0)

        rfc_name_sv = tk.StringVar()
        rfc_name_sv.set("Classifier name:")
        strvars["rfc name"] = rfc_name_sv
        rfc_name_label = ctk.CTkLabel(master=classifier_frame, textvariable=rfc_name_sv)
        rfc_name_label.place(relx=0, rely=0.1)

        rfc_status_sv = tk.StringVar()
        rfc_status_sv.set("Trained:")
        strvars["rfc status"] = rfc_status_sv
        rfc_status_label = ctk.CTkLabel(master=classifier_frame, textvariable=rfc_status_sv)
        rfc_status_label.place(relx=0, rely=0.2)

        rfc_train_sv = tk.StringVar()
        rfc_train_sv.set("Train score:")
        strvars["rfc train"] = rfc_train_sv
        rfc_train_label = ctk.CTkLabel(master=classifier_frame, textvariable=rfc_train_sv)
        rfc_train_label.place(relx=0, rely=0.3)

        rfc_test_sv = tk.StringVar()
        rfc_test_sv.set("Test score:")
        strvars["rfc test"] = rfc_test_sv
        rfc_test_label = ctk.CTkLabel(master=classifier_frame, textvariable=rfc_test_sv)
        rfc_test_label.place(relx=0, rely=0.4)

        # ----------- LOADING FRAME -------------------
        load_params_button = ctk.CTkButton(master=loading_frame, text="Load configuration")
        load_params_button.place(anchor=tk.CENTER, relx=0.25, rely=0.5)
        buttons["load config"] = load_params_button

        load_clf_button = ctk.CTkButton(master=loading_frame, text="Load classifier")
        load_clf_button.place(anchor=tk.CENTER, relx=0.5, rely=0.5)
        buttons["load rfc"] = load_clf_button

        learning_button = ctk.CTkButton(master=loading_frame, text="Learning", fg_color="green")
        learning_button.place(anchor=tk.CENTER, relx=0.75, rely=0.5)
        buttons["learning"] = learning_button

        # ------------ CONFIGURE COMMANDS ---------------

        reload_button.configure(command=partial(self.reload_rfc_params, rfc_params_stringvar))
        # todo : command configure load dataset
        load_dataset_button.configure(command=partial(self.load_dataset, strvars["load dataset"],
                                                      label_column_cbox))
        # todo : command configure open clf
        save_rfc_button.configure(command=partial(self.savepath_rfc, strvars["save rfc"]))
        load_clf_button.configure(command=partial(self.load_rfc, rfc_params_stringvar, strvars))
        # todo : command configure load config / save config
        # todo : command configure  learning
        learning_button.configure(command=partial(self.learning, entries, cboxes, rfc_params_stringvar,
                                                  strvars))

    def learning(self, entries, cboxes, rfc_params_string_var, strvars):
        if self.controller:
            self.controller.learning(entries, cboxes, rfc_params_string_var, strvars)

    def savepath_rfc(self, strvar):
        if self.controller:
            self.controller.savepath_rfc(strvar)

    def load_rfc(self, rfc_params_string_var, strvars):
        if self.controller:
            self.controller.load_rfc(rfc_params_string_var, strvars)

    def reload_rfc_params(self, rfc_params_string_var):
        if self.controller:
            self.controller.reload_rfc_params(rfc_params_string_var)

    def load_dataset(self, strvar, label_cbox):
        if self.controller:
            self.controller.load_dataset(strvar, label_cbox)
