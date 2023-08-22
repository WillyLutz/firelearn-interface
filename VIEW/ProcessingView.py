import tkinter as tk
from functools import partial
from tkinter import ttk

import customtkinter as ctk

import VIEW.graphic_params as gp
from CONTROLLER.ProcessingController import ProcessingController
from WIDGETS.Helper import Helper
from PIL import ImageTk, Image

from WIDGETS.ImageButton import ImageButton


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
        self.strvars = {}
        self.buttons = {}
        self.textboxes = {}
        self.image_buttons = {}

        self.frames = {}
        self.step_check = {"1": 2, "2": 2, "3": 2, "4": 2, "5": 2}
        self.content_frame = ctk.CTkFrame(master=self.master)
        self.content_frame.place(relx=0.15, rely=0, relwidth=0.55, relheight=0.9)

        self.manage_processing_tab()

    def manage_processing_tab(self):

        one_ibutton = ImageButton(master=self.master,
                                  img=ctk.CTkImage(dark_image=Image.open("data/1 grey.png"), size=(120, 120)),
                                  command=partial(self.show_content1, ))
        two_ibutton = ImageButton(master=self.master,
                                  img=ctk.CTkImage(dark_image=Image.open("data/2 grey.png"), size=(120, 120)),
                                  command=partial(self.show_content2, ))
        three_ibutton = ImageButton(master=self.master,
                                    img=ctk.CTkImage(dark_image=Image.open("data/3 grey.png"), size=(120, 120)),
                                    command=partial(self.show_content3, ))
        four_ibutton = ImageButton(master=self.master,
                                   img=ctk.CTkImage(dark_image=Image.open("data/4 grey.png"), size=(120, 120)),
                                   command=partial(self.show_content4, ))
        five_ibutton = ImageButton(master=self.master,
                                   img=ctk.CTkImage(dark_image=Image.open("data/5 grey.png"), size=(120, 120)),
                                   command=partial(self.show_content5, ))

        one_ibutton.place(relx=0, rely=0)
        two_ibutton.place(relx=0, rely=0.2)
        three_ibutton.place(relx=0, rely=0.4)
        four_ibutton.place(relx=0, rely=0.6)
        five_ibutton.place(relx=0, rely=0.8)

        self.image_buttons["1"] = one_ibutton
        self.image_buttons["2"] = two_ibutton
        self.image_buttons["3"] = three_ibutton
        self.image_buttons["4"] = four_ibutton
        self.image_buttons["5"] = five_ibutton

        content_1_frame = ctk.CTkFrame(master=self.content_frame, )
        content_2_frame = ctk.CTkFrame(master=self.content_frame, )
        content_3_frame = ctk.CTkFrame(master=self.content_frame, )
        content_4_frame = ctk.CTkFrame(master=self.content_frame, )
        content_5_frame = ctk.CTkFrame(master=self.content_frame, )
        self.frames["content 1"] = content_1_frame
        self.frames["content 2"] = content_2_frame
        self.frames["content 3"] = content_3_frame
        self.frames["content 4"] = content_4_frame
        self.frames["content 5"] = content_5_frame
        self.generate_content1()
        self.generate_content2()
        self.generate_content3()
        self.generate_content4()
        self.generate_content5()
        self.show_content1()

        check_all_button = ctk.CTkButton(master=self.master, text="Check all steps", command=self.check_all_steps,
                                         fg_color="green")
        check_all_button.place(anchor=tk.S, relx=0.5, rely=1)

    def generate_content1(self):
        check_content_button = ctk.CTkButton(master=self.frames["content 1"], text="Check step", fg_color="green",
                                             command=partial(self.check_processing_step_validity, "1"))
        check_content_button.place(anchor=tk.SE, relx=1, rely=1)

        content_1_frame = self.frames["content 1"]

        # ------- SORTING FILES -----------
        sorting_files_switch = ctk.CTkSwitch(master=content_1_frame, text="Sorting multiple files")
        sorting_label = ctk.CTkLabel(master=content_1_frame, text="Path to parent directory:",
                                     text_color=gp.disabled_label_color)

        sorting_sv = ctk.StringVar()
        sorting_entry = ctk.CTkEntry(master=content_1_frame, state='disabled', textvariable=sorting_sv)
        sorting_button = ctk.CTkButton(master=content_1_frame, text="Open", state='disabled')

        sorting_helper = Helper(master=content_1_frame, event_key="sorting")

        to_include_label = ctk.CTkLabel(master=content_1_frame, text="To include:",
                                        text_color=gp.disabled_label_color)
        include_sv = ctk.StringVar()
        include_entry = ctk.CTkEntry(master=content_1_frame, state='disabled', textvariable=include_sv)
        add_include_button = ctk.CTkButton(master=content_1_frame, text="+", width=25, height=25, state='disabled')
        subtract_include_button = ctk.CTkButton(master=content_1_frame, text="-", width=25, height=25,
                                                state='disabled')
        include_textbox = ctk.CTkTextbox(master=content_1_frame, corner_radius=10, state='disabled')

        to_exclude_label = ctk.CTkLabel(master=content_1_frame, text="To exclude:",
                                        text_color=gp.disabled_label_color)
        exclude_sv = ctk.StringVar()
        exclude_entry = ctk.CTkEntry(master=content_1_frame, state='disabled', textvariable=exclude_sv)
        add_exclude_button = ctk.CTkButton(master=content_1_frame, text="+", width=25, height=25, state='disabled')
        subtract_exclude_button = ctk.CTkButton(master=content_1_frame, text="-", width=25, height=25,
                                                state='disabled')
        exclude_textbox = ctk.CTkTextbox(master=content_1_frame, corner_radius=10, state='disabled')

        key_target_label = ctk.CTkLabel(master=content_1_frame, text="Target key:",
                                        text_color=gp.disabled_label_color)
        value_target_label = ctk.CTkLabel(master=content_1_frame, text="Target value:",
                                          text_color=gp.disabled_label_color)
        id_target_sv = ctk.StringVar()
        id_target_entry = ctk.CTkEntry(master=content_1_frame, state='disabled', textvariable=id_target_sv)
        rename_target_sv = ctk.StringVar()
        rename_target_entry = ctk.CTkEntry(master=content_1_frame, state='disabled', textvariable=rename_target_sv)
        add_target_button = ctk.CTkButton(master=content_1_frame, text="+", width=25, height=25, state='disabled')
        subtract_target_button = ctk.CTkButton(master=content_1_frame, text="-", width=25, height=25,
                                               state='disabled')
        target_textbox = ctk.CTkTextbox(master=content_1_frame, corner_radius=10, state='disabled')

        # -------- SINGLE FILE ------------
        single_file_helper = Helper(master=content_1_frame, event_key="single file")

        single_file_switch = ctk.CTkSwitch(master=content_1_frame, text="Single file analysis")
        single_file_label = ctk.CTkLabel(master=content_1_frame, text="Path to file:",
                                         text_color=gp.disabled_label_color)
        single_file_sv = ctk.StringVar()
        single_file_entry = ctk.CTkEntry(master=content_1_frame, state='disabled', textvariable=single_file_sv)
        single_file_button = ctk.CTkButton(master=content_1_frame, text="Open", state='disabled')

        # ------- MANAGE WIDGETS
        sorting_helper.place(anchor=ctk.NE, relx=1, rely=0)

        sorting_files_switch.place(relx=0, rely=0)
        sorting_label.place(relx=0, rely=0.05)
        sorting_entry.place(relx=0, rely=0.1, relwidth=0.8)
        sorting_button.place(relx=0.8, rely=0.1, relwidth=0.15)

        to_include_label.place(relx=0.0, rely=0.2)
        include_entry.place(relx=0.10, rely=0.2, relwidth=0.20)
        add_include_button.place(relx=0.35, rely=0.2)
        subtract_include_button.place(relx=0.40, rely=0.2)
        include_textbox.place(relx=0.0, rely=0.25, relwidth=0.45, relheight=0.15)

        to_exclude_label.place(relx=0.55, rely=0.2)
        exclude_entry.place(relx=0.65, rely=0.2, relwidth=0.20)
        add_exclude_button.place(relx=0.9, rely=0.2)
        subtract_exclude_button.place(relx=0.95, rely=0.2)
        exclude_textbox.place(relx=0.55, rely=0.25, relwidth=0.45, relheight=0.15)

        key_target_label.place(relx=0.05, rely=0.5)
        value_target_label.place(relx=0.38, rely=0.5)
        id_target_entry.place(relx=0.05, rely=0.55, relwidth=0.3)
        rename_target_entry.place(relx=0.38, rely=0.55, relwidth=0.3)
        add_target_button.place(relx=0.75, rely=0.55)
        subtract_target_button.place(relx=0.85, rely=0.55)
        target_textbox.place(relx=0.05, rely=0.6, relwidth=0.9, relheight=0.15)

        single_file_helper.place(anchor=ctk.NE, relx=1, rely=0.85)
        single_file_switch.place(relx=0, rely=0.85)
        single_file_label.place(relx=0, rely=0.9)
        single_file_entry.place(relx=0.2, rely=0.9, relwidth=0.6)
        single_file_button.place(relx=0.8, rely=0.9, relwidth=0.15)

        self.switches["sorting"] = sorting_files_switch
        self.strvars["sorting"] = sorting_sv
        self.entries["sorting"] = sorting_entry
        self.switches["single file"] = single_file_switch
        self.strvars["single file"] = single_file_sv
        self.entries["single file"] = single_file_entry
        self.strvars["key target"] = id_target_sv
        self.strvars["value target"] = rename_target_sv
        self.entries["key target"] = id_target_entry
        self.entries["value target"] = rename_target_entry
        self.textboxes["targets"] = target_textbox
        self.strvars["to exclude"] = exclude_sv
        self.entries["to exclude"] = exclude_entry
        self.textboxes["to exclude"] = exclude_textbox
        self.strvars["to include"] = include_sv
        self.entries["to include"] = include_entry
        self.textboxes["to include"] = include_textbox
        # ------------ CONFIGURE
        sorting_files_switch.configure(
            command=partial(self.controller.category_enabling_switch, sorting_files_switch,
                            content_1_frame))
        single_file_switch.configure(
            command=partial(self.controller.category_enabling_switch, single_file_switch,
                            content_1_frame))
        sorting_button.configure(command=partial(self.select_parent_directory, sorting_sv))
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

    def generate_content2(self):
        check_content_button = ctk.CTkButton(master=self.frames["content 2"], text="Check step", fg_color="green",
                                             command=partial(self.check_processing_step_validity, "2"))

        content_2_frame = self.frames["content 2"]

        # ------- RAW MEA ------------------
        raw_mea_helper = Helper(master=content_2_frame, event_key="raw mea")

        raw_mea_switch = ctk.CTkSwitch(master=content_2_frame, text="Raw MEA recording files", )
        raw_mea_label = ctk.CTkLabel(master=content_2_frame, text="Size of info headers: ",
                                     text_color=gp.enabled_label_color)
        raw_mea_sv = ctk.StringVar()
        raw_mea_entry = ctk.CTkEntry(master=content_2_frame, state='normal', textvariable=raw_mea_sv)

        # --------- SELECT ELECTRODES -------
        select_elec_helper = Helper(master=content_2_frame, event_key="select electrodes")

        electrode_switch = ctk.CTkSwitch(master=content_2_frame, text="Select electrodes", )
        electrode_mode_label = ctk.CTkLabel(master=content_2_frame, text="mode: ", text_color=gp.enabled_label_color)

        electrode_metric_label = ctk.CTkLabel(master=content_2_frame, text="metric: ",
                                              text_color=gp.enabled_label_color)
        n_electrode_label = ctk.CTkLabel(master=content_2_frame, text="n electrodes: ",
                                         text_color=gp.enabled_label_color)
        mode_electrode_cbox = tk.ttk.Combobox(master=content_2_frame, values=["None", "max", ], state='disabled')
        mode_electrode_cbox.set("None")
        metric_electrode_cbox = tk.ttk.Combobox(master=content_2_frame, values=["None", "std", ], state='disabled')
        metric_electrode_cbox.set("None")
        n_electrode_sv = ctk.StringVar()
        n_electrodes_entry = ctk.CTkEntry(master=content_2_frame, state='normal', textvariable=n_electrode_sv)

        # ------- SAMPLING ------------------------
        sampling_helper = Helper(master=content_2_frame, event_key="sampling")

        sampling_switch = ctk.CTkSwitch(master=content_2_frame, text="Down sampling recordings")
        sampling_divide_label = ctk.CTkLabel(master=content_2_frame, text="Divide recording into ",
                                             text_color=gp.enabled_label_color)
        sampling_sv = ctk.StringVar()
        sampling_entry = ctk.CTkEntry(master=content_2_frame, state='normal', textvariable=sampling_sv)
        sampling_pieces_label = ctk.CTkLabel(master=content_2_frame, text="pieces", text_color=gp.enabled_label_color)

        # ------ MANAGING WIDGETS
        check_content_button.place(anchor=tk.SE, relx=1, rely=1)

        raw_mea_helper.place(anchor=ctk.NE, relx=1, rely=0)
        raw_mea_switch.place(relx=0.0, rely=0)
        raw_mea_label.place(relx=0.0, rely=0.1, )
        raw_mea_entry.place(relx=0.2, rely=0.2, relwidth=0.5)

        select_elec_helper.place(anchor=ctk.NE, relx=1, rely=0.3)
        electrode_switch.place(relx=0.0, rely=0.3)
        electrode_mode_label.place(relx=0.0, rely=0.4, )
        electrode_metric_label.place(relx=0.33, rely=0.4, )
        n_electrode_label.place(relx=0.66, rely=0.4, )
        mode_electrode_cbox.place(relx=0.0, rely=0.5, relwidth=0.3)
        metric_electrode_cbox.place(relx=0.33, rely=0.5, relwidth=0.3)
        n_electrodes_entry.place(relx=0.66, rely=0.5, relwidth=0.2)

        sampling_helper.place(anchor=ctk.NE, relx=1, rely=0.6)
        sampling_switch.place(relx=0, rely=0.6)
        sampling_divide_label.place(relx=0, rely=0.7)
        sampling_entry.place(relx=0.40, rely=0.7, relwidth=0.2)
        sampling_pieces_label.place(relx=0.7, rely=0.7)

        self.switches["raw mea"] = raw_mea_switch
        self.strvars["raw mea"] = raw_mea_sv
        self.entries["raw mea"] = raw_mea_entry
        self.switches["select electrodes"] = electrode_switch
        self.cbboxes["select electrode mode"] = mode_electrode_cbox
        self.cbboxes["select electrode metric"] = metric_electrode_cbox
        self.strvars["n electrodes"] = n_electrode_sv
        self.entries["n electrodes"] = n_electrodes_entry
        self.switches["select electrodes"] = electrode_switch
        self.cbboxes["select electrode mode"] = mode_electrode_cbox
        self.cbboxes["select electrode metric"] = metric_electrode_cbox
        self.strvars["n electrodes"] = n_electrode_sv
        self.entries["n electrodes"] = n_electrodes_entry
        self.switches["select electrodes"] = electrode_switch
        self.cbboxes["select electrode mode"] = mode_electrode_cbox
        self.cbboxes["select electrode metric"] = metric_electrode_cbox
        self.strvars["n electrodes"] = n_electrode_sv
        self.entries["n electrodes"] = n_electrodes_entry
        self.switches["select electrodes"] = electrode_switch
        self.cbboxes["select electrode mode"] = mode_electrode_cbox
        self.cbboxes["select electrode metric"] = metric_electrode_cbox
        self.strvars["n electrodes"] = n_electrode_sv
        self.entries["n electrodes"] = n_electrodes_entry
        self.switches["sampling"] = sampling_switch
        self.entries["sampling"] = sampling_entry
        self.strvars["sampling"] = sampling_sv

        # ------ CONFIGURE


    def generate_content3(self): # todo : managing here
        check_content_button = ctk.CTkButton(master=self.frames["content 3"], text="Check step", fg_color="green",
                                             command=partial(self.check_processing_step_validity, "3"))
        check_content_button.place(anchor=tk.SE, relx=1, rely=1)

        filter_frame = ctk.CTkScrollableFrame(master=self.frames["content 3"], )
        filter_frame.place(relwidth=0.3, relheight=0.55, rely=0.45, relx=0.33)
        filter_frame.grid_columnconfigure(0, weight=1)

        # ------- FILTERING ------------------------
        filter_helper = Helper(master=filter_frame, event_key="filter")
        filter_helper.place(anchor=ctk.NE, relx=1, rely=0)

        sub_filterframe = ctk.CTkFrame(master=filter_frame, height=280)
        sub_filterframe.grid(row=0, column=0, sticky=ctk.NSEW)

        name_filter_switch = ctk.CTkSwitch(master=sub_filterframe, text="Filter 1")
        name_filter_switch.place(relx=0, rely=0)

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
                                           values=["None", "Highpass", "Lowpass", "Bandstop", "Bandpass"],
                                           state="disabled")
        type_filter_cbox.set("None")
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
                                              values=["Non", "All", "Even", "Odd", ],
                                              state="disabled")
        type_harmonics_cbox.set("None")
        type_harmonics_cbox.place(relx=0, rely=0.85, relwidth=0.25)
        freq_hamronics_sv = ctk.StringVar()
        frequency_harmonics_entry = ctk.CTkEntry(master=sub_filterframe, state='disabled',
                                                 textvariable=freq_hamronics_sv)
        frequency_harmonics_entry.place(relx=0.3, rely=0.85, relwidth=0.3)
        nth_hamronics_sv = ctk.StringVar()
        nth_harmonics_entry = ctk.CTkEntry(master=sub_filterframe, state='disabled', textvariable=nth_hamronics_sv)
        nth_harmonics_entry.place(relx=0.7, rely=0.85, relwidth=0.2)

        self.switches["filter"] = name_filter_switch
        self.entries["filter order"] = order_filter_entry
        self.strvars["filter order"] = order_filter_sv
        self.entries["filter sampling"] = sampling_filter_entry
        self.strvars["filter sampling"] = sampling_filter_sv
        self.entries["first frequency"] = frequency1_filter_entry
        self.entries["second frequency"] = frequency2_filter_entry
        self.cbboxes["filter type"] = type_filter_cbox
        self.cbboxes["harmonic type"] = type_harmonics_cbox
        self.strvars["harmonic frequency"] = freq_hamronics_sv
        self.entries["harmonic frequency"] = frequency_harmonics_entry
        self.strvars["nth harmonic"] = nth_hamronics_sv
        self.entries["nth harmonic"] = nth_harmonics_entry

        # ----------- CONFIGURE

        name_filter_switch.configure(
            command=partial(self.controller.category_enabling_switch, name_filter_switch,
                            sub_filterframe))

    def generate_content4(self):
        check_content_button = ctk.CTkButton(master=self.frames["content 4"], text="Check step", fg_color="green",
                                             command=partial(self.check_processing_step_validity, "4"))
        check_content_button.place(anchor=tk.SE, relx=1, rely=1)

        frequential_frame = ctk.CTkFrame(master=self.frames["content 4"], )
        frequential_frame.place(relwidth=0.3, relheight=0.4, rely=0.0, relx=0.66)

        # ------- FREQUENTIAL PROCESSING -----------
        frequential_helper = Helper(master=frequential_frame, event_key="fft")
        frequential_helper.place(anchor=ctk.NE, relx=1, rely=0)

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

        self.switches["fft"] = fft_switch
        self.strvars["fft sampling"] = sampling_fft_sv
        self.entries["fft sampling"] = sampling_fft_entry
        self.switches["merge"] = merge_switch
        self.switches["smoothing"] = smooth_switch
        self.strvars["smoothing"] = smooth_sv
        self.entries["smoothing"] = smooth_entry

        # -------CONFIGURE
        fft_switch.configure(
            command=partial(self.controller.category_enabling_switch, fft_switch, frequential_frame))

    def generate_content5(self):
        check_content_button = ctk.CTkButton(master=self.frames["content 5"], text="Check step", fg_color="green",
                                             command=partial(self.check_processing_step_validity, "5"))
        check_content_button.place(anchor=tk.SE, relx=1, rely=1)

        exec_frame = ctk.CTkFrame(master=self.frames['content 5'], )
        exec_frame.place(relwidth=0.3, relheight=0.55, rely=0.45, relx=0.66)

        # ------- EXECUTE PROCESSING ---------------
        exec_helper = Helper(master=exec_frame, event_key="exec")
        exec_helper.place(anchor=ctk.NE, relx=1, rely=0)

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

        self.switches["random key"] = random_key_exec_switch
        self.switches["timestamp"] = timestamp_exec_switch
        self.switches["keyword"] = keyword_exec_switch
        self.switches["make dataset"] = make_dataset_switch
        self.entries["keyword"] = keyword_exec_entry
        self.entries["save files"] = save_exec_entry
        self.strvars["keyword"] = keyword_sv
        self.strvars["save files"] = save_exec_sv

        # -------- CONFIGURE
        keyword_exec_switch.configure(
            command=partial(self.controller.modulate_entry_state_by_switch, keyword_exec_switch,
                            keyword_exec_entry))

        save_exec_button.configure(command=partial(self.select_save_directory, save_exec_sv))

        process_exec_button.configure(command=partial(self.processing, ))
        save_model_button.configure(command=partial(self.save_config, ))
        load_model_button.configure(command=partial(self.load_model, ))

    def show_content1(self, *args):
        self.select_processing_step(1)

        self.frames['content 2'].place_forget()
        self.frames['content 3'].place_forget()
        self.frames['content 4'].place_forget()
        self.frames['content 5'].place_forget()
        self.frames["content 1"].place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)

    def show_content2(self, *args):
        self.select_processing_step(2)

        self.frames['content 1'].place_forget()
        self.frames['content 3'].place_forget()
        self.frames['content 4'].place_forget()
        self.frames['content 5'].place_forget()
        self.frames["content 2"].place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)

    def show_content3(self, *args):
        self.select_processing_step(3)

        self.frames['content 1'].place_forget()
        self.frames['content 2'].place_forget()
        self.frames['content 4'].place_forget()
        self.frames['content 5'].place_forget()
        self.frames["content 3"].place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)

    def show_content4(self, *args):
        self.select_processing_step(4)

        self.frames['content 1'].place_forget()
        self.frames['content 2'].place_forget()
        self.frames['content 3'].place_forget()
        self.frames['content 5'].place_forget()
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

    def add_subtract_to_include(self, entry, textbox, mode='add'):
        if self.controller:
            self.controller.add_subtract_to_include(entry, textbox, mode)

    def add_subtract_to_exclude(self, entry, textbox, mode='add'):
        if self.controller:
            self.controller.add_subtract_to_exclude(entry, textbox, mode)

    def add_subtract_target(self, key_entry, value_entry, textbox,
                            mode='add'):
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
        for i in range(1, 6):
            if self.step_check[str(i)] == 2:
                img = ctk.CTkImage(dark_image=Image.open(f"data/{i} grey.png"), size=(120, 120))
                self.image_buttons[str(i)].configure(image=img)
            if self.step_check[str(i)] == 1:
                img = ctk.CTkImage(dark_image=Image.open(f"data/{i} green.png"), size=(120, 120))
                self.image_buttons[str(i)].configure(image=img)
            if self.step_check[str(i)] == 0:
                img = ctk.CTkImage(dark_image=Image.open(f"data/{i} red.png"), size=(120, 120))
                self.image_buttons[str(i)].configure(image=img)
            if str(i) == str(step):
                img = ctk.CTkImage(dark_image=Image.open(f"data/{i} blue.png"), size=(120, 120))
                self.image_buttons[str(i)].configure(image=img)

    def check_processing_step_validity(self, step):
        if step == '1' or step == '3':
            img = ctk.CTkImage(dark_image=Image.open(f"data/{step} green.png"), size=(120, 120))
            self.image_buttons[step].configure(image=img)
            self.step_check[step] = 1
        else:
            img = ctk.CTkImage(dark_image=Image.open(f"data/{step} red.png"), size=(120, 120))
            self.image_buttons[str(step)].configure(image=img)
            self.step_check[step] = 0

    def check_all_steps(self):
        for i in range(1, 6):
            self.check_processing_step_validity(str(i))
