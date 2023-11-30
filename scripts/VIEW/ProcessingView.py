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
from scripts.params import resource_path

class ProcessingView(ctk.CTkFrame):
    def __init__(self, app, master, parent_view):
        super().__init__(master=app)
        self.app = app
        self.master = master
        self.parent_view = parent_view
        self.controller = ProcessingController(self)

        self.switches = {}
        self.entries = {}
        self.cbboxes = {}
        self.vars = {}
        self.sliders = {}
        self.buttons = {}
        self.textboxes = {}
        self.image_buttons = {}
        self.labels = {}

        self.frames = {}
        self.step_check = {"1": 2, "2": 2, "3": 2, "4": 2, "5": 2}
        self.content_frame = ctk.CTkFrame(master=self.master)
        self.content_frame.place(relx=0.15, rely=0, relwidth=0.85, relheight=0.9)

        self.manage_processing_tab()

    def manage_processing_tab(self):

        one_ibutton = ImageButton(master=self.master,
                                  img=ctk.CTkImage(dark_image=Image.open(resource_path("data/firelearn_img/1 grey.png")), size=(120, 120)),
                                  command=partial(self.show_content1, ))
        two_ibutton = ImageButton(master=self.master,
                                  img=ctk.CTkImage(dark_image=Image.open(resource_path("data/firelearn_img/2 grey.png")), size=(120, 120)),
                                  command=partial(self.show_content2, ))
        three_ibutton = ImageButton(master=self.master,
                                    img=ctk.CTkImage(dark_image=Image.open(resource_path("data/firelearn_img/3 grey.png")), size=(120, 120)),
                                    command=partial(self.show_content3, ))
        four_ibutton = ImageButton(master=self.master,
                                   img=ctk.CTkImage(dark_image=Image.open(resource_path("data/firelearn_img/4 grey.png")), size=(120, 120)),
                                   command=partial(self.show_content4, ))

        one_ibutton.place(relx=0, rely=0)
        two_ibutton.place(relx=0, rely=0.2)
        three_ibutton.place(relx=0, rely=0.4)
        four_ibutton.place(relx=0, rely=0.6)

        self.image_buttons["1"] = one_ibutton
        self.image_buttons["2"] = two_ibutton
        self.image_buttons["3"] = three_ibutton
        self.image_buttons["4"] = four_ibutton

        content_1_frame = ctk.CTkFrame(master=self.content_frame, )
        content_2_frame = ctk.CTkFrame(master=self.content_frame, )
        content_3_frame = ctk.CTkFrame(master=self.content_frame, )
        content_4_frame = ctk.CTkFrame(master=self.content_frame, )
        self.frames["content 1"] = content_1_frame
        self.frames["content 2"] = content_2_frame
        self.frames["content 3"] = content_3_frame
        self.frames["content 4"] = content_4_frame
        self.generate_content1()
        self.generate_content2()
        self.generate_content3()
        self.generate_content4()
        self.show_content1()

        check_all_button = ctk.CTkButton(master=self.master, text="Check all steps",
                                         command=self.controller.check_params_validity,
                                         fg_color="green")
        save_model_button = ctk.CTkButton(master=self.master, text="Save config", fg_color="lightslategray",
                                          command=self.save_config)
        load_model_button = ctk.CTkButton(master=self.master, text="Load config", fg_color="lightslategray",
                                          command=self.load_model)
        process_exec_button = ctk.CTkButton(master=self.master, fg_color="green", text="Process",
                                            command=self.processing)

        check_all_button.place(anchor=tk.S, relx=0.25, rely=0.95)
        save_model_button.place(anchor=tk.S, relx=0.35, rely=0.95, )
        load_model_button.place(anchor=tk.S, relx=0.45, rely=0.95, )
        process_exec_button.place(anchor=tk.S, relx=0.55, rely=0.95, relheight=0.05)

    def generate_content1(self):

        content_1_frame = self.frames["content 1"]

        # ------- SORTING FILES -----------
        sorting_files_switch = ctk.CTkSwitch(master=content_1_frame, text="Sorting multiple files")
        sorting_label = ctk.CTkLabel(master=content_1_frame, text="Path to parent directory:",
                                     text_color=gp.enabled_label_color)

        sorting_sv = ctk.StringVar()
        sorting_entry = ErrEntry(master=content_1_frame, state='disabled', textvariable=sorting_sv)
        sorting_button = ctk.CTkButton(master=content_1_frame, text="Open", state='normal')

        sorting_helper = Helper(master=content_1_frame, event_key="#sorting-multiple-files")

        to_include_label = ctk.CTkLabel(master=content_1_frame, text="To include:",
                                        text_color=gp.enabled_label_color)
        include_sv = ctk.StringVar()
        include_entry = ErrEntry(master=content_1_frame, state='normal', textvariable=include_sv)
        add_include_button = ctk.CTkButton(master=content_1_frame, text="+", width=25, height=25, state='normal')
        subtract_include_button = ctk.CTkButton(master=content_1_frame, text="-", width=25, height=25,
                                                state='normal')
        include_textbox = ctk.CTkTextbox(master=content_1_frame, corner_radius=10, state='disabled')

        to_exclude_label = ctk.CTkLabel(master=content_1_frame, text="To exclude:",
                                        text_color=gp.enabled_label_color)
        exclude_sv = ctk.StringVar()
        exclude_entry = ErrEntry(master=content_1_frame, state='normal', textvariable=exclude_sv)
        add_exclude_button = ctk.CTkButton(master=content_1_frame, text="+", width=25, height=25, state='normal')
        subtract_exclude_button = ctk.CTkButton(master=content_1_frame, text="-", width=25, height=25,
                                                state='normal')
        exclude_textbox = ctk.CTkTextbox(master=content_1_frame, corner_radius=10, state='disabled')

        key_target_label = ctk.CTkLabel(master=content_1_frame, text="Target key:",
                                        text_color=gp.enabled_label_color)
        value_target_label = ctk.CTkLabel(master=content_1_frame, text="Target value:",
                                          text_color=gp.enabled_label_color)
        id_target_sv = ctk.StringVar()
        id_target_entry = ErrEntry(master=content_1_frame, state='normal', textvariable=id_target_sv)
        rename_target_sv = ctk.StringVar()
        rename_target_entry = ErrEntry(master=content_1_frame, state='normal', textvariable=rename_target_sv)
        add_target_button = ctk.CTkButton(master=content_1_frame, text="+", width=25, height=25, state='normal')
        subtract_target_button = ctk.CTkButton(master=content_1_frame, text="-", width=25, height=25,
                                               state='normal')
        target_textbox = ctk.CTkTextbox(master=content_1_frame, corner_radius=10, state='disabled')

        # -------- SINGLE FILE ------------
        single_file_helper = Helper(master=content_1_frame, event_key="#single-file-analysis")

        single_file_switch = ctk.CTkSwitch(master=content_1_frame, text="Single file analysis")
        single_file_label = ctk.CTkLabel(master=content_1_frame, text="Path to file:",
                                         text_color=gp.enabled_label_color)
        single_file_sv = ctk.StringVar()
        single_file_entry = ErrEntry(master=content_1_frame, state='disabled', textvariable=single_file_sv)
        single_file_button = ctk.CTkButton(master=content_1_frame, text="Open", state='normal')

        # ----- EXECUTE
        exec_helper = Helper(master=content_1_frame, event_key="#post-processing")
        random_key_exec_switch = ctk.CTkSwitch(master=content_1_frame, text="Add random key to file names")
        timestamp_exec_switch = ctk.CTkSwitch(master=content_1_frame, text="Add timestamp to file names")
        keyword_exec_switch = ctk.CTkSwitch(master=content_1_frame, text="Add keyword to file names")
        keyword_sv = ctk.StringVar()
        keyword_entry = ErrEntry(master=content_1_frame, state='normal', textvariable=keyword_sv)
        make_dataset_switch = ctk.CTkSwitch(master=content_1_frame,
                                            text="Make resulting files as datasets for learning")
        save_files_exec_label = ctk.CTkLabel(master=content_1_frame, text="Save processed files under:",
                                             text_color=gp.enabled_label_color)
        save_exec_sv = ctk.StringVar()
        save_entry = ErrEntry(master=content_1_frame, textvariable=save_exec_sv, state='disabled')
        save_exec_button = ctk.CTkButton(master=content_1_frame, text="Open")

        # ------- MANAGE WIDGETS
        sorting_helper.place(anchor=ctk.NE, relx=1, rely=0)

        sorting_files_switch.place(relx=0, rely=0)
        sorting_label.place(relx=0, rely=0.05)
        sorting_entry.place_errentry(relx=0, rely=0.1, relwidth=0.6, relpadx=50)
        sorting_button.place(relx=0.6, rely=0.1, relwidth=0.10)

        to_include_label.place(relx=0.0, rely=0.16)
        include_entry.place_errentry(relx=0.0, rely=0.2, relwidth=0.10)
        add_include_button.place(relx=0.12, rely=0.2)
        subtract_include_button.place(relx=0.15, rely=0.2)
        include_textbox.place(relx=0.0, rely=0.25, relwidth=0.2, relheight=0.15)

        to_exclude_label.place(relx=0.3, rely=0.16)
        exclude_entry.place_errentry(relx=0.3, rely=0.2, relwidth=0.10)
        add_exclude_button.place(relx=0.42, rely=0.2)
        subtract_exclude_button.place(relx=0.45, rely=0.2)
        exclude_textbox.place(relx=0.3, rely=0.25, relwidth=0.2, relheight=0.15)

        key_target_label.place(relx=0.6, rely=0.16)
        value_target_label.place(relx=0.8, rely=0.16)
        id_target_entry.place_errentry(relx=0.6, rely=0.2, relwidth=0.1)
        rename_target_entry.place_errentry(relx=0.8, rely=0.2, relwidth=0.1)
        add_target_button.place(relx=0.93, rely=0.2)
        subtract_target_button.place(relx=0.96, rely=0.2)
        target_textbox.place(relx=0.6, rely=0.25, relwidth=0.4, relheight=0.15)

        single_file_helper.place(anchor=ctk.NE, relx=1, rely=0.45)
        single_file_switch.place(relx=0, rely=0.45)
        single_file_label.place(relx=0, rely=0.5)
        single_file_entry.place_errentry(relx=0, rely=0.55, relwidth=0.6, relpady=0.04)
        single_file_button.place(relx=0.6, rely=0.55, relwidth=0.1)

        exec_helper.place(anchor=ctk.NE, relx=1, rely=0.65)
        random_key_exec_switch.place(relx=0, rely=0.65)
        timestamp_exec_switch.place(relx=0, rely=0.75)
        keyword_exec_switch.place(relx=0, rely=0.85)
        keyword_entry.place_errentry(relx=0, rely=0.90, relwidth=0.4, relpady=0.04)
        make_dataset_switch.place(relx=0.5, rely=0.65)
        save_files_exec_label.place(relx=0.5, rely=0.75)
        save_entry.place_errentry(relx=0.5, rely=0.8, relwidth=0.4, relpady=0.05)
        save_exec_button.place(relx=0.9, rely=0.8, relwidth=0.1)

        self.switches["sorting"] = sorting_files_switch
        self.vars["sorting"] = sorting_sv
        self.entries["sorting"] = sorting_entry
        self.switches["single file"] = single_file_switch
        self.vars["single file"] = single_file_sv
        self.entries["single file"] = single_file_entry
        self.vars["key target"] = id_target_sv
        self.vars["value target"] = rename_target_sv
        self.entries["key target"] = id_target_entry
        self.entries["value target"] = rename_target_entry
        self.textboxes["targets"] = target_textbox
        self.vars["to exclude"] = exclude_sv
        self.entries["to exclude"] = exclude_entry
        self.textboxes["to exclude"] = exclude_textbox
        self.vars["to include"] = include_sv
        self.entries["to include"] = include_entry
        self.textboxes["to include"] = include_textbox
        self.switches["random key"] = random_key_exec_switch
        self.switches["timestamp"] = timestamp_exec_switch
        self.switches["keyword"] = keyword_exec_switch
        self.switches["make dataset"] = make_dataset_switch
        self.entries["keyword"] = keyword_entry
        self.entries["save files"] = save_entry
        self.vars["keyword"] = keyword_sv
        self.vars["save files"] = save_exec_sv
        # ------------ CONFIGURE

        sorting_button.configure(command=partial(self.select_parent_directory, sorting_sv))
        add_include_button.configure(
            command=partial(self.add_subtract_to_include, entry=include_entry, textbox=include_textbox, mode='add'))
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
        keyword_exec_switch.configure(
            command=partial(self.controller.modulate_entry_state_by_switch, keyword_exec_switch,
                            keyword_entry))

        save_exec_button.configure(command=partial(self.select_save_directory, save_exec_sv))

        single_file_button.configure(command=partial(self.select_single_file, single_file_sv))

        # ---- ENTRY VALIDATION
        sorting_entry.configure(validate='focus',
                                validatecommand=(self.register(partial(self.parent_view.is_valid_directory, sorting_entry)), '%P'))
        single_file_entry.configure(validate='focus',
                                    validatecommand=(self.register(partial(self.parent_view.is_valid_directory, single_file_entry)), '%P'))
        save_entry.configure(validate='focus',
                             validatecommand=(self.register(partial(self.parent_view.is_valid_directory, save_entry)), '%P'))
        keyword_entry.configure(validate='focus',
                                     validatecommand=(self.register(partial(self.parent_view.has_forbidden_characters, keyword_entry)), '%P'))

        # ------ ENTRY BINDING
        include_entry.bind('<Return>',
                           lambda event: self.add_subtract_to_include(include_entry, include_textbox, 'add'))
        include_entry.bind('<Control-BackSpace>',
                           lambda event: self.add_subtract_to_include(include_entry, include_textbox, 'subtract'))
        exclude_entry.bind('<Return>',
                           lambda event: self.add_subtract_to_exclude(exclude_entry, exclude_textbox, mode='add'))
        exclude_entry.bind('<Control-BackSpace>',
                           lambda event: self.add_subtract_to_exclude(exclude_entry, exclude_textbox, mode='subtract'))
        id_target_entry.bind('<Return>',
                             lambda event: self.add_subtract_target(id_target_entry, rename_target_entry,
                                                                    target_textbox,
                                                                    'add'))
        id_target_entry.bind('<Control-BackSpace>',
                             lambda event: self.add_subtract_target(id_target_entry, rename_target_entry,
                                                                    target_textbox,
                                                                    'subtract'))
        rename_target_entry.bind('<Return>',
                                 lambda event: self.add_subtract_target(id_target_entry, rename_target_entry,
                                                                        target_textbox,
                                                                        'add'))

    def generate_content2(self):

        content_2_frame = self.frames["content 2"]

        # ------- RAW MEA ------------------
        raw_mea_helper = Helper(master=content_2_frame, event_key="#using-raw-mea-recordings")

        raw_mea_switch = ctk.CTkSwitch(master=content_2_frame, text="Raw MEA recording files", )
        raw_mea_label = ctk.CTkLabel(master=content_2_frame, text="Size of info headers: ",
                                     text_color=gp.enabled_label_color)
        raw_mea_sv = ctk.StringVar()
        raw_mea_entry = ErrEntry(master=content_2_frame, state='normal', textvariable=raw_mea_sv)

        # --------- SELECT ELECTRODES -------
        select_elec_helper = Helper(master=content_2_frame, event_key="#selecting-electrodes")

        electrode_switch = ctk.CTkSwitch(master=content_2_frame, text="Select electrodes", )
        electrode_mode_label = ctk.CTkLabel(master=content_2_frame, text="mode: ", text_color=gp.enabled_label_color)

        electrode_metric_label = ctk.CTkLabel(master=content_2_frame, text="metric: ",
                                              text_color=gp.enabled_label_color)
        n_electrode_label = ctk.CTkLabel(master=content_2_frame, text="n electrodes: ",
                                         text_color=gp.enabled_label_color)
        mode_electrode_cbox = tk.ttk.Combobox(master=content_2_frame, values=["None", "max", ], state='readonly')
        mode_electrode_cbox.set("None")
        metric_electrode_cbox = tk.ttk.Combobox(master=content_2_frame, values=["None", "std", ], state='readonly')
        metric_electrode_cbox.set("None")
        n_electrode_sv = ctk.StringVar()
        n_electrodes_entry = ErrEntry(master=content_2_frame, state='normal', textvariable=n_electrode_sv)

        # ------- SAMPLING ------------------------
        sampling_helper = Helper(master=content_2_frame, event_key="#recordings-down-sampling")

        sampling_switch = ctk.CTkSwitch(master=content_2_frame, text="Down sampling recordings")
        sampling_divide_label = ctk.CTkLabel(master=content_2_frame, text="Divide recording into ",
                                             text_color=gp.enabled_label_color)
        sampling_sv = ctk.StringVar()
        sampling_entry = ErrEntry(master=content_2_frame, state='normal', textvariable=sampling_sv)
        sampling_pieces_label = ctk.CTkLabel(master=content_2_frame, text="pieces", text_color=gp.enabled_label_color)

        # ------ MANAGING WIDGETS

        raw_mea_helper.place(anchor=ctk.NE, relx=1, rely=0)
        raw_mea_switch.place(relx=0.0, rely=0)
        raw_mea_label.place(relx=0.0, rely=0.1, )
        raw_mea_entry.place_errentry(relx=0.2, rely=0.2, relwidth=0.5)

        select_elec_helper.place(anchor=ctk.NE, relx=1, rely=0.3)
        electrode_switch.place(relx=0.0, rely=0.3)
        electrode_mode_label.place(relx=0.0, rely=0.4, )
        electrode_metric_label.place(relx=0.33, rely=0.4, )
        n_electrode_label.place(relx=0.66, rely=0.4, )
        mode_electrode_cbox.place(relx=0.0, rely=0.5, relwidth=0.3)
        metric_electrode_cbox.place(relx=0.33, rely=0.5, relwidth=0.3)
        n_electrodes_entry.place_errentry(relx=0.66, rely=0.5, relwidth=0.2)

        sampling_helper.place(anchor=ctk.NE, relx=1, rely=0.6)
        sampling_switch.place(relx=0, rely=0.6)
        sampling_divide_label.place(relx=0, rely=0.7)
        sampling_entry.place_errentry(relx=0.40, rely=0.7, relwidth=0.2)
        sampling_pieces_label.place(relx=0.7, rely=0.7)

        self.switches["raw mea"] = raw_mea_switch
        self.vars["raw mea"] = raw_mea_sv
        self.entries["raw mea"] = raw_mea_entry
        self.switches["select electrodes"] = electrode_switch
        self.cbboxes["select electrode mode"] = mode_electrode_cbox
        self.cbboxes["select electrode metric"] = metric_electrode_cbox
        self.vars["n electrodes"] = n_electrode_sv
        self.entries["n electrodes"] = n_electrodes_entry
        self.switches["select electrodes"] = electrode_switch
        self.cbboxes["select electrode mode"] = mode_electrode_cbox
        self.cbboxes["select electrode metric"] = metric_electrode_cbox
        self.vars["n electrodes"] = n_electrode_sv
        self.entries["n electrodes"] = n_electrodes_entry
        self.switches["select electrodes"] = electrode_switch
        self.cbboxes["select electrode mode"] = mode_electrode_cbox
        self.cbboxes["select electrode metric"] = metric_electrode_cbox
        self.vars["n electrodes"] = n_electrode_sv
        self.entries["n electrodes"] = n_electrodes_entry
        self.switches["select electrodes"] = electrode_switch
        self.cbboxes["select electrode mode"] = mode_electrode_cbox
        self.cbboxes["select electrode metric"] = metric_electrode_cbox
        self.vars["n electrodes"] = n_electrode_sv
        self.entries["n electrodes"] = n_electrodes_entry
        self.switches["sampling"] = sampling_switch
        self.entries["sampling"] = sampling_entry
        self.vars["sampling"] = sampling_sv

        # ------ CONFIGURE

        raw_mea_entry.configure(validate='focus',
                                validatecommand=(self.register(partial(self.parent_view.is_positive_int_or_emtpy, raw_mea_entry)), '%P'))
        n_electrodes_entry.configure(validate='focus',
                                     validatecommand=(self.register(partial(self.parent_view.is_positive_int_or_emtpy, n_electrodes_entry)), '%P'))
        sampling_entry.configure(validate='focus',
                                 validatecommand=(self.register(partial(self.parent_view.is_positive_int_or_emtpy, sampling_entry)), '%P'))


    def generate_content3(self):
        filter_frame = ctk.CTkScrollableFrame(master=self.frames["content 3"], )
        filter_frame.place(relwidth=0.9, relheight=0.9, rely=0.05, relx=0.05)
        filter_frame.grid_columnconfigure(0, weight=1)

        # ------- FILTERING ------------------------
        filter_helper = Helper(master=filter_frame, event_key="#filtering")

        sub_filterframe = ctk.CTkFrame(master=filter_frame, height=280)
        sub_filterframe.grid(row=0, column=0, sticky=ctk.NSEW)

        name_filter_switch = ctk.CTkSwitch(master=sub_filterframe, text="Filter 1")

        order_filter_label = ctk.CTkLabel(master=sub_filterframe, text="Order: ", text_color=gp.enabled_label_color)
        order_filter_sv = ctk.StringVar()
        order_filter_entry = ErrEntry(master=sub_filterframe, state='normal', textvariable=order_filter_sv)
        sampling_filter_label = ctk.CTkLabel(master=sub_filterframe, text="Sampling frequency (Hz):",
                                             text_color=gp.enabled_label_color)
        sampling_filter_sv = ctk.StringVar()
        sampling_filter_entry = ErrEntry(master=sub_filterframe, state='normal', textvariable=sampling_filter_sv)

        type_filter_label = ctk.CTkLabel(master=sub_filterframe, text="Type: ", text_color=gp.enabled_label_color)
        frequency1_filter_label = ctk.CTkLabel(master=sub_filterframe, text="f1 (Hz): ",
                                               text_color=gp.enabled_label_color)
        frequency2_filter_label = ctk.CTkLabel(master=sub_filterframe, text="f2 (Hz): ",
                                               text_color=gp.enabled_label_color)
        type_filter_cbox = tk.ttk.Combobox(master=sub_filterframe,
                                           values=["None", "Highpass", "Lowpass", "Bandstop", "Bandpass"],
                                           state="readonly")
        type_filter_cbox.set("None")
        f1_filter_sv = ctk.StringVar()
        frequency1_filter_entry = ErrEntry(master=sub_filterframe, state='normal', textvariable=f1_filter_sv)
        f2_filter_sv = ctk.StringVar()
        frequency2_filter_entry = ErrEntry(master=sub_filterframe, state='normal', textvariable=f2_filter_sv)
        harmonics_label_filter = ctk.CTkLabel(master=sub_filterframe, text="Filter harmonics",
                                              text_color=gp.enabled_label_color)
        type_harmonics_label = ctk.CTkLabel(master=sub_filterframe, text="Type:", text_color=gp.enabled_label_color)
        freq_harmonics_label = ctk.CTkLabel(master=sub_filterframe, text="Frequency (Hz):",
                                            text_color=gp.enabled_label_color)
        nth_harmonics_label = ctk.CTkLabel(master=sub_filterframe, text="Up to Nth (Hz):",
                                           text_color=gp.enabled_label_color)
        type_harmonics_cbox = tk.ttk.Combobox(master=sub_filterframe,
                                              values=["Non", "All", "Even", "Odd", ],
                                              state="readonly")
        type_harmonics_cbox.set("None")
        freq_hamronics_sv = ctk.StringVar()
        frequency_harmonics_entry = ErrEntry(master=sub_filterframe, state='normal',
                                             textvariable=freq_hamronics_sv)
        nth_hamronics_sv = ctk.StringVar()
        nth_harmonics_entry = ErrEntry(master=sub_filterframe, state='normal', textvariable=nth_hamronics_sv)

        type_filter_cbox.place(relx=0, rely=0.45, relwidth=0.4)
        filter_helper.place(anchor=ctk.NE, relx=1, rely=0)
        sampling_filter_label.place(relx=0.4, rely=0.10)
        name_filter_switch.place(relx=0, rely=0)
        order_filter_label.place(relx=0.0, rely=0.10)
        order_filter_entry.place_errentry(relx=0.0, rely=0.20, relwidth=0.2)
        sampling_filter_entry.place_errentry(relx=0.4, rely=0.20, relwidth=0.2)
        type_filter_label.place(relx=0, rely=0.35)
        frequency1_filter_label.place(relx=0.5, rely=0.35)
        frequency2_filter_label.place(relx=0.8, rely=0.35)
        frequency1_filter_entry.place_errentry(relx=0.5, rely=0.45, relwidth=0.2)
        frequency2_filter_entry.place_errentry(relx=0.8, rely=0.45, relwidth=0.2)
        harmonics_label_filter.place(relx=0, rely=0.65)
        type_harmonics_label.place(relx=0, rely=0.75)
        freq_harmonics_label.place(relx=0.3, rely=0.75)
        nth_harmonics_label.place(relx=0.7, rely=0.75)
        type_harmonics_cbox.place(relx=0, rely=0.85, relwidth=0.25)
        frequency_harmonics_entry.place_errentry(relx=0.3, rely=0.85, relwidth=0.3)
        nth_harmonics_entry.place_errentry(relx=0.7, rely=0.85, relwidth=0.2)

        self.switches["filter"] = name_filter_switch
        self.entries["filter order"] = order_filter_entry
        self.vars["filter order"] = order_filter_sv
        self.entries["filter sampling"] = sampling_filter_entry
        self.vars["filter sampling"] = sampling_filter_sv
        self.entries["first frequency"] = frequency1_filter_entry
        self.entries["second frequency"] = frequency2_filter_entry
        self.cbboxes["filter type"] = type_filter_cbox
        self.cbboxes["harmonic type"] = type_harmonics_cbox
        self.vars["harmonic frequency"] = freq_hamronics_sv
        self.entries["harmonic frequency"] = frequency_harmonics_entry
        self.vars["nth harmonic"] = nth_hamronics_sv
        self.entries["nth harmonic"] = nth_harmonics_entry

        # ----------- CONFIGURE

        order_filter_entry.configure(validate='focus',
                                 validatecommand=(self.register(partial(self.parent_view.is_positive_int_or_emtpy, order_filter_entry)), '%P'))
        sampling_filter_entry.configure(validate='focus',
                                 validatecommand=(self.register(partial(self.parent_view.is_positive_int_or_emtpy, sampling_filter_entry)), '%P'))
        frequency1_filter_entry.configure(validate='focus',
                                 validatecommand=(self.register(partial(self.parent_view.is_positive_int_or_emtpy, frequency1_filter_entry)), '%P'))
        frequency2_filter_entry.configure(validate='focus',
                                 validatecommand=(self.register(partial(self.parent_view.is_positive_int_or_emtpy, frequency2_filter_entry)), '%P'))
        frequency_harmonics_entry.configure(validate='focus',
                                 validatecommand=(self.register(partial(self.parent_view.is_positive_int_or_emtpy, frequency_harmonics_entry)), '%P'))
        nth_harmonics_entry.configure(validate='focus',
                                 validatecommand=(self.register(partial(self.parent_view.is_positive_int_or_emtpy, nth_harmonics_entry)), '%P'))


    def generate_content4(self):
        frequential_frame = self.frames["content 4"]

        # ------- FREQUENTIAL PROCESSING -----------
        frequential_helper = Helper(master=frequential_frame, event_key="#fast-fourier-transform")
        fft_switch = ctk.CTkSwitch(master=frequential_frame, text="Fast Fourier Transform")
        sampling_fft_label = ctk.CTkLabel(master=frequential_frame, text="Sampling frequency (Hz):",
                                          text_color=gp.enabled_label_color)
        sampling_fft_sv = ctk.StringVar()
        sampling_fft_entry = ErrEntry(master=frequential_frame, state='normal', textvariable=sampling_fft_sv)
        merge_switch = ctk.CTkSwitch(master=frequential_frame, text="Average electrodes signal")
        smooth_switch = ctk.CTkSwitch(master=frequential_frame, text="Smoothing signal")
        smooth_label = ctk.CTkLabel(master=frequential_frame, text="n final values:",
                                    text_color=gp.enabled_label_color)
        smooth_sv = ctk.StringVar()
        smooth_entry = ErrEntry(master=frequential_frame, state='normal', textvariable=smooth_sv)

        frequential_helper.place(anchor=ctk.NE, relx=1, rely=0)
        fft_switch.place(relx=0.0, rely=0)
        sampling_fft_label.place(relx=0, rely=0.15)
        merge_switch.place(relx=0, rely=0.5)
        smooth_label.place(relx=0, rely=0.75)
        smooth_switch.place(relx=0, rely=0.65)
        sampling_fft_entry.place_errentry(relx=0, rely=0.25)
        smooth_entry.place_errentry(relx=0, rely=0.85)

        self.switches["fft"] = fft_switch
        self.vars["fft sampling"] = sampling_fft_sv
        self.entries["fft sampling"] = sampling_fft_entry
        self.switches["merge"] = merge_switch
        self.switches["smoothing"] = smooth_switch
        self.vars["smoothing"] = smooth_sv
        self.entries["smoothing"] = smooth_entry

        smooth_entry.configure(validate='focus',
                                 validatecommand=(self.register(partial(self.parent_view.is_positive_int_or_emtpy, smooth_entry)), '%P'))
        sampling_fft_entry.configure(validate='focus',
                                 validatecommand=(self.register(partial(self.parent_view.is_positive_int_or_emtpy, sampling_fft_entry)), '%P'))


    def show_content1(self, *args):
        self.select_processing_step(1)

        self.frames['content 2'].place_forget()
        self.frames['content 3'].place_forget()
        self.frames['content 4'].place_forget()
        self.frames["content 1"].place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)

    def show_content2(self, *args):
        self.select_processing_step(2)

        self.frames['content 1'].place_forget()
        self.frames['content 3'].place_forget()
        self.frames['content 4'].place_forget()
        self.frames["content 2"].place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)

    def show_content3(self, *args):
        self.select_processing_step(3)

        self.frames['content 1'].place_forget()
        self.frames['content 2'].place_forget()
        self.frames['content 4'].place_forget()
        self.frames["content 3"].place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)

    def show_content4(self, *args):
        self.select_processing_step(4)

        self.frames['content 1'].place_forget()
        self.frames['content 2'].place_forget()
        self.frames['content 3'].place_forget()
        self.frames["content 4"].place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)

    def show_content5(self, *args):
        self.select_processing_step(5)

        self.frames['content 1'].place_forget()
        self.frames['content 2'].place_forget()
        self.frames['content 3'].place_forget()
        self.frames['content 4'].place_forget()
        self.frames["content 5"].place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)

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

    def select_processing_step(self, step):
        for i in range(1, 5):
            if self.step_check[str(i)] == 2:
                img = ctk.CTkImage(dark_image=Image.open(resource_path(f"data/firelearn_img/{i} grey.png")), size=(120, 120))
                self.image_buttons[str(i)].configure(image=img)
            if self.step_check[str(i)] == 1:
                img = ctk.CTkImage(dark_image=Image.open(resource_path(f"data/firelearn_img/{i} green.png")), size=(120, 120))
                self.image_buttons[str(i)].configure(image=img)
            if self.step_check[str(i)] == 0:
                img = ctk.CTkImage(dark_image=Image.open(resource_path(f"data/firelearn_img/{i} red.png")), size=(120, 120))
                self.image_buttons[str(i)].configure(image=img)
            if str(i) == str(step):
                img = ctk.CTkImage(dark_image=Image.open(resource_path(f"data/firelearn_img/{i} blue.png")), size=(120, 120))
                self.image_buttons[str(i)].configure(image=img)
