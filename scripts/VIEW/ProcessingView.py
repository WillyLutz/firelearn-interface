import tkinter as tk
from functools import partial
from tkinter import ttk

import customtkinter as ctk

import scripts.VIEW.graphic_params as gp
from scripts.CONTROLLER.ProcessingController import ProcessingController
from scripts.WIDGETS.Helper import Helper
from PIL import Image

from scripts.WIDGETS.ImageButton import ImageButton
from scripts.WIDGETS.ErrEntry import ErrEntry
from scripts.WIDGETS.Separator import  Separator
from scripts.WIDGETS.Pipeline import Pipeline
from scripts.params import resource_path
from scripts.WIDGETS.DragDropListbox import DragDropListbox

class ProcessingView(ctk.CTkFrame):
    def __init__(self, app, master, parent_view):
        super().__init__(master=app)
        self.app = app
        self.master = master
        self.parent_view = parent_view
        self.controller = ProcessingController(self)
        
        self.switches = {}
        self.entries = {}
        self.ckboxes = {}
        self.cbboxes = {}
        self.vars = {}
        self.sliders = {}
        self.buttons = {}
        self.textboxes = {}
        self.image_buttons = {}
        self.labels = {}
        
        self.frames = {}
        self.step_check = {"filename": 2, "signal": 2, "filesorter": 2, }
        self.content_frame = ctk.CTkFrame(master=self.master)
        self.content_frame.place(relx=0.15, rely=0, relwidth=0.85, relheight=0.9)
        
        self.manage_processing_tab()
    
    def manage_processing_tab(self):
        
        filesorter_ibtn = ImageButton(master=self.master,
                                      img=ctk.CTkImage(
                                          dark_image=Image.open(
                                              resource_path("data/firelearn_img/filesorter_grey.png")),
                                          size=(60, 60)),
                                      command=partial(self.show_filesorter_frame, ))
        signal_ibtn = ImageButton(master=self.master,
                                  img=ctk.CTkImage(
                                      dark_image=Image.open(resource_path("data/firelearn_img/signal_grey.png")),
                                      size=(60, 60)),
                                  command=partial(self.show_signal_frame, ))
        filename_ibtn = ImageButton(master=self.master,
                                    img=ctk.CTkImage(
                                        dark_image=Image.open(resource_path("data/firelearn_img/filename_grey.png")),
                                        size=(60, 60)),
                                    command=partial(self.show_filename_frame, ))
        
        filesorter_frame = ctk.CTkFrame(master=self.content_frame, )
        signal_frame = ctk.CTkFrame(master=self.content_frame, )
        filename_frame = ctk.CTkFrame(master=self.content_frame, )
        
        check_all_button = ctk.CTkButton(master=self.master, text="Check all steps",
                                         command=self.controller.check_params_validity,
                                         fg_color="green", )
        save_model_button = ctk.CTkButton(master=self.master, text="Save config", fg_color="lightslategray",
                                          command=self.save_config)
        load_model_button = ctk.CTkButton(master=self.master, text="Load config", fg_color="lightslategray",
                                          command=self.load_model)
        process_exec_button = ctk.CTkButton(master=self.master, fg_color="green", text="Process",
                                            command=self.processing)
        
        processing_summary_frame = ctk.CTkFrame(master=self.content_frame, )
        self.frames["processing summary"] = processing_summary_frame
        processing_summary_frame.place(relx=0.6, rely=0.05, relwidth=0.35, relheight=0.9)


        self.image_buttons["filesorter"] = filesorter_ibtn
        self.image_buttons["signal"] = signal_ibtn
        self.image_buttons["filename"] = filename_ibtn
        self.frames["filesorter"] = filesorter_frame
        self.frames["signal"] = signal_frame
        self.frames["filename"] = filename_frame
        
        check_all_button.place(anchor=tk.S, relx=0.25, rely=0.95)
        save_model_button.place(anchor=tk.S, relx=0.35, rely=0.95, )
        load_model_button.place(anchor=tk.S, relx=0.45, rely=0.95, )
        process_exec_button.place(anchor=tk.S, relx=0.55, rely=0.95, relheight=0.05)
        filesorter_ibtn.place(relx=0, rely=0)
        signal_ibtn.place(relx=0, rely=0.2)
        filename_ibtn.place(relx=0, rely=0.4)
        
        
        self.generate_summary()

        self.generate_filesorter_content()
        self.generate_signal_content()
        self.generate_filename_content()
        self.show_filesorter_frame()
        
    def trace_parent_path(self, *args):
        path = self.vars["filesorter multiple"].get()
        if len(path) > 35:
            path = "/.../..." + path[-35:]
        self.vars["summary multiple"].set(path)
        
    def trace_single_file_path(self, *args):
        path = self.vars["filesorter single"].get()
        if len(path) > 35:
            path = "/.../..." + path[-35:]
        self.vars["summary single"].set(path)
    def trace_multiple_files_checkbox(self, *args ):
        self.vars["summary multiple files"].set('enabled' if self.ckboxes["filesorter multiple"].get() else 'disabled')
    def trace_single_file_checkbox(self, *args ):
        self.vars["summary single file"].set('enabled' if self.ckboxes["filesorter single"].get() else 'disabled')
        
    def generate_summary(self):
        summary_scrollable_frame = ctk.CTkScrollableFrame(master=self.frames["processing summary"])
        
        summary_label = ctk.CTkLabel(master=summary_scrollable_frame, text="Processing summary", font=('', 20))
        filesorter_label = ctk.CTkLabel(master=summary_scrollable_frame, text="File sorting", font=('', 15))
        signal_processing_label = ctk.CTkLabel(master=summary_scrollable_frame, text="Signal processing", font=('', 15))
        output_label = ctk.CTkLabel(master=summary_scrollable_frame, text="Output", font=('', 15))
        
        summary_scrollable_frame.grid_columnconfigure(0, weight=10)
        summary_scrollable_frame.grid_columnconfigure(1, weight=10)
        summary_scrollable_frame.grid_columnconfigure(2, weight=1)
        
        multiple_files_frame = ctk.CTkFrame(master=summary_scrollable_frame, fg_color='transparent')
        multiple_files_label = ctk.CTkLabel(master=multiple_files_frame, text="Sorting multiple files: ")
        multiple_files_label_state_var = ctk.StringVar(value='disabled')
        multiple_files_label_state = ctk.CTkLabel(master=multiple_files_frame, textvariable=multiple_files_label_state_var)
        
        parent_path_frame = ctk.CTkFrame(master=summary_scrollable_frame, fg_color='transparent')
        parent_path_label_title = ctk.CTkLabel(master=parent_path_frame, text="Parent path: ")
        parent_path_label_var = ctk.StringVar(value='')
        parent_path_label = ctk.CTkLabel(master=parent_path_frame, textvariable=parent_path_label_var)
        
        to_include_label = ctk.CTkLabel(master=summary_scrollable_frame, text="To include:")
        to_exclude_label = ctk.CTkLabel(master=summary_scrollable_frame, text="To exclude:")
        include_exclude_frame = ctk.CTkFrame(master=summary_scrollable_frame, fg_color="transparent")
        include_textbox = ctk.CTkTextbox(master=include_exclude_frame, corner_radius=10, state='disabled')
        exclude_textbox = ctk.CTkTextbox(master=include_exclude_frame, corner_radius=10, state='disabled')
        
        targets_label = ctk.CTkLabel(master=summary_scrollable_frame, text="Targets")
        target_textbox = ctk.CTkTextbox(master=summary_scrollable_frame, corner_radius=10, state='disabled')
        
        single_file_frame = ctk.CTkFrame(master=summary_scrollable_frame, fg_color='transparent')
        single_file_label = ctk.CTkLabel(master=single_file_frame, text="Sorting single files: ")
        single_file_label_state_var = ctk.StringVar(value='disabled')
        single_file_label_state = ctk.CTkLabel(master=single_file_frame,
                                                  textvariable=single_file_label_state_var)
        
        file_path_frame = ctk.CTkFrame(master=summary_scrollable_frame, fg_color='transparent')
        file_path_label_title = ctk.CTkLabel(master=file_path_frame, text="File path: ")
        file_path_label_var = ctk.StringVar(value='')
        file_path_label = ctk.CTkLabel(master=file_path_frame, textvariable=file_path_label_var)

        # ------------  WIDGET MANAGEMENT
        summary_scrollable_frame.place(relwidth=1, relheight=1)
        # separator row 0
        # separator row 1
        # separator row 2
        summary_label.grid(row=3, column=0, columnspan=2)
        # separator row 4
        filesorter_label.grid(row=5, column=0, columnspan=2)
        # separator row 6
        multiple_files_frame.grid(row=7, column=0, sticky='ew', columnspan=2)
        multiple_files_label.pack(side="left")
        multiple_files_label_state.pack(side='left')
        # separator row 8
        parent_path_frame.grid(row=9, column=0, sticky='ew', columnspan=2)
        parent_path_label_title.pack(side='left')
        parent_path_label.pack(side='left')
        # separator row 10
        to_include_label.grid(row=11, column=0)
        to_exclude_label.grid(row=11, column=1)
        include_exclude_frame.grid(row=12, column=0, columnspan=2, sticky='nsew')
        include_textbox.pack(side='left', padx=5, pady=5)
        exclude_textbox.pack(side='left', padx=5, pady=5)
        # separator row 13
        targets_label.grid(row=14, column=0)
        target_textbox.grid(row=15, column=0, columnspan=2, sticky='ew')
        # separator row 16
        single_file_frame.grid(row=17, column=0, sticky='ew', columnspan=2)
        single_file_label.pack(side="left")
        single_file_label_state.pack(side='left')
        # separator row 18
        file_path_frame.grid(row=19, column=0, sticky='ew', columnspan=2)
        file_path_label_title.pack(side='left')
        file_path_label.pack(side='left')
        # separator row 20
        # separator row 21
        # separator row 22
        signal_processing_label.grid(row=23, column=0, columnspan=2)
        # separator row 24
        
        
        # ------------ SEPARATORS
        for row in range(0, 25, 1):
            if row in [0, 1, 2, 4, 6, 8, 10, 13, 16, 18, 20, 21, 22, 24]:
                sep = Separator(master=summary_scrollable_frame, orient='h')
                sep.grid(row=row, column=0, columnspan=2, sticky="ew")
                summary_scrollable_frame.grid_rowconfigure(row, weight=1)
            else:
                summary_scrollable_frame.grid_rowconfigure(row, weight=10)
        
        
        self.vars["summary multiple files"] = multiple_files_label_state_var
        self.vars["summary multiple"] = parent_path_label_var
        self.textboxes["summary inclusion"] = include_textbox
        self.textboxes["summary exclusion"] = exclude_textbox
        self.textboxes["summary targets"] = target_textbox
        self.vars["summary single file"] = single_file_label_state_var
        self.vars["summary single"] = file_path_label_var


        
    
    def generate_filesorter_content(self):
        
        filesorter_frame = self.frames["filesorter"]
        n_rows = 10
        for i in range(n_rows):
            filesorter_frame.grid_rowconfigure(i, weight=1)
        filesorter_frame.grid_columnconfigure(0, weight=1)
        filesorter_frame.grid_columnconfigure(1, weight=1)
        filesorter_frame.grid_columnconfigure(2, weight=20)
        filesorter_frame.grid_columnconfigure(3, weight=1)
        
        # ------- SORTING FILES -----------
        sorting_files_ckbox_var = ctk.IntVar(value=0)
        sorting_files_ckbox = ctk.CTkCheckBox(master=filesorter_frame, text="Sorting multiple files", variable=sorting_files_ckbox_var)
        
        sorting_frame = ctk.CTkFrame(master=filesorter_frame, fg_color='transparent')
        sorting_label = ctk.CTkLabel(master=sorting_frame, text="Path to parent directory:",
                                     text_color=gp.enabled_label_color)
        
        sorting_sv = ctk.StringVar()
        sorting_entry = ErrEntry(master=filesorter_frame, state='disabled', textvariable=sorting_sv)
        sorting_button = ctk.CTkButton(master=sorting_frame, text="Open", state='normal', width=40)
        
        sorting_helper = Helper(master=filesorter_frame, event_key="#sorting-multiple-files")
        
        to_include_frame = ctk.CTkFrame(master=filesorter_frame, fg_color='transparent')
        to_include_label = ctk.CTkLabel(master=to_include_frame, text="To include:",
                                        text_color=gp.enabled_label_color)
        include_sv = ctk.StringVar()
        include_entry = ErrEntry(master=filesorter_frame, state='normal', textvariable=include_sv)
        add_include_button = ctk.CTkButton(master=to_include_frame, text="+", width=25, height=25, state='normal')
        subtract_include_button = ctk.CTkButton(master=to_include_frame, text="-", width=25, height=25,
                                                state='normal')
        
        
        
        to_exclude_frame = ctk.CTkFrame(master=filesorter_frame, fg_color='transparent')
        to_exclude_label = ctk.CTkLabel(master=to_exclude_frame, text="To exclude:",
                                        text_color=gp.enabled_label_color)
        exclude_sv = ctk.StringVar()
        exclude_entry = ErrEntry(master=filesorter_frame, state='normal', textvariable=exclude_sv)
        add_exclude_button = ctk.CTkButton(master=to_exclude_frame, text="+", width=25, height=25, state='normal')
        subtract_exclude_button = ctk.CTkButton(master=to_exclude_frame, text="-", width=25, height=25,
                                                state='normal')
        
        target_key_frame = ctk.CTkFrame(master=filesorter_frame, fg_color='transparent')
        target_value_frame = ctk.CTkFrame(master=filesorter_frame, fg_color='transparent')
        
        key_target_label = ctk.CTkLabel(master=target_key_frame, text="Target key:",
                                        text_color=gp.enabled_label_color)
        value_target_label = ctk.CTkLabel(master=target_value_frame, text="Target value:",
                                          text_color=gp.enabled_label_color)
        id_target_sv = ctk.StringVar()
        id_target_entry = ErrEntry(master=filesorter_frame, state='normal', textvariable=id_target_sv)
        rename_target_sv = ctk.StringVar()
        rename_target_entry = ErrEntry(master=filesorter_frame, state='normal', textvariable=rename_target_sv)
        add_target_button = ctk.CTkButton(master=target_value_frame, text="+", width=25, height=25, state='normal')
        subtract_target_button = ctk.CTkButton(master=target_value_frame, text="-", width=25, height=25,
                                               state='normal')
        
        # -------- SINGLE FILE ------------
        single_file_frame = ctk.CTkFrame(master=filesorter_frame, fg_color='transparent')
        single_file_helper = Helper(master=filesorter_frame, event_key="#single-file-analysis")
        single_file_ckbox_var = ctk.IntVar(value=0)
        single_file_ckbox = ctk.CTkCheckBox(master=filesorter_frame, text="Single file analysis", variable=single_file_ckbox_var)
        single_file_label = ctk.CTkLabel(master=single_file_frame, text="Path to file:",
                                         text_color=gp.enabled_label_color)
        single_file_sv = ctk.StringVar()
        single_file_entry = ErrEntry(master=filesorter_frame, state='disabled', textvariable=single_file_sv)
        single_file_button = ctk.CTkButton(master=single_file_frame, text="Open", state='normal', width=40)
        
        # ------- MANAGE WIDGETS
        # sorting_helper.place(anchor=ctk.NE, relx=1, rely=0)
        # todo : add helper
        
        sorting_files_ckbox.grid(row=0, column=0, sticky='w' )
        
        # ---- row 1 separator ----
        
        sorting_frame.grid(row=2, column=0, sticky='ew')
        # sorting_entry.place_errentry(relx=0, rely=0.1, relwidth=0.6, relpadx=50)
        sorting_entry.grid(row=2, column=2 , sticky='ew')
        sorting_label.pack(side='left')
        sorting_button.pack(side='right')
        
        # ---- row 3 separator ----
        
        to_include_frame.grid(row=4, column=0, sticky='ew' )
        to_include_label.pack(side='left' )
        # include_entry.place_errentry(relx=0.0, rely=0.2, relwidth=0.3)
        add_include_button.pack(side='right' )
        subtract_include_button.pack(side='right' )
        include_entry.grid(row=4, column=2, sticky='ew')
        
        # ---- row 5 separator ----
        
        to_exclude_frame.grid(row=6, column=0, sticky='ew' )
        to_exclude_label.pack(side='left' )
        # exclude_entry.place_errentry(relx=0.5, rely=0.2, relwidth=0.3)
        add_exclude_button.pack(side='right' )
        subtract_exclude_button.pack(side='right' )
        exclude_entry.grid(row=6, column=2, sticky='ew' )
        
        # ---- row 7 separator ----
        
        target_key_frame.grid(row=8, column=0, sticky='ew' )
        id_target_entry.grid(row=8, column=2, sticky='ew' )

        # ---- row 9 separator ----
        
        target_value_frame.grid(row=10, column=0, sticky='ew' )
        rename_target_entry.grid(row=10, column=2, sticky='ew')
        
        key_target_label.pack(side='left')
        value_target_label.pack(side='left')
        # id_target_entry.place_errentry(relx=0, rely=0.54, relwidth=0.35)
        # rename_target_entry.place_errentry(relx=0.4, rely=0.54, relwidth=0.35)
        add_target_button.pack(side='right')
        subtract_target_button.pack(side='right')
        
        # ---- row 11 separator ----
        
        # single_file_helper.place(anchor=ctk.NE, relx=1, rely=0.85)
        # todo : add helper
        single_file_ckbox.grid(row=12, column=0, sticky='w' )
        
        # ---- row 13 separator ----
        
        single_file_frame.grid(row=14, column=0, sticky='ew' )
        single_file_label.pack(side='left')
        # single_file_entry.place_errentry(relx=0, rely=0.95, relwidth=0.6, relpady=0.04)
        single_file_entry.grid(row=14, column=2, sticky='ew')
        single_file_button.pack(side='right')
        
        self.ckboxes["filesorter multiple"] = sorting_files_ckbox
        self.vars["filesorter multiple"] = sorting_sv
        self.entries["filesorter multiple"] = sorting_entry
        self.ckboxes["filesorter single"] = single_file_ckbox
        self.vars["filesorter single"] = single_file_sv
        self.entries["filesorter single"] = single_file_entry
        self.vars["filesorter key target"] = id_target_sv
        self.vars["filesorter value target"] = rename_target_sv
        self.entries["filesorter key target"] = id_target_entry
        self.entries["filesorter value target"] = rename_target_entry
        self.vars["filesorter exclusion"] = exclude_sv
        self.entries["filesorter exclusion"] = exclude_entry
        self.vars["filesorter inclusion"] = include_sv
        self.entries["filesorter inclusion"] = include_entry
        
        
        # ------------ SEPARATORS
        for col in [1, ]:
            sep = Separator(master=filesorter_frame, orient='v')
            sep.grid(row=0, column=col, rowspan=20, sticky="ns")
            
        for row in range(0, 15, 1):
            if row in [1, 3, 5, 7, 9, 11, 13]:
                sep = Separator(master=filesorter_frame, orient='h')
                sep.grid(row=row, column=0, columnspan=20, sticky="ew")
                filesorter_frame.grid_rowconfigure(row, weight=1)
            else:
                filesorter_frame.grid_rowconfigure(row, weight=10)

        # ------------ CONFIGURE
        
        sorting_button.configure(command=partial(self.select_parent_directory, sorting_sv))
        add_include_button.configure(
            command=partial(self.add_subtract_to_include, entry=include_entry, textbox=self.textboxes["summary inclusion"], mode='add'))
        subtract_include_button.configure(
            command=partial(self.add_subtract_to_include, include_entry, self.textboxes["summary inclusion"], mode='subtract'))
        add_exclude_button.configure(
            command=partial(self.add_subtract_to_exclude, exclude_entry, self.textboxes["summary exclusion"], mode='add'))
        subtract_exclude_button.configure(
            command=partial(self.add_subtract_to_exclude, exclude_entry, self.textboxes["summary exclusion"], mode='subtract'))
        add_target_button.configure(
            command=partial(self.add_subtract_target, id_target_entry, rename_target_entry, self.textboxes["summary targets"],
                            mode='add'))
        subtract_target_button.configure(
            command=partial(self.add_subtract_target, id_target_entry, rename_target_entry, self.textboxes["summary targets"],
                            mode='subtract'))
        single_file_button.configure(command=partial(self.select_single_file, single_file_sv))
        # ----------- TRACE -------------------
        sorting_files_ckbox_var.trace("w", self.trace_multiple_files_checkbox)
        single_file_ckbox_var.trace("w", self.trace_single_file_checkbox)
        sorting_sv.trace("w", self.trace_parent_path)
        single_file_sv.trace("w", self.trace_single_file_path)
        
       
        
        # ---- ENTRY VALIDATION
        sorting_entry.configure(validate='focus',
                                validatecommand=(
                                    self.register(partial(self.parent_view.is_valid_directory, sorting_entry)), '%P'))
        single_file_entry.configure(validate='focus',
                                    validatecommand=(
                                        self.register(partial(self.parent_view.is_valid_directory, single_file_entry)),
                                        '%P'))
        
        # ------ ENTRY BINDING
        include_entry.bind('<Return>',
                           lambda event: self.add_subtract_to_include(include_entry, self.textboxes["summary inclusion"], 'add'))
        include_entry.bind('<Control-BackSpace>',
                           lambda event: self.add_subtract_to_include(include_entry, self.textboxes["summary inclusion"], 'subtract'))
        exclude_entry.bind('<Return>',
                           lambda event: self.add_subtract_to_exclude(exclude_entry, self.textboxes["summary exclusion"], mode='add'))
        exclude_entry.bind('<Control-BackSpace>',
                           lambda event: self.add_subtract_to_exclude(exclude_entry, self.textboxes["summary exclusion"], mode='subtract'))
        id_target_entry.bind('<Return>',
                             lambda event: self.add_subtract_target(id_target_entry, rename_target_entry,
                                                                    self.textboxes["summary targets"],
                                                                    'add'))
        id_target_entry.bind('<Control-BackSpace>',
                             lambda event: self.add_subtract_target(id_target_entry, rename_target_entry,
                                                                    self.textboxes["summary targets"],
                                                                    'subtract'))
        rename_target_entry.bind('<Return>',
                                 lambda event: self.add_subtract_target(id_target_entry, rename_target_entry,
                                                                        self.textboxes["summary targets"],
                                                                        'add'))
    
    def generate_signal_content(self):
        
        signal_frame = self.frames["signal"]
        
        # ------- signal behead ------------------
        raw_mea_helper = Helper(master=signal_frame, event_key="#using-raw-mea-recordings")
        
        behead_switch = ctk.CTkSwitch(master=signal_frame, text="Beheading top-file metadata", )
        behead_sv = ctk.StringVar()
        behead_entry = ErrEntry(master=signal_frame, state='normal', textvariable=behead_sv)
        
        # --------- signal select columns -------
        select_elec_helper = Helper(master=signal_frame, event_key="#selecting-electrodes")
        
        electrode_switch = ctk.CTkSwitch(master=signal_frame, text="Select columns", )
        electrode_mode_label = ctk.CTkLabel(master=signal_frame, text="mode: ", text_color=gp.enabled_label_color)
        
        electrode_metric_label = ctk.CTkLabel(master=signal_frame, text="metric: ",
                                              text_color=gp.enabled_label_color)
        n_electrode_label = ctk.CTkLabel(master=signal_frame, text="signal select columns number: ",
                                         text_color=gp.enabled_label_color)
        mode_electrode_cbox = tk.ttk.Combobox(master=signal_frame, values=["None", "max", ], state='readonly')
        mode_electrode_cbox.set("None")
        metric_electrode_cbox = tk.ttk.Combobox(master=signal_frame, values=["None", "std", ], state='readonly')
        metric_electrode_cbox.set("None")
        n_electrode_sv = ctk.StringVar()
        n_electrodes_entry = ErrEntry(master=signal_frame, state='normal', textvariable=n_electrode_sv)
        
        # ------- SAMPLING ------------------------
        sampling_helper = Helper(master=signal_frame, event_key="#recordings-down-sampling")
        
        sampling_switch = ctk.CTkSwitch(master=signal_frame, text="Divide file into")
        sampling_sv = ctk.StringVar()
        sampling_entry = ErrEntry(master=signal_frame, state='normal', textvariable=sampling_sv)
        sampling_pieces_label = ctk.CTkLabel(master=signal_frame, text="pieces", text_color=gp.enabled_label_color)
        
        # ------- FILTERING ------------------------
        filter_helper = Helper(master=signal_frame, event_key="#filtering")
        
        filter_switch = ctk.CTkSwitch(master=signal_frame, text="Filtering")
        
        order_filter_label = ctk.CTkLabel(master=signal_frame, text="Order: ", text_color=gp.enabled_label_color)
        order_filter_sv = ctk.StringVar()
        order_filter_entry = ErrEntry(master=signal_frame, state='normal', textvariable=order_filter_sv)
        sampling_filter_label = ctk.CTkLabel(master=signal_frame, text="Sampling frequency (Hz):",
                                             text_color=gp.enabled_label_color)
        sampling_filter_sv = ctk.StringVar()
        sampling_filter_entry = ErrEntry(master=signal_frame, state='normal', textvariable=sampling_filter_sv)
        
        type_filter_label = ctk.CTkLabel(master=signal_frame, text="Type: ", text_color=gp.enabled_label_color)
        frequency1_filter_label = ctk.CTkLabel(master=signal_frame, text="First cut frequency (Hz): ",
                                               text_color=gp.enabled_label_color)
        frequency2_filter_label = ctk.CTkLabel(master=signal_frame, text="Second cut frequency (optional, Hz): ",
                                               text_color=gp.enabled_label_color)
        type_filter_cbox = tk.ttk.Combobox(master=signal_frame,
                                           values=["None", "Highpass", "Lowpass", "Bandstop", "Bandpass"],
                                           state="readonly")
        type_filter_cbox.set("None")
        f1_filter_sv = ctk.StringVar()
        frequency1_filter_entry = ErrEntry(master=signal_frame, state='normal', textvariable=f1_filter_sv)
        f2_filter_sv = ctk.StringVar()
        frequency2_filter_entry = ErrEntry(master=signal_frame, state='normal', textvariable=f2_filter_sv)
        harmonics_label_filter = ctk.CTkLabel(master=signal_frame, text="Filter harmonics",
                                              text_color=gp.enabled_label_color)
        type_harmonics_label = ctk.CTkLabel(master=signal_frame, text="Type:", text_color=gp.enabled_label_color)
        freq_harmonics_label = ctk.CTkLabel(master=signal_frame, text="Frequency (Hz):",
                                            text_color=gp.enabled_label_color)
        nth_harmonics_label = ctk.CTkLabel(master=signal_frame, text="Up to Nth (Hz):",
                                           text_color=gp.enabled_label_color)
        type_harmonics_cbox = tk.ttk.Combobox(master=signal_frame,
                                              values=["Non", "All", "Even", "Odd", ],
                                              state="readonly")
        type_harmonics_cbox.set("None")
        freq_hamronics_sv = ctk.StringVar()
        frequency_harmonics_entry = ErrEntry(master=signal_frame, state='normal',
                                             textvariable=freq_hamronics_sv)
        nth_hamronics_sv = ctk.StringVar()
        nth_harmonics_entry = ErrEntry(master=signal_frame, state='normal', textvariable=nth_hamronics_sv)
        
        # ------- FREQUENTIAL PROCESSING -----------
        frequential_helper = Helper(master=signal_frame, event_key="#fast-fourier-transform")
        fft_switch = ctk.CTkSwitch(master=signal_frame, text="Fast Fourier Transform. Sampling frequency (Hz):")
        sampling_fft_sv = ctk.StringVar()
        sampling_fft_entry = ErrEntry(master=signal_frame, state='normal', textvariable=sampling_fft_sv)
        merge_switch = ctk.CTkSwitch(master=signal_frame, text="Average electrodes signal")
        smooth_switch = ctk.CTkSwitch(master=signal_frame, text="Smoothing row-wise data into")
        smooth_label = ctk.CTkLabel(master=signal_frame, text="values",
                                    text_color=gp.enabled_label_color)
        smooth_sv = ctk.StringVar()
        smooth_entry = ErrEntry(master=signal_frame, state='normal', textvariable=smooth_sv)
        
        # ------ MANAGING WIDGETS
        
        raw_mea_helper.place(anchor=ctk.NE, relx=1, rely=0)
        behead_switch.place(relx=0.0, rely=0)
        behead_entry.place_errentry(relx=0.4, rely=0, relwidth=0.2)
        
        select_elec_helper.place(anchor=ctk.NE, relx=1, rely=0.1)
        electrode_switch.place(relx=0.0, rely=0.1)
        electrode_mode_label.place(relx=0.0, rely=0.15, )
        electrode_metric_label.place(relx=0.2, rely=0.15, )
        n_electrode_label.place(relx=0.4, rely=0.15, )
        mode_electrode_cbox.place(relx=0.0, rely=0.2, relwidth=0.15)
        metric_electrode_cbox.place(relx=0.2, rely=0.2, relwidth=0.15)
        n_electrodes_entry.place_errentry(relx=0.4, rely=0.2, relwidth=0.15)
        
        sampling_helper.place(anchor=ctk.NE, relx=1, rely=0.3)
        sampling_switch.place(relx=0, rely=0.3)
        sampling_entry.place_errentry(relx=0.22, rely=0.3, relwidth=0.1)
        sampling_pieces_label.place(relx=0.38, rely=0.3)
        
        frequential_helper.place(anchor=ctk.NE, relx=1, rely=0.35)
        sampling_fft_entry.place_errentry(relx=0.55, rely=0.35)
        fft_switch.place(relx=0.0, rely=0.35)
        
        merge_switch.place(relx=0, rely=0.4)
        
        smooth_switch.place(relx=0, rely=0.45)
        smooth_entry.place_errentry(relx=0.38, rely=0.45, relwidth=0.1)
        smooth_label.place(relx=0.5, rely=0.45)
        
        filter_helper.place(anchor=ctk.NE, relx=1, rely=0.55)
        filter_switch.place(relx=0, rely=0.55)
        sampling_filter_label.place(relx=0.4, rely=0.6)
        order_filter_label.place(relx=0.0, rely=0.6)
        order_filter_entry.place_errentry(relx=0.1, rely=0.6, relwidth=0.2)
        sampling_filter_entry.place_errentry(relx=0.65, rely=0.6, relwidth=0.2)
        type_filter_label.place(relx=0, rely=0.65)
        type_filter_cbox.place(relx=0.08, rely=0.65, relwidth=0.15)
        frequency1_filter_label.place(relx=0, rely=0.7)
        frequency2_filter_label.place(relx=0.45, rely=0.7)
        frequency1_filter_entry.place_errentry(relx=0.25, rely=0.7, relwidth=0.15)
        frequency2_filter_entry.place_errentry(relx=0.8, rely=0.7, relwidth=0.15)
        
        harmonics_label_filter.place(relx=0, rely=0.8)
        type_harmonics_label.place(relx=0, rely=0.85)
        freq_harmonics_label.place(relx=0.3, rely=0.85)
        nth_harmonics_label.place(relx=0.7, rely=0.85)
        type_harmonics_cbox.place(relx=0, rely=0.9, relwidth=0.25)
        frequency_harmonics_entry.place_errentry(relx=0.3, rely=0.9, relwidth=0.3)
        nth_harmonics_entry.place_errentry(relx=0.7, rely=0.9, relwidth=0.2)
        
        self.switches["signal behead"] = behead_switch
        self.vars["signal behead"] = behead_sv
        self.entries["signal behead"] = behead_entry
        
        self.switches["signal select columns"] = electrode_switch
        self.cbboxes["signal select columns mode"] = mode_electrode_cbox
        self.cbboxes["signal select columns metric"] = metric_electrode_cbox
        self.vars["signal select columns number"] = n_electrode_sv
        self.entries["signal select columns number"] = n_electrodes_entry
        
        self.switches["signal sampling"] = sampling_switch
        self.entries["signal sampling"] = sampling_entry
        self.vars["signal sampling"] = sampling_sv
        
        self.switches["signal fft"] = fft_switch
        self.vars["signal fft sf"] = sampling_fft_sv
        self.entries["signal fft sf"] = sampling_fft_entry
        self.switches["signal merge"] = merge_switch
        self.switches["signal smoothing"] = smooth_switch
        self.vars["signal smoothing"] = smooth_sv
        self.entries["signal smoothing"] = smooth_entry
        
        self.switches["signal filter"] = filter_switch
        self.entries["signal filter order"] = order_filter_entry
        self.vars["signal filter order"] = order_filter_sv
        self.entries["signal filter sf"] = sampling_filter_entry
        self.vars["signal filter sf"] = sampling_filter_sv
        self.entries["signal filter first frequency"] = frequency1_filter_entry
        self.entries["signal filter second frequency"] = frequency2_filter_entry
        self.cbboxes["signal filter type"] = type_filter_cbox
        self.cbboxes["signal filter harmonic type"] = type_harmonics_cbox
        self.vars["signal filter harmonic frequency"] = freq_hamronics_sv
        self.entries["signal filter harmonic frequency"] = frequency_harmonics_entry
        self.vars["signal filter nth harmonic"] = nth_hamronics_sv
        self.entries["signal filter nth harmonic"] = nth_harmonics_entry
        
        # ------ CONFIGURE
        
        behead_entry.configure(validate='focus',
                               validatecommand=(
                                   self.register(partial(self.parent_view.is_positive_int_or_emtpy, behead_entry)),
                                   '%P'))
        n_electrodes_entry.configure(validate='focus',
                                     validatecommand=(self.register(
                                         partial(self.parent_view.is_positive_int_or_emtpy, n_electrodes_entry)), '%P'))
        sampling_entry.configure(validate='focus',
                                 validatecommand=(
                                     self.register(partial(self.parent_view.is_positive_int_or_emtpy, sampling_entry)),
                                     '%P'))
        
        order_filter_entry.configure(validate='focus',
                                     validatecommand=(self.register(
                                         partial(self.parent_view.is_positive_int_or_emtpy, order_filter_entry)), '%P'))
        sampling_filter_entry.configure(validate='focus',
                                        validatecommand=(self.register(
                                            partial(self.parent_view.is_positive_int_or_emtpy, sampling_filter_entry)),
                                                         '%P'))
        frequency1_filter_entry.configure(validate='focus',
                                          validatecommand=(self.register(
                                              partial(self.parent_view.is_positive_int_or_emtpy,
                                                      frequency1_filter_entry)), '%P'))
        frequency2_filter_entry.configure(validate='focus',
                                          validatecommand=(self.register(
                                              partial(self.parent_view.is_positive_int_or_emtpy,
                                                      frequency2_filter_entry)), '%P'))
        frequency_harmonics_entry.configure(validate='focus',
                                            validatecommand=(self.register(
                                                partial(self.parent_view.is_positive_int_or_emtpy,
                                                        frequency_harmonics_entry)), '%P'))
        nth_harmonics_entry.configure(validate='focus',
                                      validatecommand=(self.register(
                                          partial(self.parent_view.is_positive_int_or_emtpy, nth_harmonics_entry)),
                                                       '%P'))
        
        smooth_entry.configure(validate='focus',
                               validatecommand=(
                                   self.register(partial(self.parent_view.is_positive_int_or_emtpy, smooth_entry)),
                                   '%P'))
        sampling_fft_entry.configure(validate='focus',
                                     validatecommand=(self.register(
                                         partial(self.parent_view.is_positive_int_or_emtpy, sampling_fft_entry)), '%P'))
    
    def generate_filename_content(self):
        filename_frame = self.frames["filename"]
        
        filename_frame.place(relwidth=0.9, relheight=0.9, rely=0.05, relx=0.05)
        filename_frame.grid_columnconfigure(0, weight=1)
        
        # ----- EXECUTE
        exec_helper = Helper(master=filename_frame, event_key="#post-processing")
        random_key_exec_switch = ctk.CTkSwitch(master=filename_frame, text="Add random key to file names")
        timestamp_exec_switch = ctk.CTkSwitch(master=filename_frame, text="Add timestamp to file names")
        keyword_exec_switch = ctk.CTkSwitch(master=filename_frame, text="Add keyword to file names")
        keyword_sv = ctk.StringVar()
        keyword_entry = ErrEntry(master=filename_frame, state='normal', textvariable=keyword_sv)
        make_dataset_switch = ctk.CTkSwitch(master=filename_frame,
                                            text="Make resulting files as datasets for learning")
        save_files_exec_label = ctk.CTkLabel(master=filename_frame, text="Save processed files under:",
                                             text_color=gp.enabled_label_color)
        save_exec_sv = ctk.StringVar()
        save_entry = ErrEntry(master=filename_frame, textvariable=save_exec_sv, state='disabled')
        save_exec_button = ctk.CTkButton(master=filename_frame, text="Open")
        
        filename_switch = ctk.CTkSwitch(master=filename_frame, text="Specify file name")
        filename_var = ctk.StringVar()
        filename_entry = ErrEntry(master=filename_frame, state='normal', textvariable=filename_var)
        
        exec_helper.place(anchor=ctk.NE, relx=1, rely=0.65)
        random_key_exec_switch.place(relx=0, rely=0.05)
        timestamp_exec_switch.place(relx=0, rely=0.15)
        keyword_exec_switch.place(relx=0, rely=0.25)
        keyword_entry.place_errentry(relx=0, rely=0.30, relwidth=0.4, relpady=0.04)
        make_dataset_switch.place(relx=0, rely=0.4)
        
        filename_switch.place(relx=0, rely=0.5)
        filename_entry.place(relx=0, rely=0.55, relwidth=0.4)
        save_files_exec_label.place(relx=0, rely=0.65)
        save_entry.place_errentry(relx=0, rely=0.7, relwidth=0.4, relpady=0.05)
        save_exec_button.place(relx=0.4, rely=0.7, relwidth=0.1)
        
        self.switches["filename random key"] = random_key_exec_switch
        self.switches["filename timestamp"] = timestamp_exec_switch
        self.switches["filename keyword"] = keyword_exec_switch
        self.switches["filename"] = filename_switch
        self.switches["make dataset"] = make_dataset_switch
        self.entries["filename keyword"] = keyword_entry
        self.entries["filename"] = filename_entry
        self.entries["filename save under"] = save_entry
        self.vars["filename keyword"] = keyword_sv
        self.vars["filename save under"] = save_exec_sv
        
        # ----------- CONFIGURE
        
        keyword_exec_switch.configure(
            command=partial(self.controller.modulate_entry_state_by_switch, keyword_exec_switch,
                            keyword_entry))
        
        filename_switch.configure(
            command=partial(self.controller.modulate_entry_state_by_switch, filename_switch,
                            filename_entry))
        
        save_exec_button.configure(command=partial(self.select_save_directory, save_exec_sv))
        
        # ---- ENTRY VALIDATION
        save_entry.configure(validate='focus',
                             validatecommand=(
                                 self.register(partial(self.parent_view.is_valid_directory, save_entry)), '%P'))
        keyword_entry.configure(validate='focus',
                                validatecommand=(
                                    self.register(partial(self.parent_view.has_forbidden_characters, keyword_entry)),
                                    '%P'))
        filename_entry.configure(validate='focus',
                                 validatecommand=(
                                     self.register(partial(self.parent_view.has_forbidden_characters, filename_entry)),
                                     '%P'))
    
    def show_filesorter_frame(self, *args):
        self.select_check_processing_step("filesorter")
        
        self.frames['signal'].place_forget()
        self.frames['filename'].place_forget()
        self.frames["filesorter"].place(relx=0.05, rely=0.05, relwidth=0.5, relheight=0.9)
    
    def show_signal_frame(self, *args):
        self.select_check_processing_step('signal')
        
        self.frames['filesorter'].place_forget()
        self.frames['filename'].place_forget()
        self.frames["signal"].place(relx=0.05, rely=0.05, relwidth=0.5, relheight=0.9)
    
    def show_filename_frame(self, *args):
        self.select_check_processing_step('filename')
        
        self.frames['filesorter'].place_forget()
        self.frames['signal'].place_forget()
        self.frames["filename"].place(relx=0.05, rely=0.05, relwidth=0.5, relheight=0.9)
    
    def select_save_directory(self, strvar):
        if self.controller:
            self.controller.select_save_directory(strvar)
    
    def select_parent_directory(self, strvar):
        if self.controller:
            self.controller.select_parent_directory(strvar)
    
    def select_single_file(self, strvar):
        if self.controller:
            self.controller.select_single_file(strvar)
    
    def add_subtract_to_include(self, entry, textbox, mode='add', *args):
        if self.controller:
            self.controller.add_subtract_to_include(entry, textbox, mode)
    
    def add_subtract_to_exclude(self, entry, textbox, mode='add', *args):
        if self.controller:
            self.controller.add_subtract_to_exclude(entry, textbox, mode)
    
    def add_subtract_target(self, key_entry, value_entry, textbox,
                            mode='add', *args):
        if self.controller:
            self.controller.add_subtract_target(key_entry, value_entry, textbox, mode)
    
    def update_params(self, widgets: dict, ):
        if self.controller:
            self.controller.update_params(widgets)
    
    def processing(self, ):
        if self.controller:
            self.controller.processing()
    
    def check_params_validity(self, ):
        if self.controller:
            self.controller.check_params_validity()
    
    def update_number_of_tasks(self, n_file, n_col, ):
        if self.controller:
            self.controller.update_number_of_tasks(n_file, n_col)
    
    def save_config(self, ):
        if self.controller:
            self.controller.save_config()
    
    def load_model(self, ):
        if self.controller:
            self.controller.load_config()
    
    def select_check_processing_step(self, step=None):
        # todo : make images smaller when grey or red
        for s in ["filesorter", 'signal', 'filename']:
            if self.step_check[s] == 2:
                img = ctk.CTkImage(dark_image=Image.open(resource_path(f"data/firelearn_img/{s}_grey.png")),
                                   size=(60, 60))
                self.image_buttons[s].configure(image=img)
                self.image_buttons[s].set_image_size((60, 60))
            if self.step_check[s] == 1:
                img = ctk.CTkImage(dark_image=Image.open(resource_path(f"data/firelearn_img/{s}_green.png")),
                                   size=(60, 60))
                self.image_buttons[s].configure(image=img)
                self.image_buttons[s].set_image_size((60, 60))
            if self.step_check[s] == 0:
                img = ctk.CTkImage(dark_image=Image.open(resource_path(f"data/firelearn_img/{s}_red.png")),
                                   size=(60, 60))
                self.image_buttons[s].configure(image=img)
                self.image_buttons[s].set_image_size((60, 60))
            
            if step:
                if s == str(step):
                    img = ctk.CTkImage(dark_image=Image.open(resource_path(f"data/firelearn_img/{s}_blue.png")),
                                       size=(120, 120))
                    self.image_buttons[s].configure(image=img)
                    self.image_buttons[s].set_image_size((120, 120))

