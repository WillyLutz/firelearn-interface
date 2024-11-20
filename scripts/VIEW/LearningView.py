import tkinter as tk
from functools import partial
from tkinter import ttk, filedialog

import customtkinter as ctk
from sklearn.ensemble import RandomForestClassifier

import scripts.VIEW.graphic_params as gp
from scripts.CONTROLLER.LearningController import LearningController
from scripts.WIDGETS.ErrEntry import ErrEntry
from scripts.WIDGETS.Helper import Helper
from scripts.WIDGETS.Separator import Separator


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
        self.sliders = {}

        self.subtabs = ctk.CTkTabview(master=self.master, corner_radius=10)
        self.subtabs.place(relwidth=1.0, relheight=1.0)
        self.subtabs.add("RFC")

        self.manage_tab()

    def set_controller(self, controller):
        self.controller = controller

    def manage_params_frame(self, params_frame):
        # params_frame.grid_rowconfigure(2, weight=1)
        params_frame.grid_rowconfigure(5, weight=20)
        params_frame.grid_columnconfigure(0, weight=10)
        params_frame.grid_columnconfigure(1, weight=1)
        params_frame.grid_columnconfigure(2, weight=10)

        
        # row separator 0
        # row separator 1
        params_label = ctk.CTkLabel(master=params_frame, text="CLASSIFIER PARAMETERS", font=('', 20))
        reload_button = ctk.CTkButton(master=params_frame, text="Reload default")
        # row separator 3
        # row separator 4
        params_scrollable_frame = ctk.CTkScrollableFrame(master=params_frame, corner_radius=10, fg_color='transparent' )
        clf = RandomForestClassifier()
        params_scrollable_frame.grid_columnconfigure(0, weight=20)
        params_scrollable_frame.grid_columnconfigure(1, weight=1)
        params_scrollable_frame.grid_columnconfigure(2, weight=20)
        
        n_param = 0
        for name, value in clf.get_params().items():
            param_label = ctk.CTkLabel(master=params_scrollable_frame, text=name, justify='left')
            param_label.grid(row=n_param, column=0, pady=5, padx=0, sticky='w')
            
            param_stringvar = tk.StringVar()
            param_stringvar.set(value)
            param_entry = ErrEntry(master=params_scrollable_frame, state="normal", textvariable=param_stringvar, width=100)
            param_entry.grid(row=n_param, column=2, pady=5, padx=5, sticky='w')
            
            sep = Separator(master=params_scrollable_frame, orient='h')
            sep.grid(row=n_param + 1, column=0, columnspan=3, sticky='ew')
            
            params_scrollable_frame.grid_rowconfigure(n_param, weight=10)
            params_scrollable_frame.grid_rowconfigure(n_param + 1, weight=10)
            n_param += 2
            
            self.rfc_params_stringvar[name] = param_stringvar
            self.entries[f"params {param_stringvar.get()}"] = param_entry
        
        sep1 = Separator(master=params_scrollable_frame, orient='v')
        sep1.grid(row=0, column=1, rowspan=n_param, sticky='ns')
        
        reload_button.configure(command=self.reload_rfc_params)

        self.buttons["reload"] = reload_button
        
        params_label.grid(row=2, column=0, columnspan=3, sticky='w')
        reload_button.grid(row=2, column=2, sticky='e')
        params_scrollable_frame.grid(row=5, column=0, columnspan=3, sticky='nsew')
        
        # --------------- MANAGE SEPARATORS
        general_params_separators_indices = [0, 1, 3, 4, ]
        general_params_vertical_separator_ranges = []
        for r in range(general_params_separators_indices[-1] + 2):
            if r in general_params_separators_indices:
                sep = Separator(master=params_frame, orient='h')
                sep.grid(row=r, column=0, columnspan=3, sticky='ew')
        for couple in general_params_vertical_separator_ranges:
            general_v_sep = Separator(master=params_frame, orient='v')
            general_v_sep.grid(row=couple[0], column=1, rowspan=couple[1] - couple[0], sticky='ns')

        
    def manage_dataset_frame(self, dataset_frame):
        dataset_frame.grid_columnconfigure(0, weight=20)
        dataset_frame.grid_columnconfigure(1, weight=1)
        dataset_frame.grid_columnconfigure(2, weight=20)
        # row separator 0
        # row separator 1
        split_label = ctk.CTkLabel(master=dataset_frame, text="SPLIT DATASET", font=('', 20))
        # row separator 3,
        # row separator 4
        load_btn = ctk.CTkButton(master=dataset_frame, text="Load dataset", command=self.load_splitting_dataset)
        load_var = ctk.StringVar()
        load_entry = ctk.CTkEntry(dataset_frame, textvariable=load_var)
        # row separator 6
        ratio_label = ctk.CTkLabel(master=dataset_frame, text="Train/Test ratio:")
        ratio_var = tk.DoubleVar(value=0.7)
        ratio_label_var = ctk.CTkLabel(master=dataset_frame, textvariable=ratio_var)
        ratio_slider = ctk.CTkSlider(master=dataset_frame, from_=0, to=1, number_of_steps=20,
                                     variable=ratio_var)
        # row separator 8
        split_btn = ctk.CTkButton(master=dataset_frame, text="Split", command=self.controller.split_dataset,
                                  fg_color='tomato')
        # row separator 10
        # row separator 11
        train_test_label = ctk.CTkLabel(master=dataset_frame, text='TRAIN - TEST', font=('', 20))
        # row separator 13
        # row separator 14
        
        load_train_dataset_button = ctk.CTkButton(master=dataset_frame, text="Load Train dataset")
        load_train_dataset_strvar = tk.StringVar()
        load_train_dataset_entry = ErrEntry(master=dataset_frame, state='disabled',
                                      textvariable=load_train_dataset_strvar)
        # row separator 16
        load_test_dataset_button = ctk.CTkButton(master=dataset_frame, text="Load test dataset")
        load_test_dataset_strvar = tk.StringVar()
        load_test_dataset_entry = ErrEntry(master=dataset_frame, state='disabled',
                                            textvariable=load_test_dataset_strvar)
        # row separator 18
        label_column_label = ctk.CTkLabel(master=dataset_frame, text="Select targets column")
        label_column_var = tk.StringVar(value='None')
        label_column_cbbox = tk.ttk.Combobox(master=dataset_frame, state='disabled', values=["None", ],
                                             textvariable=label_column_var)
        # row separator 20
        training_target_frame = ctk.CTkFrame(master=dataset_frame, fg_color='transparent')
        key_target_label = ctk.CTkLabel(master=training_target_frame, text="Training targets:",
                                        text_color=gp.enabled_label_color)

        id_target_sv = ctk.StringVar()
        id_target_cbbox = tk.ttk.Combobox(master=dataset_frame, state='readonly', textvariable=id_target_sv,)
        add_target_button = ctk.CTkButton(master=training_target_frame, text="+", width=25, height=25, state='normal')
        subtract_target_button = ctk.CTkButton(master=training_target_frame, text="-", width=25, height=25,
                                               state='normal')
        # row separator 22
        training_textbox = ctk.CTkTextbox(master=dataset_frame, corner_radius=10, state='disabled', height=100)
        
        # row separator 24
        n_iter_label = ctk.CTkLabel(master=dataset_frame, text="Train / test iterations:")
        n_iter_sv = tk.StringVar(value="1")
        n_iter_entry = ErrEntry(master=dataset_frame, textvariable=n_iter_sv, state='normal')
        # row separator 26
        save_rfc_strvar = ctk.StringVar()
        save_entry = ErrEntry(master=dataset_frame, textvariable=save_rfc_strvar)
        save_rfc_button = ctk.CTkButton(master=dataset_frame, text="Save classifier as", )
        # row separator 28
        # --------------- MANAGE SEPARATORS
        general_params_separators_indices = [0, 1, 3, 4, 6, 8, 10, 11, 13, 14, 16 , 18, 20, 22, 24, 26, 28]
        general_params_vertical_separator_ranges = [(5, 8), (15, 23), (25, 28)]
        for r in range(general_params_separators_indices[-1] + 2):
            if r in general_params_separators_indices:
                sep = Separator(master=dataset_frame, orient='h')
                sep.grid(row=r, column=0, columnspan=3, sticky='ew')
        for couple in general_params_vertical_separator_ranges:
            general_v_sep = Separator(master=dataset_frame, orient='v')
            general_v_sep.grid(row=couple[0], column=1, rowspan=couple[1] - couple[0], sticky='ns')
            
        # ----------------- MANAGE WIDGETS
        split_label.grid(row=2, column=0, columnspan=3, sticky='we')
        load_btn.grid(row=5, column=0, sticky='w')
        load_entry.grid(row=5, column=2, sticky='we')
        ratio_label.grid(row=7, column=0, sticky='w')
        ratio_label_var.grid(row=7, column=0, sticky='e')
        ratio_slider.grid(row=7, column=2, sticky='we')
        split_btn.grid(row=9, column=0, columnspan=3, sticky='we')
        
        train_test_label.grid(row=12, column=0, columnspan=3, sticky='we')
        
        load_train_dataset_button.grid(row=15, column=0, sticky='w')
        load_train_dataset_entry.grid(row=15, column=2, sticky='we')
        load_test_dataset_button.grid(row=17, column=0, sticky='w')
        load_test_dataset_entry.grid(row=17, column=2, sticky='we')
        label_column_label.grid(row=19, column=0, sticky='w')
        label_column_cbbox.grid(row=19, column=2, sticky='we')
        training_target_frame.grid(row=21, column=0, sticky='nsew')
        training_target_frame.grid_columnconfigure(0, weight=8)
        id_target_cbbox.grid(row=21, column=2, sticky='we')
        key_target_label.grid(row=0, column=0, sticky='w')
        add_target_button.grid(row=0, column=1, sticky='w')
        subtract_target_button.grid(row=0, column=2, sticky='w')
        training_textbox.grid(row=23, column=0, columnspan=3, sticky='nsew')
        n_iter_label.grid(row=25, column=0, sticky='w')
        n_iter_entry.grid(row=25, column=2, sticky='we')
        save_rfc_button.grid(row=27, column=0, sticky='w')
        save_entry.grid(row=27, column=2, sticky='we')

    
        # ------------ STORE WIDGETS
        
        self.buttons["load train dataset"] = load_train_dataset_button
        self.entries["load train dataset"] = load_train_dataset_entry
        self.vars["load train dataset"] = load_train_dataset_strvar
        
        self.buttons["load test dataset"] = load_test_dataset_button
        self.entries["load test dataset"] = load_test_dataset_entry
        self.vars["load test dataset"] = load_test_dataset_strvar
        
        self.cbboxes["target column"] = label_column_cbbox
        self.vars["target column"] = label_column_var
        self.cbboxes["key target"] = id_target_cbbox
        self.vars["key target"] = id_target_sv
        self.buttons["add target"] = add_target_button
        self.buttons["subtract target"] = subtract_target_button
        self.textboxes["targets"] = training_textbox
        self.vars["n iter"] = n_iter_sv
        self.entries["n iter"] = n_iter_entry
        self.entries["save rfc"] = save_entry
        self.vars["save rfc"] = save_rfc_strvar
        self.buttons["save rfc"] = save_rfc_button
        
        self.vars["split dataset path"] = load_var
        self.vars["split dataset ratio"] = ratio_var
        self.entries["split dataset path"] = load_entry
        self.sliders["split dataset"] = ratio_slider
        
        ratio_var.trace("w", partial(self.trace_round_var, "split dataset ratio"))
        
        load_train_dataset_button.configure(command=self.load_train_dataset)
        load_test_dataset_button.configure(command=self.load_test_dataset)
        
        save_rfc_button.configure(command=partial(self.savepath_rfc, self.vars["save rfc"]))
        add_target_button.configure(command=self.add_target)
        subtract_target_button.configure(command=self.subtract_target)
        load_train_dataset_entry.configure(validate='focus',
                                           validatecommand=(self.register(
                                               partial(self.parent_view.is_valid_directory, load_train_dataset_entry)),
                                                            '%P'))
        
        n_iter_entry.configure(validate='focus',
                               validatecommand=(
                               self.register(partial(self.parent_view.is_positive_int, n_iter_entry)), '%P'))
        save_entry.configure(validate='focus',
                             validatecommand=(
                             self.register(partial(self.parent_view.is_valid_directory, save_entry)), '%P'))
        
    def manage_display_frame(self, display_frame):
        
        display_frame.grid_columnconfigure(0, weight=20)
        display_frame.grid_columnconfigure(1, weight=1)
        display_frame.grid_columnconfigure(2, weight=20)
        display_frame.grid_rowconfigure(5, weight=20)
        
        # ----------- DISPLAY CLASSIFIER -----------------
        # row separator 0
        # row separator 1
        metrics_label = ctk.CTkLabel(master=display_frame, text="METRICS", font=('', 20))
        # row separator 3
        # row separator 4
      
        metrics_textbox = ctk.CTkTextbox(master=display_frame, state='disabled')
        export_button = ctk.CTkButton(master=display_frame, text="Export results", fg_color="green")
    

        # --------------- MANAGE SEPARATORS
        general_params_separators_indices = [0, 1, 3, 4, 6]
        general_params_vertical_separator_ranges = []
        for r in range(general_params_separators_indices[-1] + 2):
            if r in general_params_separators_indices:
                sep = Separator(master=display_frame, orient='h')
                sep.grid(row=r, column=0, columnspan=3, sticky='ew')
        for couple in general_params_vertical_separator_ranges:
            general_v_sep = Separator(master=display_frame, orient='v')
            general_v_sep.grid(row=couple[0], column=1, rowspan=couple[1] - couple[0], sticky='ns')
    
        metrics_label.grid(row=2, column=0, columnspan=3, sticky='we')
        metrics_textbox.grid(row=5, column=0, columnspan=3, sticky='nswe')
        export_button.grid(row=7, column=0, sticky='w')
        
        self.textboxes["metrics"] = metrics_textbox
        self.buttons["export"] = export_button
        export_button.configure(command=self.export)
        
    def manage_execution_frame(self, execution_frame):
        execution_frame.grid_columnconfigure(0, weight=1)
        
        # ----------- LOADING FRAME -------------------
        execution_label = ctk.CTkLabel(master=execution_frame, text="EXECUTION", font=('', 20))
        save_config_button = ctk.CTkButton(master=execution_frame, text="Save config", fg_color="lightslategray")
        load_config_button = ctk.CTkButton(master=execution_frame, text="Load config", fg_color="lightslategray")
        splitting_button = ctk.CTkButton(master=execution_frame, text="Split train-test", fg_color="tomato")
        learning_button = ctk.CTkButton(master=execution_frame, text="Learning", fg_color="green")
        
        for i in [0, 1, 3, 4, 6, 8, 10, 12]:
            sep = Separator(master=execution_frame, orient='h')
            sep.grid(row=i, column=0, sticky='we')
        # -------- MANAGE WIDGETS
        execution_label.grid(row=2, column=0, sticky="we")
        save_config_button.grid(row=5, column=0, sticky='we')
        load_config_button.grid(row=7, column=0, sticky='we')
        splitting_button.grid(row=9, column=0, sticky='we')
        learning_button.grid(row=11, column=0, sticky='we')
        
        self.buttons["save config"] = save_config_button
        self.buttons["load config"] = load_config_button
        self.buttons["split"] = splitting_button
        self.buttons["learning"] = learning_button
        
        # ------------ CONFIGURE COMMANDS ---------------
        
        load_config_button.configure(command=self.load_model)
        save_config_button.configure(command=self.save_config)
        learning_button.configure(command=self.learning)
        
        
    def manage_tab(self):
        self.subtabs.tab("RFC").grid_columnconfigure(0, weight=1)
        self.subtabs.tab("RFC").grid_columnconfigure(1, weight=1)
        self.subtabs.tab("RFC").grid_columnconfigure(2, weight=1)
        self.subtabs.tab("RFC").grid_rowconfigure(0, weight=6)
        self.subtabs.tab("RFC").grid_rowconfigure(1, weight=1)
        
        params_frame = ctk.CTkFrame(master=self.subtabs.tab("RFC"))
        dataset_frame = ctk.CTkFrame(master=self.subtabs.tab("RFC"))
        execution_frame = ctk.CTkFrame(master=self.subtabs.tab("RFC"))
        display_frame = ctk.CTkFrame(master=self.subtabs.tab("RFC"))

        self.manage_params_frame(params_frame)
        self.manage_dataset_frame(dataset_frame)
        self.manage_display_frame(display_frame)
        self.manage_execution_frame(execution_frame)
        
        params_frame.grid(row=0, column=0, rowspan=2, sticky='nsew', padx=10)
        dataset_frame.grid(row=0, column=1, rowspan=2, sticky='nsew', padx=10)
        display_frame.grid(row=0, column=2, sticky='nsew', padx=2, pady=10)
        execution_frame.grid(row=1, column=2, sticky='nsew', padx=2, pady=10)

        

       

       
        
        
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

    def load_train_dataset(self):
        if self.controller:
            self.controller.load_train_dataset()

    def load_test_dataset(self):
        if self.controller:
            self.controller.load_test_dataset()


    def load_splitting_dataset(self):
        filename = filedialog.askopenfilename(title="Open file",
                                              filetypes=(("Tables", "*.txt *.xls *.xlsx *.csv"),))

        if filename:
            self.vars["split dataset path"].set(filename)

    def trace_round_var(self, *args):
        self.vars[args[0]].set(round(self.vars[args[0]].get(), 2))

