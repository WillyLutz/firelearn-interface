import tkinter as tk

import customtkinter
import customtkinter as ctk
from tkinter import ttk

import pandastable
from PIL import ImageTk, Image
from functools import partial
from pandastable import Table, TableModel
import pandas as pd
import data.params as p
import tkterminal
from tkterminal import Terminal
import VIEW.graphic_params as gp


class MainView(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(master=app)

        self.app = app
        self.app.geometry("1080x720")
        self.app.resizable(0, 0)
        self.app.configure(height=720, width=1080)

        self.master_frame = ctk.CTkFrame(master=self.app, )
        self.master_frame.place(relwidth=1.0, relheight=1.0)

        # ------------ MENU BAR ------------------------
        self.menu_bar = tk.Menu()
        self.file_menu = tk.Menu(self.menu_bar)
        self.file_menu.add_command(label="Save software state", command='')
        self.file_menu.add_command(label="Load software state", command='')
        self.file_menu.add_command(label="Exit", command=self.quit)

        self.help_menu = tk.Menu(self.menu_bar)
        self.help_menu.add_command(label="Getting Started", command='')
        self.help_menu.add_command(label="Help ?", command='')
        self.help_menu.add_command(label="About", command='')

        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)

        self.app.config(menu=self.menu_bar)

        # ------------- TABS MENU ----------------------
        self.tabs_view = ctk.CTkTabview(master=self.master_frame, border_color='red', corner_radius=10)
        self.tabs_view.place(relwidth=1.0, relheight=1.0)
        self.tabs_view.add("Home")
        self.tabs_view.add("Processing")
        self.tabs_view.add("Learning")
        self.tabs_view.add("Analysis")
        self.tabs_view.add("Terminal")

        self.learning_subtabs = ctk.CTkTabview(master=self.tabs_view.tab("Learning"), corner_radius=10)
        self.learning_subtabs.place(relwidth=1.0, relheight=1.0)
        self.learning_subtabs.add("RFC")
        self.learning_subtabs.add("SVM")

        self.analysis_subtabs = ctk.CTkTabview(master=self.tabs_view.tab("Analysis"), corner_radius=10)
        self.analysis_subtabs.place(relwidth=1.0, relheight=1.0)
        self.analysis_subtabs.add("Plot")
        self.analysis_subtabs.add("PCA")
        self.analysis_subtabs.add("Confusion")
        self.analysis_subtabs.add("Feature importance")

        # ------------- MANAGING PARENT TABS -----------
        self.manage_home_tab()
        self.manage_terminal_tab()
        self.manage_processing_tab()

        # ------------- SETTING CONTROLLER -------------
        self.controller = None
        self.terminal = None

    def manage_from_temporal_subtab(self):
        # ------- FRAMES ------------------
        sorting_frame = ctk.CTkFrame(master=self.tabs_view.tab("Processing"), )
        sorting_frame.place(relwidth=0.3, relheight=0.85)

        single_file_frame = ctk.CTkFrame(master=self.tabs_view.tab("Processing"), )
        single_file_frame.place(relwidth=0.3, relheight=0.15, rely=0.85)

        raw_mea_frame = ctk.CTkFrame(master=self.tabs_view.tab("Processing"), )
        raw_mea_frame.place(relwidth=0.3, relheight=0.15, rely=0, relx=0.33)

        select_elec_frame = ctk.CTkFrame(master=self.tabs_view.tab("Processing"), )
        select_elec_frame.place(relwidth=0.3, relheight=0.15, rely=0.15, relx=0.33)

        sampling_frame = ctk.CTkFrame(master=self.tabs_view.tab("Processing"), )
        sampling_frame.place(relwidth=0.3, relheight=0.15, rely=0.3, relx=0.33)

        filter_frame = ctk.CTkScrollableFrame(master=self.tabs_view.tab("Processing"), )
        filter_frame.place(relwidth=0.3, relheight=0.55, rely=0.45, relx=0.33)
        filter_frame.grid_columnconfigure(0, weight=1)

        frequential_frame = ctk.CTkFrame(master=self.tabs_view.tab("Processing"), )
        frequential_frame.place(relwidth=0.3, relheight=0.5, rely=0.0, relx=0.66)

        exec_frame = ctk.CTkFrame(master=self.tabs_view.tab("Processing"), )
        exec_frame.place(relwidth=0.3, relheight=0.45, rely=0.55, relx=0.66)

        # ------- SORTING FILES -----------
        sorting_files_switch = ctk.CTkSwitch(master=sorting_frame, text="Sorting multiple files")
        sorting_files_switch.place(relx=0, rely=0)
        sorting_label = ctk.CTkLabel(master=sorting_frame, text="Path to parent directory:", text_color=gp.disabled_label_color)
        sorting_label.place(relx=0, rely=0.05)
        sorting_sv = ctk.StringVar()
        sorting_entry = ctk.CTkEntry(master=sorting_frame, state='disabled', textvariable=sorting_sv)
        sorting_entry.place(relx=0, rely=0.1, relwidth=0.8)
        sorting_button = ctk.CTkButton(master=sorting_frame, text="Open", state='disabled')
        sorting_button.place(relx=0.8, rely=0.1, relwidth=0.15)

        to_include_label = ctk.CTkLabel(master=sorting_frame, text="To include:", text_color=gp.disabled_label_color)
        to_include_label.place(relx=0.05, rely=0.2)
        include_sv = ctk.StringVar()
        include_entry = ctk.CTkEntry(master=sorting_frame, state='disabled', textvariable=include_sv)
        include_entry.place(relx=0.3, rely=0.2, relwidth=0.4)
        add_include_button = ctk.CTkButton(master=sorting_frame, text="+", width=25, height=25, state='disabled')
        add_include_button.place(relx=0.75, rely=0.2)
        subtract_include_button = ctk.CTkButton(master=sorting_frame, text="-", width=25, height=25, state='disabled')
        subtract_include_button.place(relx=0.85, rely=0.2)
        include_textbox = ctk.CTkTextbox(master=sorting_frame, corner_radius=10, state='disabled')
        include_textbox.place(relx=0.05, rely=0.25, relwidth=0.9, relheight=0.15)

        to_exclude_label = ctk.CTkLabel(master=sorting_frame, text="To exclude:", text_color=gp.disabled_label_color)
        to_exclude_label.place(relx=0.05, rely=0.45)
        exclude_entry = ctk.CTkEntry(master=sorting_frame, state='disabled')
        exclude_entry.place(relx=0.3, rely=0.45, relwidth=0.4)
        add_exclude_button = ctk.CTkButton(master=sorting_frame, text="+", width=25, height=25, state='disabled')
        add_exclude_button.place(relx=0.75, rely=0.45)
        subtract_exclude_button = ctk.CTkButton(master=sorting_frame, text="-", width=25, height=25, state='disabled')
        subtract_exclude_button.place(relx=0.85, rely=0.45)
        exclude_textbox = ctk.CTkTextbox(master=sorting_frame, corner_radius=10, state='disabled')
        exclude_textbox.place(relx=0.05, rely=0.5, relwidth=0.9, relheight=0.15)

        id_target_label = ctk.CTkLabel(master=sorting_frame, text="Target's ID:", text_color=gp.disabled_label_color)
        id_target_label.place(relx=0.05, rely=0.7)
        rename_target_label = ctk.CTkLabel(master=sorting_frame, text="Rename target:", text_color=gp.disabled_label_color)
        rename_target_label.place(relx=0.38, rely=0.7)
        id_target_sv = ctk.StringVar()
        id_target_entry = ctk.CTkEntry(master=sorting_frame, state='disabled', textvariable=id_target_sv)
        id_target_entry.place(relx=0.05, rely=0.75, relwidth=0.3)
        rename_target_sv = ctk.StringVar()
        rename_target_entry = ctk.CTkEntry(master=sorting_frame, state='disabled', textvariable=rename_target_sv)
        rename_target_entry.place(relx=0.38, rely=0.75, relwidth=0.3)
        add_target_button = ctk.CTkButton(master=sorting_frame, text="+", width=25, height=25, state='disabled')
        add_target_button.place(relx=0.75, rely=0.75)
        subtract_target_button = ctk.CTkButton(master=sorting_frame, text="-", width=25, height=25, state='disabled')
        subtract_target_button.place(relx=0.85, rely=0.75)
        target_textbox = ctk.CTkTextbox(master=sorting_frame, corner_radius=10, state='disabled')
        target_textbox.place(relx=0.05, rely=0.8, relwidth=0.9, relheight=0.15)

        # -------- SINGLE FILE ------------
        single_file_switch = ctk.CTkSwitch(master=single_file_frame, text="Single file analysis")
        single_file_switch.place(relx=0, rely=0)
        single_file_label = ctk.CTkLabel(master=single_file_frame, text="Path to file:", text_color=gp.disabled_label_color)
        single_file_label.place(relx=0, rely=0.5)
        single_file_sv = ctk.StringVar()
        single_file_entry = ctk.CTkEntry(master=single_file_frame, state='disabled', textvariable=single_file_sv)
        single_file_entry.place(relx=0.2, rely=0.5, relwidth=0.6)
        single_file_button = ctk.CTkButton(master=single_file_frame, text="Open", state='disabled')
        single_file_button.place(relx=0.8, rely=0.5, relwidth=0.15)

        # ------- RAW MEA ------------------
        raw_mea_switch = ctk.CTkSwitch(master=raw_mea_frame, text="Raw MEA recording files", )
        raw_mea_switch.place(relx=0.0, rely=0)
        raw_mea_label = ctk.CTkLabel(master=raw_mea_frame, text="Size of info headers: ", text_color=gp.disabled_label_color)
        raw_mea_label.place(relx=0.0, rely=0.5, )
        raw_mea_sv = ctk.StringVar()
        raw_mea_entry = ctk.CTkEntry(master=raw_mea_frame, state='disabled', textvariable=raw_mea_sv)
        raw_mea_entry.place(relx=0.4, rely=0.5, relwidth=0.5)

        # --------- SELECT ELECTRODES -------
        electrode_switch = ctk.CTkSwitch(master=select_elec_frame, text="Select electrodes", )
        electrode_switch.place(relx=0.0, rely=0.0)
        electrode_mode_label = ctk.CTkLabel(master=select_elec_frame, text="mode: ", text_color=gp.disabled_label_color)
        electrode_mode_label.place(relx=0.0, rely=0.3, )
        electrode_metric_label = ctk.CTkLabel(master=select_elec_frame, text="metric: ", text_color=gp.disabled_label_color)
        electrode_metric_label.place(relx=0.33, rely=0.3, )
        n_electrode_label = ctk.CTkLabel(master=select_elec_frame, text="n electrodes: ", text_color=gp.disabled_label_color)
        n_electrode_label.place(relx=0.66, rely=0.3, )
        mode_electrode_opmenu = ctk.CTkOptionMenu(master=select_elec_frame, values=["max", ], state='disabled')
        mode_electrode_opmenu.set("max")
        mode_electrode_opmenu.place(relx=0.0, rely=0.66, relwidth=0.3)
        metric_electrode_opmenu = ctk.CTkOptionMenu(master=select_elec_frame, values=["std", ], state='disabled')
        metric_electrode_opmenu.set("std")
        metric_electrode_opmenu.place(relx=0.33, rely=0.66, relwidth=0.3)
        n_electrode_sv = ctk.StringVar()
        n_electrodes_entry = ctk.CTkEntry(master=select_elec_frame, state='disabled', textvariable=n_electrode_sv)
        n_electrodes_entry.place(relx=0.66, rely=0.66, relwidth=0.2)

        # ------- SAMPLING ------------------------
        sampling_switch = ctk.CTkSwitch(master=sampling_frame, text="Down sampling recordings")
        sampling_switch.place(relx=0, rely=0)
        sampling_divide_label = ctk.CTkLabel(master=sampling_frame, text="Divide recording into ", text_color=gp.disabled_label_color)
        sampling_divide_label.place(relx=0, rely=0.33)
        sampling_sv = ctk.StringVar()
        sampling_entry = ctk.CTkEntry(master=sampling_frame, state='disabled', textvariable=sampling_sv)
        sampling_entry.place(relx=0.40, rely=0.33, relwidth=0.2)
        sampling_pieces_label = ctk.CTkLabel(master=sampling_frame, text="pieces", text_color=gp.disabled_label_color)
        sampling_pieces_label.place(relx=0.7, rely=0.33)

        # ------- FILTERING ------------------------
        sub_filterframe = ctk.CTkFrame(master=filter_frame, height=280)
        sub_filterframe.grid(row=0, column=0, sticky=ctk.NSEW)

        name_filter_switch = ctk.CTkSwitch(master=sub_filterframe, text="Filter 1")
        name_filter_switch.place(relx=0, rely=0)

        add_filter_button = ctk.CTkButton(master=sub_filterframe, text="+", width=25, height=25, state='disabled')
        add_filter_button.place(relx=0.8, rely=0)
        subtract_filter_button = ctk.CTkButton(master=sub_filterframe, text="-", width=25, height=25, state='disabled')
        subtract_filter_button.place(relx=0.9, rely=0)

        order_filter_label = ctk.CTkLabel(master=sub_filterframe, text="Order: ", text_color=gp.disabled_label_color)
        order_filter_label.place(relx=0.0, rely=0.10)
        order_filter_sv = ctk.StringVar()
        order_filter_entry = ctk.CTkEntry(master=sub_filterframe, state='disabled', textvariable=order_filter_sv)
        order_filter_entry.place(relx=0.0, rely=0.20, relwidth=0.2)
        sampling_filter_label = ctk.CTkLabel(master=sub_filterframe, text="Sampling frequency (Hz):", text_color=gp.disabled_label_color)
        sampling_filter_label.place(relx=0.4, rely=0.10)
        sampling_filter_sv = ctk.StringVar()
        sampling_filter_entry = ctk.CTkEntry(master=sub_filterframe, state='disabled', textvariable=sampling_filter_sv)
        sampling_filter_entry.place(relx=0.4, rely=0.20, relwidth=0.2)

        type_filter_label = ctk.CTkLabel(master=sub_filterframe, text="Type: ", text_color=gp.disabled_label_color)
        type_filter_label.place(relx=0, rely=0.35)
        frequency1_filter_label = ctk.CTkLabel(master=sub_filterframe, text="f1 (Hz): ", text_color=gp.disabled_label_color)
        frequency1_filter_label.place(relx=0.5, rely=0.35)
        frequency2_filter_label = ctk.CTkLabel(master=sub_filterframe, text="f2 (Hz): ", text_color=gp.disabled_label_color)
        frequency2_filter_label.place(relx=0.8, rely=0.35)
        type_filter_opmenu = ctk.CTkOptionMenu(master=sub_filterframe,
                                               values=["Highpass", "Lowpass", "Bandstop", "Bandpass"],
                                               state="disabled")
        type_filter_opmenu.set("Highpass")
        type_filter_opmenu.place(relx=0, rely=0.45, relwidth=0.4)
        f1_filter_sv = ctk.StringVar()
        frequency1_filter_entry = ctk.CTkEntry(master=sub_filterframe, state='disabled', textvariable=f1_filter_sv)
        frequency1_filter_entry.place(relx=0.5, rely=0.45, relwidth=0.2)
        f2_filter_sv = ctk.StringVar()
        frequency2_filter_entry = ctk.CTkEntry(master=sub_filterframe, state='disabled', textvariable=f2_filter_sv)
        frequency2_filter_entry.place(relx=0.8, rely=0.45, relwidth=0.2)

        harmonics_label_filter = ctk.CTkLabel(master=sub_filterframe, text="Filter harmonics", text_color=gp.disabled_label_color)
        harmonics_label_filter.place(relx=0, rely=0.65)

        type_harmonics_label = ctk.CTkLabel(master=sub_filterframe, text="Type:", text_color=gp.disabled_label_color)
        type_harmonics_label.place(relx=0, rely=0.75)
        freq_harmonics_label = ctk.CTkLabel(master=sub_filterframe, text="Frequency (Hz):", text_color=gp.disabled_label_color)
        freq_harmonics_label.place(relx=0.3, rely=0.75)
        nth_harmonics_label = ctk.CTkLabel(master=sub_filterframe, text="Up to Nth (Hz):", text_color=gp.disabled_label_color)
        nth_harmonics_label.place(relx=0.7, rely=0.75)

        type_harmonics_opmenu = ctk.CTkOptionMenu(master=sub_filterframe,
                                                  values=["All", "Even", "Odd", ],
                                                  state="disabled")
        type_harmonics_opmenu.set("All")
        type_harmonics_opmenu.place(relx=0, rely=0.85, relwidth=0.25)
        freq_hamronics_sv = ctk.StringVar()
        frequency_harmonics_entry = ctk.CTkEntry(master=sub_filterframe, state='disabled', textvariable=freq_hamronics_sv)
        frequency_harmonics_entry.place(relx=0.3, rely=0.85, relwidth=0.3)
        nth_hamronics_sv = ctk.StringVar()
        nth_harmonics_entry = ctk.CTkEntry(master=sub_filterframe, state='disabled', textvariable=nth_hamronics_sv)
        nth_harmonics_entry.place(relx=0.7, rely=0.85, relwidth=0.2)

        # ------- FREQUENTIAL PROCESSING -----------
        fft_switch = ctk.CTkSwitch(master=frequential_frame, text="Fast Fourier Transform")
        fft_switch.place(relx=0.0, rely=0)
        sampling_fft_label = ctk.CTkLabel(master=frequential_frame, text="Sampling frequency (Hz):", text_color=gp.disabled_label_color)
        sampling_fft_label.place(relx=0, rely=0.15)
        sampling_fft_sv = ctk.StringVar()
        sampling_fft_entry = ctk.CTkEntry(master=frequential_frame, state='disabled', textvariable=sampling_fft_sv)
        sampling_fft_entry.place(relx=0, rely=0.25)
        merge_switch = ctk.CTkSwitch(master=frequential_frame, text="Average electrodes signal")
        merge_switch.place(relx=0, rely=0.5)
        smooth_switch = ctk.CTkSwitch(master=frequential_frame, text="Smoothing signal")
        smooth_switch.place(relx=0, rely=0.65)
        smooth_label = ctk.CTkLabel(master=frequential_frame, text="n final values:", text_color=gp.disabled_label_color)
        smooth_label.place(relx=0, rely=0.75)
        smooth_sv = ctk.StringVar()
        smooth_entry = ctk.CTkEntry(master=frequential_frame, state='disabled', textvariable=smooth_sv)
        smooth_entry.place(relx=0, rely=0.85)

        # ------- EXECUTE PROCESSING ---------------
        random_key_exev_switch = ctk.CTkSwitch(master=exec_frame, text="Add random key to file names")
        random_key_exev_switch.place(relx=0, rely=0)

        timestamp_exec_switch = ctk.CTkSwitch(master=exec_frame, text="Add timestamp to file names")
        timestamp_exec_switch.place(relx=0, rely=0.15)

        keyword_exec_switch = ctk.CTkSwitch(master=exec_frame, text="Add keyword to file names")
        keyword_exec_switch.place(relx=0, rely=0.30)
        keyword_sv = ctk.StringVar()
        keyword_exec_entry = ctk.CTkEntry(master=exec_frame, state='disabled', textvariable=keyword_sv)
        keyword_exec_entry.place(relx=0, rely=0.40, relwidth=0.7)

        save_files_exec_label = ctk.CTkLabel(master=exec_frame, text="Save processed files under:", text_color=gp.enabled_label_color)
        save_files_exec_label.place(relx=0, rely=0.55)
        save_exec_sv = ctk.StringVar()
        save_exec_entry = ctk.CTkEntry(master=exec_frame, textvariable=save_exec_sv)
        save_exec_entry.place(relx=0, rely=0.7, relwidth=0.7)
        save_exec_button = ctk.CTkButton(master=exec_frame, text="Open")
        save_exec_button.place(relx=0.8, rely=0.7, relwidth=0.15)

        process_exec_button = ctk.CTkButton(master=exec_frame, fg_color="green", text="Process")
        process_exec_button.place(relx=0.7, rely=0.85, relwidth=0.3, relheight=0.15)

        # ------- CONFIGURE SWITCHES COMMANDS ---------------
        sorting_files_switch.configure(command=partial(self.category_enabling_switch, sorting_files_switch, sorting_frame))
        single_file_switch.configure(command=partial(self.category_enabling_switch, single_file_switch, single_file_frame))
        raw_mea_switch.configure(command=partial(self.category_enabling_switch, raw_mea_switch, raw_mea_frame))
        sampling_switch.configure(command=partial(self.category_enabling_switch, sampling_switch, sampling_frame))
        electrode_switch.configure(command=partial(self.category_enabling_switch, electrode_switch, select_elec_frame))
        fft_switch.configure(command=partial(self.category_enabling_switch, fft_switch, frequential_frame))
        keyword_exec_switch.configure(command=partial(self.add_keyword_filename, keyword_exec_switch, keyword_exec_entry))
        name_filter_switch.configure(command=partial(self.category_enabling_switch, name_filter_switch, sub_filterframe))

        sorting_button.configure(command=partial(self.select_parent_directory, display_in=sorting_sv))
        add_include_button.configure(command=partial(self.add_subtract_to_include, include_entry, include_textbox, mode='add'))
        subtract_include_button.configure(command=partial(self.add_subtract_to_include, include_entry, include_textbox, mode='subtract'))
        add_exclude_button.configure(command=partial(self.add_subtract_to_exclude, exclude_entry, exclude_textbox, mode='add'))
        subtract_exclude_button.configure(command=partial(self.add_subtract_to_exclude, exclude_entry, exclude_textbox, mode='subtract'))
        

    def select_parent_directory(self, display_in):
        if self.controller:
            self.controller.select_parent_directory(display_in=display_in)

    def add_subtract_to_include(self, entry, textbox, mode):
        if self.controller:
            self.controller.add_subtract_to_include_for_processing(entry, textbox, mode)
            
    def add_subtract_to_exclude(self, entry, textbox, mode):
        if self.controller:
            self.controller.add_subtract_to_exclude_for_processing(entry, textbox, mode)


    def add_keyword_filename(self, switch, entry):
        if self.controller:
            self.controller.add_keyword_filename(switch, entry)


    def category_enabling_switch(self, switch, parent_widget):
        if self.controller:
            self.controller.category_enabling_switch(switch, parent_widget)

    def manage_processing_tab(self):
        self.manage_from_temporal_subtab()

    def manage_terminal_tab(self):
        term_frame = ctk.CTkFrame(master=self.tabs_view.tab("Terminal"), )
        term_frame.place(relwidth=1, relheight=1)
        # self.terminal = Terminal(master=self.tabs_view.tab("Terminal"))
        # self.terminal.place(relwidth=1, relheight=1, anchor=ctk.NW) todo: fix this

    def manage_home_tab(self):
        welcome_label = ctk.CTkLabel(self.tabs_view.tab("Home"), text=f"Welcome to FireLearn", font=('', 18, 'bold'))
        welcome_label.place(relwidth=0.5, relheight=0.1)
        message = "FireLearn is an independent python library used\n" \
                  " to do machine learning and deep learning. This\n" \
                  " tool is especially made for a user friendly \n" \
                  "approach of the artificial intelligence applied\n" \
                  " in a biological context. \n\n" \
                  "FireLearn GUI has been developed by a third party\n" \
                  "and do not display any licence."
        welcome_message = ctk.CTkLabel(self.tabs_view.tab("Home"), text=message, font=('', 15))
        welcome_message.place(anchor=ctk.W, rely=0.3, relwidth=0.5, )

        disclaimer_label = ctk.CTkLabel(self.tabs_view.tab("Home"), text="In development, for personal use only - "
                                                                         "LUTZ W. 2023")
        disclaimer_label.place(anchor=ctk.S, relwidth=1, rely=0.95, relx=0.5)

        fl_logo = ctk.CTkImage(dark_image=Image.open("data/logo firelearn temporary.png"), size=(500, 500))
        fl_label = ctk.CTkLabel(master=self.tabs_view.tab("Home"), image=fl_logo, text="")
        fl_label.place(relx=0.5, rely=0)

        github_image = customtkinter.CTkImage(dark_image=Image.open("data/github_logo.png"),
                                              size=(60, 60))
        github_button = ctk.CTkButton(master=self.tabs_view.tab("Home"), image=github_image, text="",
                                      width=70, height=70, corner_radius=10,
                                      command=partial(self.open_web,
                                                      "https://github.com/WillyLutz/firelearn-interface"))
        github_button.place(relx=0.1, rely=0.6)

    def open_web(self, url):
        if self.controller:
            self.controller.open_web(url)

    def set_controller(self, controller):
        self.controller = controller
