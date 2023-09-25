import tkinter as tk
from functools import partial
from tkinter import ttk

import customtkinter as ctk
from sklearn.ensemble import RandomForestClassifier

import VIEW.graphic_params as gp
from CONTROLLER.LearningController import LearningController
from WIDGETS.ErrEntry import ErrEntry
from WIDGETS.Helper import Helper


class LearningView(ctk.CTkFrame):
    def __init__(self, app, master, parent_view):
        super().__init__(master=app)
        self.master = master
        self.app = app
        self.parent_view = parent_view
        self.controller = LearningController(self, )

        self.entries = {}
        self.buttons = {}
        self.cbboxes = {}
        self.vars = {}
        self.switches = {}
        self.checkboxes = {}
        self.rfc_params_stringvar = {}
        self.textboxes = {}

        self.subtabs = ctk.CTkTabview(master=self.master, corner_radius=10)
        self.subtabs.place(relwidth=1.0, relheight=1.0)
        self.subtabs.add("RFC")

        self.manage_tab()

    def set_controller(self, controller):
        self.controller = controller

    def manage_tab(self):
        params_frame = ctk.CTkFrame(master=self.subtabs.tab("RFC"))
        manage_dataset_frame = ctk.CTkFrame(master=self.subtabs.tab("RFC"))
        loading_frame = ctk.CTkFrame(master=self.subtabs.tab("RFC"))
        classifier_frame = ctk.CTkFrame(master=self.subtabs.tab("RFC"))

        # ----------- PARAMETERS -----------------
        clf_params_helper = Helper(master=params_frame, event_key="clf params")

        params_label = ctk.CTkLabel(master=params_frame, text="Classifier parameters")
        params_sframe = ctk.CTkScrollableFrame(master=params_frame, corner_radius=10)
        reload_button = ctk.CTkButton(master=params_frame, text="Reload default")

        params_sframe.grid_columnconfigure(0, weight=1)
        params_sframe.grid_columnconfigure(1, weight=2)

        sub_paramsframe = ctk.CTkFrame(master=params_sframe, )
        params_frame.place(relx=0, rely=0, relwidth=0.30, relheight=1)
        manage_dataset_frame.place(relx=0.33, rely=0, relwidth=0.30, relheight=0.85)

        clf = RandomForestClassifier()

        n_param = 0
        for name, value in clf.get_params().items():
            param_label = ctk.CTkLabel(master=sub_paramsframe, text=name, justify='left')
            param_label.grid(row=n_param, column=0, pady=10, padx=0)

            param_stringvar = tk.StringVar()
            param_stringvar.set(value)
            param_entry = ErrEntry(master=sub_paramsframe, state="normal", textvariable=param_stringvar, width=100)
            param_entry.grid(row=n_param, column=1, pady=10, padx=10)
            n_param += 1
            self.rfc_params_stringvar[name] = param_stringvar
            self.entries[f"params {param_stringvar.get()}"] = param_entry

        # ------------ MANAGE DATASET ------------------
        load_dataset_helper = Helper(master=manage_dataset_frame, event_key="load dataset")
        load_dataset_button = ctk.CTkButton(master=manage_dataset_frame, text="Load dataset")
        load_dataset_strvar = tk.StringVar()
        load_dataset_entry = ErrEntry(master=manage_dataset_frame, state='disabled',
                                      textvariable=load_dataset_strvar)

        select_target_helper = Helper(master=manage_dataset_frame, event_key="select targets")
        label_column_label = ctk.CTkLabel(master=manage_dataset_frame, text="Select targets column")
        label_column_var = tk.StringVar(value='None')
        label_column_cbbox = tk.ttk.Combobox(master=manage_dataset_frame, state='disabled', values=["None", ],
                                             textvariable=label_column_var)
        training_targets_helper = Helper(master=manage_dataset_frame, event_key="training targets")
        key_target_label = ctk.CTkLabel(master=manage_dataset_frame, text="Training targets:",
                                        text_color=gp.enabled_label_color)

        id_target_sv = ctk.StringVar()
        id_target_entry = ErrEntry(master=manage_dataset_frame, state='normal', textvariable=id_target_sv)
        add_target_button = ctk.CTkButton(master=manage_dataset_frame, text="+", width=25, height=25, state='normal')
        subtract_target_button = ctk.CTkButton(master=manage_dataset_frame, text="-", width=25, height=25,
                                               state='normal')
        training_textbox = ctk.CTkTextbox(master=manage_dataset_frame, corner_radius=10, state='disabled')
        n_iter_label = ctk.CTkLabel(master=manage_dataset_frame, text="Train / test iterations:")
        n_iter_sv = tk.StringVar()
        n_iter_sv.set("1")
        n_iter_entry = ErrEntry(master=manage_dataset_frame, textvariable=n_iter_sv, state='normal')
        get_advanced_metrics_helper = Helper(master=manage_dataset_frame, event_key="get advanced metrics")
        get_metrics_switch = ctk.CTkSwitch(master=manage_dataset_frame, text="Get advanced \nclassification metrics")
        load_classifier_helper = Helper(master=manage_dataset_frame, event_key="load clf")
        load_rfc_switch = ctk.CTkSwitch(master=manage_dataset_frame, text="Load pre-trained\nclassifier",
                                        command=self.load_classifier)
        load_clf_button = ctk.CTkButton(master=manage_dataset_frame, text="Load classifier", state='disabled')
        save_clf_helper = Helper(master=manage_dataset_frame, event_key="save clf")
        save_rfc_switch = ctk.CTkSwitch(master=manage_dataset_frame, text="Save classifier after training",
                                        command=self.save_classifier)
        save_files_label = ctk.CTkLabel(master=manage_dataset_frame, text="Save Classifier under:",
                                        text_color=gp.enabled_label_color)
        save_rfc_strvar = ctk.StringVar()
        save_entry = ErrEntry(master=manage_dataset_frame, textvariable=save_rfc_strvar)
        save_rfc_button = ctk.CTkButton(master=manage_dataset_frame, text="Save classifier as", state='disabled')

        # ----------- DISPLAY CLASSIFIER -----------------

        rfc_path_sv = tk.StringVar()
        rfc_path_label = ctk.CTkLabel(master=classifier_frame, text="Classifier path:")
        rfc_path_entry = ErrEntry(master=classifier_frame, textvariable=rfc_path_sv, state='disabled')

        rfc_name_sv = tk.StringVar()
        rfc_name_label = ctk.CTkLabel(master=classifier_frame, text="Classifier name:")
        rfc_name_entry = ErrEntry(master=classifier_frame, textvariable=rfc_name_sv, state='disabled')

        rfc_status_sv = tk.StringVar()
        rfc_status_label = ctk.CTkLabel(master=classifier_frame, text="Pre-Trained:")
        rfc_status_entry = ErrEntry(master=classifier_frame, textvariable=rfc_status_sv, state='disabled')

        advanced_metrics_helper = Helper(master=classifier_frame, event_key="advanced metrics")
        metrics_textbox = ctk.CTkTextbox(master=classifier_frame, state='disabled')
        export_button = ctk.CTkButton(master=classifier_frame, text="Export results", fg_color="green")

        # ----------- LOADING FRAME -------------------
        save_config_button = ctk.CTkButton(master=loading_frame, text="Save config", fg_color="lightslategray")
        load_config_button = ctk.CTkButton(master=loading_frame, text="Load config", fg_color="lightslategray")
        learning_button = ctk.CTkButton(master=loading_frame, text="Learning", fg_color="green")

        # -------- MANAGE WIDGETS

        loading_frame.place(relx=0.33, rely=0.9, relwidth=0.63, relheight=0.1)
        classifier_frame.place(relx=0.66, rely=0, relwidth=0.3, relheight=0.85)

        clf_params_helper.place(anchor=tk.NE, relx=1, rely=0)
        params_label.place(relx=0, rely=0)
        reload_button.place(relx=0.5, rely=0)
        params_sframe.place(relx=0.025, rely=0.1, relheight=0.85, relwidth=0.95)
        sub_paramsframe.place(relx=0, rely=0, relheight=1, relwidth=1)
        sub_paramsframe.grid(row=0, column=0, sticky=ctk.NSEW)

        load_dataset_helper.place(anchor=tk.NE, relx=1, rely=0)
        load_dataset_button.place(relx=0, rely=0, relwidth=0.2)
        load_dataset_entry.place_errentry(relx=0.25, rely=0, relwidth=0.65)
        select_target_helper.place(relx=0.25, rely=0.1)
        label_column_label.place(relx=0, rely=0.1)
        label_column_cbbox.place(relx=0, rely=0.15, relwidth=0.8)
        training_targets_helper.place(relx=0.28, rely=0.22)
        key_target_label.place(relx=0.05, rely=0.22)
        id_target_entry.place_errentry(relx=0.05, rely=0.28, relwidth=0.4)
        add_target_button.place(relx=0.5, rely=0.28)
        subtract_target_button.place(relx=0.6, rely=0.28)
        training_textbox.place(relx=0.05, rely=0.35, relwidth=0.4, relheight=0.43)
        n_iter_label.place(relx=0.5, rely=0.4)
        n_iter_entry.place_errentry(relx=0.5, rely=0.45, relwidth=0.1)
        get_advanced_metrics_helper.place(relx=0.9, rely=0.55)
        get_metrics_switch.place(relx=0.5, rely=0.55)
        load_classifier_helper.place(relx=0.9, rely=0.65)
        load_rfc_switch.place(relx=0.5, rely=0.65)
        load_clf_button.place(relx=0.5, rely=0.73, relwidth=0.3)
        save_clf_helper.place(relx=0.5, rely=0.83)
        save_rfc_switch.place(relx=0, rely=0.83)
        save_rfc_button.place(relx=0.66, rely=0.92, )
        save_files_label.place(relx=0, rely=0.87)
        save_entry.place_errentry(relx=0, rely=0.92, relwidth=0.65)

        rfc_path_label.place(relx=0, rely=0)
        rfc_path_entry.place_errentry(relx=0.25, rely=0, relwidth=0.7)
        rfc_name_label.place(relx=0, rely=0.1)
        rfc_name_entry.place_errentry(relx=0.25, rely=0.1, relwidth=0.3)
        rfc_status_label.place(relx=0, rely=0.2)
        rfc_status_entry.place_errentry(relx=0.25, rely=0.2, relwidth=0.3)
        advanced_metrics_helper.place(anchor=tk.SE, relx=1, rely=0.3)
        metrics_textbox.place(relx=0.05, rely=0.3, relwidth=0.9, relheight=0.6)
        export_button.place(anchor=tk.SE, relx=1, rely=1)

        save_config_button.place(anchor=tk.CENTER, relx=0.2, rely=0.5, relwidth=0.18)
        load_config_button.place(anchor=tk.CENTER, relx=0.4, rely=0.5, relwidth=0.18)
        learning_button.place(anchor=tk.CENTER, relx=0.8, rely=0.5, relwidth=0.18, relheight=0.8)

        self.buttons["reload"] = reload_button

        self.buttons["load dataset"] = load_dataset_button
        self.entries["load dataset"] = load_dataset_entry
        self.vars["load dataset"] = load_dataset_strvar
        self.cbboxes["target column"] = label_column_cbbox
        self.vars["target column"] = label_column_var
        self.entries["key target"] = id_target_entry
        self.vars["key target"] = id_target_sv
        self.buttons["add target"] = add_target_button
        self.buttons["subtract target"] = subtract_target_button
        self.textboxes["targets"] = training_textbox
        self.vars["n iter"] = n_iter_sv
        self.entries["n iter"] = n_iter_entry
        self.switches["get metrics"] = get_metrics_switch
        self.switches["load rfc"] = load_rfc_switch
        self.buttons["load rfc"] = load_clf_button
        self.switches["save rfc"] = save_rfc_switch
        self.entries["save rfc"] = save_entry
        self.vars["save rfc"] = save_rfc_strvar
        self.buttons["save rfc"] = save_rfc_button

        self.vars["rfc path"] = rfc_path_sv
        self.entries["rfc path"] = rfc_path_entry
        self.vars["rfc name"] = rfc_name_sv
        self.entries["rfc name"] = rfc_name_entry
        self.vars["rfc status"] = rfc_status_sv
        self.entries["rfc status"] = rfc_status_entry
        self.textboxes["metrics"] = metrics_textbox
        self.buttons["export"] = export_button

        self.buttons["save config"] = save_config_button
        self.buttons["load config"] = load_config_button
        self.buttons["learning"] = learning_button

        # ------------ CONFIGURE COMMANDS ---------------

        reload_button.configure(command=self.reload_rfc_params)
        load_dataset_button.configure(command=self.load_dataset)
        save_rfc_button.configure(command=partial(self.savepath_rfc, self.vars["save rfc"]))
        load_clf_button.configure(command=self.load_rfc)
        load_config_button.configure(command=self.load_model)
        save_config_button.configure(command=self.save_config)
        learning_button.configure(command=self.learning)
        export_button.configure(command=self.export)
        add_target_button.configure(command=self.add_target)
        subtract_target_button.configure(command=self.subtract_target)

        id_target_entry.bind('<Return>', self.add_target)
        id_target_entry.bind('<Control-BackSpace>', self.subtract_target)

        load_dataset_entry.configure(validate='focus',
                                     validatecommand=(self.register(partial(self.parent_view.is_valid_directory, load_dataset_entry)), '%P'))
        id_target_entry.configure(validate='focus',
                                  validatecommand=(self.register(partial(self.parent_view.has_forbidden_characters, id_target_entry)), '%P'))
        n_iter_entry.configure(validate='focus',
                               validatecommand=(self.register(partial(self.parent_view.is_positive_int, n_iter_entry)), '%P'))
        save_entry.configure(validate='focus',
                             validatecommand=(self.register(partial(self.parent_view.is_valid_directory, save_entry)), '%P'))
        rfc_path_entry.configure(validate='focus',
                                 validatecommand=(self.register(partial(self.parent_view.is_valid_directory, rfc_path_entry)), '%P'))
        rfc_name_entry.configure(validate='focus',
                                  validatecommand=(self.register(partial(self.parent_view.has_forbidden_characters, rfc_name_entry)), '%P'))
        rfc_status_entry.configure(validate='focus',
                                  validatecommand=(self.register(partial(self.parent_view.has_forbidden_characters, rfc_status_entry)), '%P'))
    def add_target(self, *args):
        if self.controller:
            self.controller.add_subtract_target('add')

    def subtract_target(self, *args):
        if self.controller:
            self.controller.add_subtract_target('subtract')

    def load_classifier(self):
        if self.switches["load rfc"].get():
            self.buttons["load rfc"].configure(state='normal')
        else:
            self.buttons["load rfc"].configure(state='disabled')

    def save_classifier(self):
        if self.switches["save rfc"].get():
            self.buttons["save rfc"].configure(state='normal')
        else:
            self.buttons["save rfc"].configure(state='disabled')

    def export(self):
        if self.controller:
            self.controller.export()

    def save_config(self):
        if self.controller:
            self.controller.save_config()

    def load_model(self):
        if self.controller:
            self.controller.load_config()

    def learning(self, ):
        if self.controller:
            self.controller.learning()

    def savepath_rfc(self, strvar):
        if self.controller:
            self.controller.savepath_rfc(strvar)

    def load_rfc(self):
        if self.controller:
            self.controller.load_rfc(self.rfc_params_stringvar, self.vars)

    def reload_rfc_params(self):
        if self.controller:
            self.controller.reload_rfc_params(self.rfc_params_stringvar)

    def load_dataset(self):
        if self.controller:
            self.controller.load_dataset()
