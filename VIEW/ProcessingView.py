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


class ProcessingView(ctk.CTkFrame):
    def __init__(self, app, master, controller):
        super().__init__(master=app)
        self.master = master
        self.controller = controller

        self.manage_processing_tab()

    def manage_processing_tab(self):
        # ------- FRAMES ------------------
        sorting_frame = ctk.CTkFrame(master=self.master, )
        sorting_frame.place(relwidth=0.3, relheight=0.85)

        single_file_frame = ctk.CTkFrame(master=self.master, )
        single_file_frame.place(relwidth=0.3, relheight=0.15, rely=0.85)

        raw_mea_frame = ctk.CTkFrame(master=self.master, )
        raw_mea_frame.place(relwidth=0.3, relheight=0.15, rely=0, relx=0.33)

        select_elec_frame = ctk.CTkFrame(master=self.master, )
        select_elec_frame.place(relwidth=0.3, relheight=0.15, rely=0.15, relx=0.33)

        sampling_frame = ctk.CTkFrame(master=self.master, )
        sampling_frame.place(relwidth=0.3, relheight=0.15, rely=0.3, relx=0.33)

        filter_frame = ctk.CTkScrollableFrame(master=self.master, )
        filter_frame.place(relwidth=0.3, relheight=0.55, rely=0.45, relx=0.33)
        filter_frame.grid_columnconfigure(0, weight=1)

        frequential_frame = ctk.CTkFrame(master=self.master, )
        frequential_frame.place(relwidth=0.3, relheight=0.4, rely=0.0, relx=0.66)

        exec_frame = ctk.CTkFrame(master=self.master, )
        exec_frame.place(relwidth=0.3, relheight=0.55, rely=0.45, relx=0.66)

        # ------- SORTING FILES -----------
        sorting_files_switch = ctk.CTkSwitch(master=sorting_frame, text="Sorting multiple files")
        sorting_files_switch.place(relx=0, rely=0)
        sorting_label = ctk.CTkLabel(master=sorting_frame, text="Path to parent directory:",
                                     text_color=gp.disabled_label_color)
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

        id_target_label = ctk.CTkLabel(master=sorting_frame, text="Target'n_sample ID:",
                                       text_color=gp.disabled_label_color)
        id_target_label.place(relx=0.05, rely=0.7)
        rename_target_label = ctk.CTkLabel(master=sorting_frame, text="Rename target:",
                                           text_color=gp.disabled_label_color)
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
        single_file_label = ctk.CTkLabel(master=single_file_frame, text="Path to file:",
                                         text_color=gp.disabled_label_color)
        single_file_label.place(relx=0, rely=0.5)
        single_file_sv = ctk.StringVar()
        single_file_entry = ctk.CTkEntry(master=single_file_frame, state='disabled', textvariable=single_file_sv)
        single_file_entry.place(relx=0.2, rely=0.5, relwidth=0.6)
        single_file_button = ctk.CTkButton(master=single_file_frame, text="Open", state='disabled')
        single_file_button.place(relx=0.8, rely=0.5, relwidth=0.15)

        # ------- RAW MEA ------------------
        raw_mea_switch = ctk.CTkSwitch(master=raw_mea_frame, text="Raw MEA recording files", )
        raw_mea_switch.place(relx=0.0, rely=0)
        raw_mea_label = ctk.CTkLabel(master=raw_mea_frame, text="Size of info headers: ",
                                     text_color=gp.disabled_label_color)
        raw_mea_label.place(relx=0.0, rely=0.5, )
        raw_mea_sv = ctk.StringVar()
        raw_mea_entry = ctk.CTkEntry(master=raw_mea_frame, state='disabled', textvariable=raw_mea_sv)
        raw_mea_entry.place(relx=0.4, rely=0.5, relwidth=0.5)

        # --------- SELECT ELECTRODES -------
        electrode_switch = ctk.CTkSwitch(master=select_elec_frame, text="Select electrodes", )
        electrode_switch.place(relx=0.0, rely=0.0)
        electrode_mode_label = ctk.CTkLabel(master=select_elec_frame, text="mode: ", text_color=gp.disabled_label_color)
        electrode_mode_label.place(relx=0.0, rely=0.3, )
        electrode_metric_label = ctk.CTkLabel(master=select_elec_frame, text="metric: ",
                                              text_color=gp.disabled_label_color)
        electrode_metric_label.place(relx=0.33, rely=0.3, )
        n_electrode_label = ctk.CTkLabel(master=select_elec_frame, text="n electrodes: ",
                                         text_color=gp.disabled_label_color)
        n_electrode_label.place(relx=0.66, rely=0.3, )
        mode_electrode_cbox = tk.ttk.Combobox(master=select_elec_frame, values=["max", ], state='disabled')
        mode_electrode_cbox.set("max")
        mode_electrode_cbox.place(relx=0.0, rely=0.66, relwidth=0.3)
        metric_electrode_cbox = tk.ttk.Combobox(master=select_elec_frame, values=["std", ], state='disabled')
        metric_electrode_cbox.set("std")
        metric_electrode_cbox.place(relx=0.33, rely=0.66, relwidth=0.3)
        n_electrode_sv = ctk.StringVar()
        n_electrodes_entry = ctk.CTkEntry(master=select_elec_frame, state='disabled', textvariable=n_electrode_sv)
        n_electrodes_entry.place(relx=0.66, rely=0.66, relwidth=0.2)

        # ------- SAMPLING ------------------------
        sampling_switch = ctk.CTkSwitch(master=sampling_frame, text="Down sampling recordings")
        sampling_switch.place(relx=0, rely=0)
        sampling_divide_label = ctk.CTkLabel(master=sampling_frame, text="Divide recording into ",
                                             text_color=gp.disabled_label_color)
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

        # add_filter_button = ctk.CTkButton(parent=sub_filterframe, text="+", width=25, height=25, state='disabled')
        # add_filter_button.place(relx=0.8, rely=0)
        # subtract_filter_button = ctk.CTkButton(parent=sub_filterframe, text="-", width=25, height=25, state='disabled')
        # subtract_filter_button.place(relx=0.9, rely=0)

        order_filter_label = ctk.CTkLabel(master=sub_filterframe, text="Order: ", text_color=gp.disabled_label_color)
        order_filter_label.place(relx=0.0, rely=0.10)
        order_filter_sv = ctk.StringVar()
        order_filter_entry = ctk.CTkEntry(master=sub_filterframe, state='disabled', textvariable=order_filter_sv)
        order_filter_entry.place(relx=0.0, rely=0.20, relwidth=0.2)
        sampling_filter_label = ctk.CTkLabel(master=sub_filterframe, text="Sampling frequency (Hz):",
                                             text_color=gp.disabled_label_color)
        sampling_filter_label.place(relx=0.4, rely=0.10)
        sampling_filter_sv = ctk.StringVar()
        sampling_filter_entry = ctk.CTkEntry(master=sub_filterframe, state='disabled', textvariable=sampling_filter_sv)
        sampling_filter_entry.place(relx=0.4, rely=0.20, relwidth=0.2)

        type_filter_label = ctk.CTkLabel(master=sub_filterframe, text="Type: ", text_color=gp.disabled_label_color)
        type_filter_label.place(relx=0, rely=0.35)
        frequency1_filter_label = ctk.CTkLabel(master=sub_filterframe, text="f1 (Hz): ",
                                               text_color=gp.disabled_label_color)
        frequency1_filter_label.place(relx=0.5, rely=0.35)
        frequency2_filter_label = ctk.CTkLabel(master=sub_filterframe, text="f2 (Hz): ",
                                               text_color=gp.disabled_label_color)
        frequency2_filter_label.place(relx=0.8, rely=0.35)
        type_filter_cbox = tk.ttk.Combobox(master=sub_filterframe,
                                           values=["Highpass", "Lowpass", "Bandstop", "Bandpass"],
                                           state="disabled")
        type_filter_cbox.set("Highpass")
        type_filter_cbox.place(relx=0, rely=0.45, relwidth=0.4)
        f1_filter_sv = ctk.StringVar()
        frequency1_filter_entry = ctk.CTkEntry(master=sub_filterframe, state='disabled', textvariable=f1_filter_sv)
        frequency1_filter_entry.place(relx=0.5, rely=0.45, relwidth=0.2)
        f2_filter_sv = ctk.StringVar()
        frequency2_filter_entry = ctk.CTkEntry(master=sub_filterframe, state='disabled', textvariable=f2_filter_sv)
        frequency2_filter_entry.place(relx=0.8, rely=0.45, relwidth=0.2)

        harmonics_label_filter = ctk.CTkLabel(master=sub_filterframe, text="Filter harmonics",
                                              text_color=gp.disabled_label_color)
        harmonics_label_filter.place(relx=0, rely=0.65)

        type_harmonics_label = ctk.CTkLabel(master=sub_filterframe, text="Type:", text_color=gp.disabled_label_color)
        type_harmonics_label.place(relx=0, rely=0.75)
        freq_harmonics_label = ctk.CTkLabel(master=sub_filterframe, text="Frequency (Hz):",
                                            text_color=gp.disabled_label_color)
        freq_harmonics_label.place(relx=0.3, rely=0.75)
        nth_harmonics_label = ctk.CTkLabel(master=sub_filterframe, text="Up to Nth (Hz):",
                                           text_color=gp.disabled_label_color)
        nth_harmonics_label.place(relx=0.7, rely=0.75)

        type_harmonics_cbox = tk.ttk.Combobox(master=sub_filterframe,
                                              values=["All", "Even", "Odd", ],
                                              state="disabled")
        type_harmonics_cbox.set("All")
        type_harmonics_cbox.place(relx=0, rely=0.85, relwidth=0.25)
        freq_hamronics_sv = ctk.StringVar()
        frequency_harmonics_entry = ctk.CTkEntry(master=sub_filterframe, state='disabled',
                                                 textvariable=freq_hamronics_sv)
        frequency_harmonics_entry.place(relx=0.3, rely=0.85, relwidth=0.3)
        nth_hamronics_sv = ctk.StringVar()
        nth_harmonics_entry = ctk.CTkEntry(master=sub_filterframe, state='disabled', textvariable=nth_hamronics_sv)
        nth_harmonics_entry.place(relx=0.7, rely=0.85, relwidth=0.2)

        # ------- FREQUENTIAL PROCESSING -----------
        fft_switch = ctk.CTkSwitch(master=frequential_frame, text="Fast Fourier Transform")
        fft_switch.place(relx=0.0, rely=0)
        sampling_fft_label = ctk.CTkLabel(master=frequential_frame, text="Sampling frequency (Hz):",
                                          text_color=gp.disabled_label_color)
        sampling_fft_label.place(relx=0, rely=0.15)
        sampling_fft_sv = ctk.StringVar()
        sampling_fft_entry = ctk.CTkEntry(master=frequential_frame, state='disabled', textvariable=sampling_fft_sv)
        sampling_fft_entry.place(relx=0, rely=0.25)
        merge_switch = ctk.CTkSwitch(master=frequential_frame, text="Average electrodes signal")
        merge_switch.place(relx=0, rely=0.5)
        smooth_switch = ctk.CTkSwitch(master=frequential_frame, text="Smoothing signal")
        smooth_switch.place(relx=0, rely=0.65)
        smooth_label = ctk.CTkLabel(master=frequential_frame, text="n final values:",
                                    text_color=gp.disabled_label_color)
        smooth_label.place(relx=0, rely=0.75)
        smooth_sv = ctk.StringVar()
        smooth_entry = ctk.CTkEntry(master=frequential_frame, state='disabled', textvariable=smooth_sv)
        smooth_entry.place(relx=0, rely=0.85)

        # ------- EXECUTE PROCESSING ---------------
        random_key_exec_switch = ctk.CTkSwitch(master=exec_frame, text="Add random key to file names")
        random_key_exec_switch.place(relx=0, rely=0)

        timestamp_exec_switch = ctk.CTkSwitch(master=exec_frame, text="Add timestamp to file names")
        timestamp_exec_switch.place(relx=0, rely=0.10)

        keyword_exec_switch = ctk.CTkSwitch(master=exec_frame, text="Add keyword to file names")
        keyword_exec_switch.place(relx=0, rely=0.20)
        keyword_sv = ctk.StringVar()
        keyword_exec_entry = ctk.CTkEntry(master=exec_frame, state='disabled', textvariable=keyword_sv)
        keyword_exec_entry.place(relx=0, rely=0.30, relwidth=0.7)

        make_dataset_switch = ctk.CTkSwitch(master=exec_frame, text="Make resulting files as datasets for learning")
        make_dataset_switch.place(relx=0, rely=0.5)

        save_files_exec_label = ctk.CTkLabel(master=exec_frame, text="Save processed files under:",
                                             text_color=gp.enabled_label_color)
        save_files_exec_label.place(relx=0, rely=0.6)
        save_exec_sv = ctk.StringVar()
        save_exec_entry = ctk.CTkEntry(master=exec_frame, textvariable=save_exec_sv)
        save_exec_entry.place(relx=0, rely=0.7, relwidth=0.7)
        save_exec_button = ctk.CTkButton(master=exec_frame, text="Open")
        save_exec_button.place(relx=0.8, rely=0.7, relwidth=0.15)

        save_model_button = ctk.CTkButton(master=exec_frame, text="Save config", fg_color="lightslategray")
        save_model_button.place(relx=0, rely=0.9, relwidth=0.3, relheight=0.10)
        load_model_button = ctk.CTkButton(master=exec_frame, text="Load config", fg_color="lightslategray")
        load_model_button.place(relx=0.35, rely=0.9, relwidth=0.3, relheight=0.10)
        process_exec_button = ctk.CTkButton(master=exec_frame, fg_color="green", text="Process")
        process_exec_button.place(relx=0.7, rely=0.85, relwidth=0.3, relheight=0.15)

        # ------- CONFIGURE SWITCH COMMANDS -----------------
        sorting_files_switch.configure(
            command=partial(self.controller.main_controller.category_enabling_switch, sorting_files_switch,
                            sorting_frame))
        single_file_switch.configure(
            command=partial(self.controller.main_controller.category_enabling_switch, single_file_switch,
                            single_file_frame))
        raw_mea_switch.configure(
            command=partial(self.controller.main_controller.category_enabling_switch, raw_mea_switch, raw_mea_frame))
        sampling_switch.configure(
            command=partial(self.controller.main_controller.category_enabling_switch, sampling_switch, sampling_frame))
        electrode_switch.configure(
            command=partial(self.controller.main_controller.category_enabling_switch, electrode_switch,
                            select_elec_frame))
        fft_switch.configure(
            command=partial(self.controller.main_controller.category_enabling_switch, fft_switch, frequential_frame))
        keyword_exec_switch.configure(
            command=partial(self.controller.main_controller.modulate_entry_state_by_switch, keyword_exec_switch,
                            keyword_exec_entry))
        name_filter_switch.configure(
            command=partial(self.controller.main_controller.category_enabling_switch, name_filter_switch,
                            sub_filterframe))

        # -------- CONFIGURE BUTTON COMMANDS ----------------
        sorting_button.configure(command=partial(self.select_parent_directory, display_sv=sorting_sv))
        add_include_button.configure(
            command=partial(self.add_subtract_to_include, include_entry, include_textbox, mode='add'))
        subtract_include_button.configure(
            command=partial(self.add_subtract_to_include, include_entry, include_textbox, mode='subtract'))
        add_exclude_button.configure(
            command=partial(self.add_subtract_to_exclude, exclude_entry, exclude_textbox, mode='add'))
        subtract_exclude_button.configure(
            command=partial(self.add_subtract_to_exclude, exclude_entry, exclude_textbox, mode='subtract'))
        add_target_button.configure(
            command=partial(self.add_subtract_target, id_target_entry, rename_target_entry, target_textbox,
                            mode='add'))
        subtract_target_button.configure(
            command=partial(self.add_subtract_target, id_target_entry, rename_target_entry, target_textbox,
                            mode='subtract'))

        single_file_button.configure(command=partial(self.select_single_file, single_file_sv))

        save_exec_button.configure(command=partial(self.select_save_directory, save_exec_sv))

        switch_widgets = {"sorting": sorting_files_switch, "single file": single_file_switch, "raw mea": raw_mea_switch,
                          "select electrodes": electrode_switch, "sampling": sampling_switch,
                          "filter": name_filter_switch,
                          "fft": fft_switch, "average": merge_switch, "smoothing": smooth_switch,
                          "random key": random_key_exec_switch, "timestamp": timestamp_exec_switch,
                          "keyword": keyword_exec_switch, "make dataset": make_dataset_switch}
        cbox_widgets = {"mode electrode": mode_electrode_cbox, "metric electrode": metric_electrode_cbox,
                        "filter type": type_filter_cbox, "harmonic type": type_harmonics_cbox}
        entry_widgets = {"parent directory": sorting_entry, "single file": single_file_entry,
                         "info header": raw_mea_entry, "n electrodes": n_electrodes_entry, "sampling": sampling_entry,
                         "filter order": order_filter_entry, "filter fs": sampling_filter_entry,
                         "first frequency": frequency1_filter_entry,
                         "second frequency": frequency2_filter_entry, "harmonic": frequency_harmonics_entry,
                         "nth harmonic": nth_harmonics_entry,
                         "sampling fft": sampling_fft_entry, "n smoothing": smooth_entry, "keyword": keyword_exec_entry,
                         "save under": save_exec_entry, }
        textbox_widgets = {"to include": include_textbox, "to exclude": exclude_textbox, "targets": target_textbox}
        process_exec_button.configure(command=partial(self.processing, switch_widgets, cbox_widgets,
                                                      entry_widgets))
        save_model_button.configure(command=partial(self.save_model, switch_widgets, cbox_widgets,
                                                    entry_widgets))
        load_model_button.configure(command=partial(self.save_model, switch_widgets, cbox_widgets,
                                                    entry_widgets, textbox_widgets))

    def select_save_directory(self, strvar):
        if self.controller:
            self.controller.select_save_directory(strvar)

    def select_parent_directory(self, strvar):
        if self.controller:
            self.controller.select_parent_directory(strvar)

    def select_single_file(self, strvar):
        if self.controller:
            self.controller.select_single_file(strvar)

    def add_subtract_to_include(self, entry, textbox, mode='add'):
        if self.controller:
            self.controller.add_subtract_to_include(entry, textbox, mode)

    def add_subtract_to_exclude(self, entry, textbox, mode='add'):
        if self.controller:
            self.controller.add_subtract_to_exclude(entry, textbox, mode)

    def add_subtract_target(self, key_entry, value_entry, textbox,
                            mode='add'):  # todo : to processing controller
        if self.controller:
            self.controller.add_subtract_target(key_entry, value_entry, textbox, mode)

    def update_params(self, widgets: dict, ):
        if self.controller:
            self.controller.update_params(widgets)

    def processing(self, switch_widgets, cbox_widgets, entry_widgets):
        if self.controller:
            self.controller.processing(switch_widgets, cbox_widgets, entry_widgets)

    def check_params_validity(self, switch_widgets, cbox_widgets,
                              entry_widgets):
        if self.controller:
            self.controller.check_params_validity(switch_widgets, cbox_widgets, entry_widgets)

    def update_number_of_tasks(self, n_file, n_col, ):
        if self.controller:
            self.controller.update_number_of_tasks(n_file, n_col)

    def save_model(self, switch_widgets, cbox_widgets, entry_widgets):
        if self.controller:
            self.controller.save_model(switch_widgets, cbox_widgets, entry_widgets)

    def load_model(self, switch_widgets, cbox_widgets, entry_widgets, textbox_widgets):
        if self.controller:
            self.controller.load_model(switch_widgets, cbox_widgets, entry_widgets,
                                       textbox_widgets)

    def update_view_from_model(self, switch_widgets, cbox_widgets, entry_widgets,
                               textbox_widgets):
        if self.controller:
            self.controller.update_view_from_model(switch_widgets, cbox_widgets, entry_widgets,
                                                   textbox_widgets)
