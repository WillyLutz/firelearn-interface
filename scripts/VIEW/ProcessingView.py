import tkinter as tk
from functools import partial
from tkinter import ttk

import customtkinter as ctk
from tensorflow.python.ops.gen_experimental_dataset_ops import experimental_latency_stats_dataset_eager_fallback
from tensorflow.python.ops.gen_state_ops import variable

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
        super().__init__(master=master, fg_color='blue')
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
        
        self.ibuttons_frame = ctk.CTkFrame(master=self.master, fg_color='transparent')
        self.content_frame = ctk.CTkFrame(master=self.master, )
        
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=8)
        self.master.grid_rowconfigure(0, weight=1)
        
        self.ibuttons_frame.grid_rowconfigure(0, weight=50)
        self.ibuttons_frame.grid_rowconfigure(1, weight=50)
        self.ibuttons_frame.grid_rowconfigure(2, weight=50)
        self.ibuttons_frame.grid_rowconfigure(3, weight=1)
        self.ibuttons_frame.grid_rowconfigure(4, weight=10)
        self.ibuttons_frame.grid_rowconfigure(5, weight=10)
        self.ibuttons_frame.grid_rowconfigure(6, weight=10)
        self.ibuttons_frame.grid_rowconfigure(7, weight=10)

        self.ibuttons_frame.grid(row=0, column=0, sticky='nsew')
        self.content_frame.grid(row=0, column=1, sticky='nsew',)
        self.manage_processing_tab()
    
    def manage_processing_tab(self):

        filesorter_ibtn = ImageButton(master=self.ibuttons_frame,
                                      img=ctk.CTkImage(
                                          dark_image=Image.open(
                                              resource_path("data/firelearn_img/filesorter_grey.png")),
                                          size=(60, 60)),
                                      command=partial(self.show_filesorter_frame, ))
        signal_ibtn = ImageButton(master=self.ibuttons_frame,
                                  img=ctk.CTkImage(
                                      dark_image=Image.open(resource_path("data/firelearn_img/signal_grey.png")),
                                      size=(60, 60)),
                                  command=partial(self.show_signal_frame, ))
        filename_ibtn = ImageButton(master=self.ibuttons_frame,
                                    img=ctk.CTkImage(
                                        dark_image=Image.open(resource_path("data/firelearn_img/filename_grey.png")),
                                        size=(60, 60)),
                                    command=partial(self.show_filename_frame, ))
        
        filesorter_frame = ctk.CTkFrame(master=self.content_frame, )
        signal_frame = ctk.CTkFrame(master=self.content_frame, )
        filename_frame = ctk.CTkFrame(master=self.content_frame, )
        
        check_all_button = ctk.CTkButton(master=self.ibuttons_frame, text="Check all steps",
                                         command=self.controller.check_params_validity,
                                         fg_color="green", )
        save_model_button = ctk.CTkButton(master=self.ibuttons_frame, text="Save config", fg_color="lightslategray",
                                          command=self.save_config)
        load_model_button = ctk.CTkButton(master=self.ibuttons_frame, text="Load config", fg_color="lightslategray",
                                          command=self.load_model)
        process_exec_button = ctk.CTkButton(master=self.ibuttons_frame, fg_color="green", text="Process",
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
        
        sep = Separator(master=self.ibuttons_frame, orient='h')
        sep.grid(row=3, column=0, sticky="ew")
        
        
        filesorter_ibtn.grid(row=0, column=0)
        signal_ibtn.grid(row=1, column=0)
        filename_ibtn.grid(row=2, column=0)
        save_model_button.grid(row=4, column=0)
        load_model_button.grid(row=5, column=0)
        check_all_button.grid(row=6, column=0)
        process_exec_button.grid(row=7, column=0)
        
        
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
        
    def trace_behead_checkbox_and_entry(self, *args):
        text = self.vars["summary behead"].get()
        text = ' '.join(text.split(" ")[:-1])
        text += ' disabled' if not self.vars["signal ckbox behead"].get() else " "+ self.vars["signal behead"].get()
        self.vars["summary behead"].set(text)
        
    def trace_select_columns(self, *args):
        n_col = self.vars["signal select columns number"].get()
        mode = self.vars["signal select columns mode"].get()
        metric = self.vars["signal select columns metric"].get()
        
        var = f"{n_col} - {mode} - {metric}"
        
        text = 'disabled' if not self.vars["signal select columns ckbox"].get() else var
        self.vars["summary select columns"].set(text)
    
    def trace_divide(self, *args):
        base = "Divide file into: "
        text = 'disabled' if not self.vars["signal sampling ckbox"].get() else self.vars["signal sampling"].get()
        self.vars["summary divide"].set(base + text)
    
    def trace_fft(self, *args):
        base = self.vars["summary fft"].get()
        base = ' '.join(base.split(" ")[:-1])
        
        text = ' disabled' if not self.vars["signal fft"].get() else " "+ self.vars["signal fft sf"].get()
        
        self.vars["summary fft"].set(base + text)
        
    def trace_average(self, *args):
        base = self.vars["summary average"].get()
        base = ' '.join(base.split(" ")[:-1])
        
        text = ' disabled' if not self.vars["signal average"].get() else " enabled"
        
        self.vars["summary average"].set(base + text)
        
    def trace_interpolation(self, *args):
        base = self.vars["summary interpolation"].get()
        base = ' '.join(base.split(" ")[:-1])
        
        text = ' disabled' if not self.vars["signal interpolation ckbox"].get() \
            else " " + self.vars["signal interpolation"].get()
        
        self.vars["summary interpolation"].set(base + text)
        
    def trace_filter(self, *args):
        filter_text = 'disabled' if not self.vars["signal filter"].get() else 'enabled'
        self.vars["summary filter"].set("Filtering: " + filter_text)
        
        order_text = self.vars["signal filter order"].get()
        self.vars["summary filter order"].set("Order: " + order_text)
        
        type_text = self.vars["signal filter type"].get()
        self.vars["summary filter type"].set("Type: " + type_text)
        
        sf_text = self.vars["signal filter sf"].get()
        self.vars["summary filter sf"].set("Sampling frequency (Hz): " + sf_text)
        
        first_cut_text = self.vars["signal filter first cut"].get()
        self.vars["summary filter first cut"].set("1st cut (Hz): " + first_cut_text)
        
        second_cut_text = self.vars["signal filter second cut"].get()
        self.vars["summary filter second cut"].set("2nd cut (Hz): " + second_cut_text)
        
    def trace_harmonics(self, *args):
        harmonics_text = 'disabled' if not self.vars["signal harmonics ckbox"].get() else 'enabled'
        self.vars["summary harmonics"].set("Filtering harmonics: " + harmonics_text)
        
        type_text = self.vars["signal harmonics type"].get()
        self.vars["summary harmonics type"].set("Type: " + type_text)
        
        freq_text = self.vars["signal filter harmonic frequency"].get()
        self.vars["summary harmonics frequency"].set("Frequency (Hz): " + freq_text)
        
        nth_text = self.vars["signal filter nth harmonic"].get()
        self.vars["summary harmonics nth"].set("Up to Nth: " + nth_text)
        
        
    def trace_filename(self, *args):
        random_key = self.vars["filename random key"].get()
        self.vars["summary random key"].set("Random key: " + "disabled" if not random_key else "Random key: " +'enabled')
        
        keyword = self.vars["filename keyword"].get()
        self.vars["summary keyword"].set("Keyword: " + keyword if self.vars["filename keyword ckbox"].get()
                                         else "Keyword: disabled")
        
        save_under = self.vars["filename save under"].get()
        if len(save_under) > 25:
            save_under = "/.../..." + save_under[-25:]
        self.vars["summary save under"].set("Save processed files under: " + save_under)
        
        timestamp = self.vars["filename timestamp"].get()
        self.vars["summary timestamp"].set("Timestamp: enabled" if timestamp else "Timestamp: disabled")
        
        make_dataset = self.vars["filename make dataset"].get()
        self.vars["summary make dataset"].set("Make files as dataset: enabled" if make_dataset
                                              else "Make files as dataset: disabled")
        
        filename = self.vars["filename filename"].get()
        self.vars["summary filename"].set("Specified filename: " + filename if self.vars["filename filename ckbox"].get()
                                          else "Specified filename: disabled")
        
    def generate_summary(self):
        summary_scrollable_frame = ctk.CTkScrollableFrame(master=self.frames["processing summary"])
        
        summary_label = ctk.CTkLabel(master=summary_scrollable_frame, text="Processing summary", font=('', 20))
        filesorter_label = ctk.CTkLabel(master=summary_scrollable_frame, text="File sorting", font=('', 15))
        
        summary_scrollable_frame.grid_columnconfigure(0, weight=10)
        summary_scrollable_frame.grid_columnconfigure(1, weight=1)
        summary_scrollable_frame.grid_columnconfigure(2, weight=10)
        
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
        
        # --------------- SIGNAL PROCESSING
        signal_processing_label = ctk.CTkLabel(master=summary_scrollable_frame, text="Signal processing", font=('', 15))
        
        beheading_var = ctk.StringVar(value='Beheading top-file metadata: disabled')
        beheading_label = ctk.CTkLabel(master=summary_scrollable_frame, textvariable=beheading_var)

        select_column_frame = ctk.CTkFrame(master=summary_scrollable_frame, fg_color='transparent')
        select_columns_label_unvar = ctk.CTkLabel(master=select_column_frame, text="Select columns: ")
        select_columns_var = ctk.StringVar(value='disabled')
        select_columns_label = ctk.CTkLabel(master=select_column_frame, textvariable=select_columns_var)

        divide_var = ctk.StringVar(value='Divide file into: disabled')
        divide_label = ctk.CTkLabel(master=summary_scrollable_frame, textvariable=divide_var)
        
        fft_var = ctk.StringVar(value='Fast Fourier Transform sampling frequency (Hz): disabled')
        fft_label = ctk.CTkLabel(master=summary_scrollable_frame, textvariable=fft_var)
        
        average_var = ctk.StringVar(value='Average signal column-wise: disabled')
        average_label = ctk.CTkLabel(master=summary_scrollable_frame, textvariable=average_var)
        
        interpolation_var = ctk.StringVar(value='Linear interpolation into n values: disabled')
        interpolation_label = ctk.CTkLabel(master=summary_scrollable_frame, textvariable=interpolation_var)
        
        # -- filtering
        filter_frame = ctk.CTkFrame(master=summary_scrollable_frame, fg_color='transparent')
        filter_var = ctk.StringVar(value='Filtering: ')
        filter_label = ctk.CTkLabel(master=filter_frame, textvariable=filter_var)
        order_var = ctk.StringVar(value='Order: ')
        order_label=ctk.CTkLabel(master=filter_frame, textvariable=order_var)
        sf_var = ctk.StringVar(value='Sampling frequency (Hz): ')
        sf_label = ctk.CTkLabel(master=filter_frame, textvariable=sf_var)
        type_var = ctk.StringVar(value='Type: ')
        type_label = ctk.CTkLabel(master=filter_frame, textvariable=type_var)
        first_cut_var = ctk.StringVar(value='1st cut (Hz): ')
        first_cut_label = ctk.CTkLabel(master=filter_frame, textvariable=first_cut_var)
        second_cut_var = ctk.StringVar(value='2nd cut (Hz): ')
        second_cut_label = ctk.CTkLabel(master=filter_frame, textvariable=second_cut_var)
        
        # ---- harmonics
        harmonics_frame = ctk.CTkFrame(master=summary_scrollable_frame, fg_color='transparent')
        harmonics_var = ctk.StringVar(value="Filter harmonics: ")
        harmonics_label = ctk.CTkLabel(master=harmonics_frame, textvariable=harmonics_var,)
        harmonics_type_var = ctk.StringVar(value="Type")
        harmonics_type_label = ctk.CTkLabel(master=harmonics_frame, textvariable=harmonics_type_var)
        harmonics_freq_var = ctk.StringVar(value="Frequency (Hz): ")
        harmonics_freq_label = ctk.CTkLabel(master=harmonics_frame, textvariable=harmonics_freq_var)
        harmonics_nth_var = ctk.StringVar(value="Up to Nth: ")
        harmonics_nth_label = ctk.CTkLabel(master=harmonics_frame, textvariable=harmonics_nth_var)
        
        # ------------- FILEMANAGER ---------------
        output_label = ctk.CTkLabel(master=summary_scrollable_frame, text="Output management", font=('', 15))
        
        random_key_var = ctk.StringVar(value="Random key: disabled")
        timestamp_var = ctk.StringVar(value="Timestamp: disabled")
        keyword_var = ctk.StringVar(value="Keyword: disabled")
        make_dataset_var = ctk.StringVar(value="Make files as dataset: disabled")
        filename_var = ctk.StringVar(value="Specified filename: disabled")
        save_under_var = ctk.StringVar(value="Save processed files under: ")
        
        random_key_label = ctk.CTkLabel(master=summary_scrollable_frame, textvariable=random_key_var)
        timestamp_label = ctk.CTkLabel(master=summary_scrollable_frame, textvariable=timestamp_var)
        keyword_label = ctk.CTkLabel(master=summary_scrollable_frame, textvariable=keyword_var)
        make_dataset_label = ctk.CTkLabel(master=summary_scrollable_frame, textvariable=make_dataset_var)
        filename_label = ctk.CTkLabel(master=summary_scrollable_frame, textvariable=filename_var)
        save_under_label = ctk.CTkLabel(master=summary_scrollable_frame, textvariable=save_under_var)
        
        # ------------  WIDGET MANAGEMENT
        summary_scrollable_frame.place(relwidth=1, relheight=1)
        # separator row 0
        # separator row 1
        # separator row 2
        summary_label.grid(row=3, column=0, columnspan=3)
        # separator row 4
        filesorter_label.grid(row=5, column=0, columnspan=3)
        # separator row 6
        multiple_files_frame.grid(row=7, column=0, sticky='ew', columnspan=3)
        multiple_files_label.pack(side="left")
        multiple_files_label_state.pack(side='left')
        # separator row 8
        parent_path_frame.grid(row=9, column=0, sticky='ew', columnspan=3)
        parent_path_label_title.pack(side='left')
        parent_path_label.pack(side='left')
        # separator row 10
        to_include_label.grid(row=11, column=0)
        to_exclude_label.grid(row=11, column=1)
        include_exclude_frame.grid(row=12, column=0, columnspan=3, sticky='nsew')
        include_textbox.pack(side='left', padx=5, pady=5)
        exclude_textbox.pack(side='left', padx=5, pady=5)
        # separator row 13
        targets_label.grid(row=14, column=0)
        target_textbox.grid(row=15, column=0, columnspan=3, sticky='ew')
        # separator row 16
        single_file_frame.grid(row=17, column=0, sticky='ew', columnspan=3)
        single_file_label.pack(side="left")
        single_file_label_state.pack(side='left')
        # separator row 18
        file_path_frame.grid(row=19, column=0, sticky='ew', columnspan=3)
        file_path_label_title.pack(side='left')
        file_path_label.pack(side='left')
        # separator row 20
        # separator row 21
        # separator row 22
        signal_processing_label.grid(row=23, column=0, columnspan=3)
        # separator row 24
        beheading_label.grid(row=25, column=0, columnspan=3, sticky="w")
        #separator row 26
        select_column_frame.grid(row=27, column=0, columnspan=3, sticky='w')
        select_columns_label_unvar.pack(side='left',)
        select_columns_label.pack(side='left',)
        # separator row 28
        divide_label.grid(row=29, column=0, columnspan=3, sticky='w')
        #separator row 30
        fft_label.grid(row=31, column=0, columnspan=3, sticky='w')
        #separator row 32
        average_label.grid(row=33, column=0, columnspan=3, sticky='w')
        #separator row 34
        interpolation_label.grid(row=35, column=0, columnspan=3, sticky='w')
        #separator row 36
        filter_frame.grid(row=37, column=0, columnspan=3, sticky="nsew")
        
        filter_label.grid(row=0, column=0, sticky='w')
        order_label.grid(row=0, column=2, sticky='w')
        sf_label.grid(row=1, column=0, sticky='w')
        type_label.grid(row=1, column=2, sticky='w')
        first_cut_label.grid(row=2, column=0, sticky='w')
        second_cut_label.grid(row=2, column=2, sticky='w')
        
        filter_frame.grid_columnconfigure(0, weight=20)
        filter_frame.grid_columnconfigure(1, weight=1)
        filter_frame.grid_columnconfigure(2, weight=20)
        minisep = Separator(master=filter_frame, orient='v')
        minisep.grid(row=0, column=1, rowspan=3, sticky="ns")
        #separator row 38
        harmonics_frame.grid(row=39, column=0, columnspan=3, sticky='nsew')
        
        harmonics_label.grid(row=0, column=0, sticky='w')
        harmonics_type_label.grid(row=0, column=2, sticky='w')
        harmonics_freq_label.grid(row=1, column=0, sticky='w')
        harmonics_nth_label.grid(row=1, column=2, sticky='w')
        
        harmonics_frame.grid_columnconfigure(0, weight=20)
        harmonics_frame.grid_columnconfigure(1, weight=1)
        harmonics_frame.grid_columnconfigure(2, weight=20)
        harmonic_sep = Separator(master=harmonics_frame, orient='v')
        harmonic_sep.grid(row=0, column=1, rowspan=3, sticky="ns")
        # separator row 40
        # separator row 41
        # separator row 42
        output_label.grid(row=43, column=0, columnspan=3)
        # separator row 44
        random_key_label.grid(row=45, column=0, columnspan=3,  sticky='w')
        # separator row 46
        timestamp_label.grid(row=47, column=0, columnspan=3,  sticky='w')
        # separator row 48
        keyword_label.grid(row=49, column=0, columnspan=3,  sticky='w')
        # separator row 50
        make_dataset_label.grid(row=51, column=0, columnspan=3, sticky='w')
        # separator row 52
        filename_label.grid(row=53, column=0, columnspan=3,  sticky='w')
        # separator row 54
        save_under_label.grid(row=55, column=0, columnspan=3, sticky='w')
        
        # ------------ SEPARATORS
        for row in range(0, 55, 1):
            if row in [0, 1, 2, 4, 6, 8, 10, 13, 16, 18, 20, 21, 22, 24, 26, 28, 30,
                       32, 34, 36, 38, 40, 41, 42, 44, 46, 48, 50, 52, 54, ]:
                sep = Separator(master=summary_scrollable_frame, orient='h')
                sep.grid(row=row, column=0, columnspan=3, sticky="ew")
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
        
        self.vars["summary behead"] = beheading_var
        self.vars["summary select columns"] = select_columns_var
        self.vars["summary divide"] = divide_var
        self.vars["summary fft"] = fft_var
        self.vars["summary interpolation"] = interpolation_var
        self.vars["summary average"] = average_var
        
        self.vars["summary filter"] = filter_var
        self.vars["summary filter order"] = order_var
        self.vars["summary filter sf"] = sf_var
        self.vars["summary filter type"] = type_var
        self.vars["summary filter first cut"] = first_cut_var
        self.vars["summary filter second cut"] = second_cut_var
        
        self.vars["summary harmonics"] = harmonics_var
        self.vars["summary harmonics type"] = harmonics_type_var
        self.vars["summary harmonics frequency"] = harmonics_freq_var
        self.vars["summary harmonics nth"] = harmonics_nth_var
        
        self.vars["summary random key"] = random_key_var
        self.vars["summary timestamp"] = timestamp_var
        self.vars["summary keyword"] = keyword_var
        self.vars["summary make dataset"] = make_dataset_var
        self.vars["summary filename"] = filename_var
        self.vars["summary save under"] = save_under_var
    
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
        # separator row 12
        
        # single_file_helper.place(anchor=ctk.NE, relx=1, rely=0.85)
        # todo : add helper
        single_file_ckbox.grid(row=13, column=0, sticky='w' )
        
        # ---- row 14 separator ----
        
        single_file_frame.grid(row=15, column=0, sticky='ew' )
        single_file_label.pack(side='left')
        # single_file_entry.place_errentry(relx=0, rely=0.95, relwidth=0.6, relpady=0.04)
        single_file_entry.grid(row=15, column=2, sticky='ew')
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
            if row in [1, 3, 5, 7, 9, 11,12, 14]:
                sep = Separator(master=filesorter_frame, orient='h')
                sep.grid(row=row, column=0, columnspan=3, sticky="ew")
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
        behead_ckbox_var = ctk.IntVar(value=0)
        behead_ckbox = ctk.CTkCheckBox(master=signal_frame, text="Beheading top-file metadata", variable=behead_ckbox_var)
        behead_sv = ctk.StringVar()
        behead_entry = ErrEntry(master=signal_frame, state='normal', textvariable=behead_sv)
        
        # --------- signal select columns -------
        electrode_ckbox_var = ctk.IntVar(value=0)
        electrode_ckbox = ctk.CTkCheckBox(master=signal_frame, text="Select columns", variable=electrode_ckbox_var)
        electrode_mode_label = ctk.CTkLabel(master=signal_frame, text="mode: ", text_color=gp.enabled_label_color)
        
        electrode_metric_label = ctk.CTkLabel(master=signal_frame, text="metric: ",
                                              text_color=gp.enabled_label_color)
        mode_electrode_var = ctk.StringVar(value='None')
        mode_electrode_cbox = tk.ttk.Combobox(master=signal_frame, values=["None", "max", ], state='readonly',
                                              textvariable=mode_electrode_var)
        mode_electrode_cbox.set("None")
        metric_electrode_var = ctk.StringVar(value='None')
        metric_electrode_cbox = tk.ttk.Combobox(master=signal_frame, values=["None", "std", ], state='readonly',
                                                textvariable=metric_electrode_var)
        metric_electrode_cbox.set("None")
        n_electrode_sv = ctk.StringVar()
        n_electrodes_entry = ErrEntry(master=signal_frame, state='normal', textvariable=n_electrode_sv)
        
        # ------- SAMPLING ------------------------
        sampling_var = ctk.IntVar(value=0)
        sampling_ckbox = ctk.CTkCheckBox(master=signal_frame, text="Divide file into", variable=sampling_var)
        sampling_sv = ctk.StringVar()
        sampling_entry = ErrEntry(master=signal_frame, state='normal', textvariable=sampling_sv)
        
        # ------- FILTERING ------------------------
        filter_var = ctk.IntVar(value=0)
        filter_ckbox = ctk.CTkCheckBox(master=signal_frame, text="Filtering", variable=filter_var)
        
        order_filter_label = ctk.CTkLabel(master=signal_frame, text="Order: ", text_color=gp.enabled_label_color)
        order_filter_sv = ctk.StringVar()
        order_filter_entry = ErrEntry(master=signal_frame, state='normal', textvariable=order_filter_sv)
        sampling_filter_label = ctk.CTkLabel(master=signal_frame, text="Sampling frequency (Hz):",
                                             text_color=gp.enabled_label_color)
        sampling_filter_sv = ctk.StringVar()
        sampling_filter_entry = ErrEntry(master=signal_frame, state='normal', textvariable=sampling_filter_sv)
        
        filter_type_var = ctk.StringVar(value='None')
        type_filter_label = ctk.CTkLabel(master=signal_frame, text="Type: ", text_color=gp.enabled_label_color)
        frequency1_filter_label = ctk.CTkLabel(master=signal_frame, text="1st cut frequency (Hz): ",
                                               text_color=gp.enabled_label_color)
        frequency2_filter_label = ctk.CTkLabel(master=signal_frame, text="2nd cut frequency (optional, Hz): ",
                                               text_color=gp.enabled_label_color)
        type_filter_cbox = tk.ttk.Combobox(master=signal_frame,
                                           values=["None", "Highpass", "Lowpass", "Bandstop", "Bandpass"],
                                           state="readonly", textvariable=filter_type_var)
        type_filter_cbox.set("None")
        f1_filter_sv = ctk.StringVar()
        frequency1_filter_entry = ErrEntry(master=signal_frame, state='normal', textvariable=f1_filter_sv)
        f2_filter_sv = ctk.StringVar()
        frequency2_filter_entry = ErrEntry(master=signal_frame, state='normal', textvariable=f2_filter_sv)
        
        # ---------- HARMONICS
        harmonics_filter_var = ctk.IntVar(value=0)
        harmonics_filter_ckbox = ctk.CTkCheckBox(master=signal_frame, text="Filter harmonics", variable=harmonics_filter_var)
        type_harmonics_label = ctk.CTkLabel(master=signal_frame, text="Type:", text_color=gp.enabled_label_color)
        freq_harmonics_label = ctk.CTkLabel(master=signal_frame, text="Frequency (Hz):",
                                            text_color=gp.enabled_label_color)
        nth_harmonics_label = ctk.CTkLabel(master=signal_frame, text="Up to Nth (Hz):",
                                           text_color=gp.enabled_label_color)
        
        harmonics_type_var = ctk.StringVar(value='None')
        type_harmonics_cbox = tk.ttk.Combobox(master=signal_frame,
                                              values=["None", "All", "Even", "Odd", ],
                                              state="readonly", textvariable=harmonics_type_var)
        type_harmonics_cbox.set("None")
        freq_harmonics_sv = ctk.StringVar()
        frequency_harmonics_entry = ErrEntry(master=signal_frame, state='normal',
                                             textvariable=freq_harmonics_sv)
        nth_harmonics_sv = ctk.StringVar()
        nth_harmonics_entry = ErrEntry(master=signal_frame, state='normal', textvariable=nth_harmonics_sv)
        
        # ------- FREQUENTIAL PROCESSING -----------
        fft_ckbox_var = ctk.IntVar(value=0)
        sampling_fft_sv = ctk.StringVar()
        average_ckbox_var = ctk.IntVar(value=0)
        interpolation_ckbox_var = ctk.IntVar(value=0)
        
        fft_ckbox = ctk.CTkCheckBox(master=signal_frame, text="FFT. Sampling frequency (Hz):", variable=fft_ckbox_var)

        sampling_fft_entry = ErrEntry(master=signal_frame, state='normal', textvariable=sampling_fft_sv)
        average_ckbox = ctk.CTkCheckBox(master=signal_frame, text="Average electrodes signal",
                                        variable=average_ckbox_var)
        interpolation_ckbox = ctk.CTkCheckBox(master=signal_frame, text="Linear interpolation into n values: ", 
                                              variable=interpolation_ckbox_var)

        interpolation_entry_var = ctk.StringVar()
        interpolation_entry = ErrEntry(master=signal_frame, state='normal', textvariable=interpolation_entry_var)
        
        # ------ MANAGING WIDGETS
        behead_ckbox.grid(row=0, column=0, sticky='ew')
        behead_entry.grid(row=0, column=2, sticky='ew')
        # Separator row 1
        # Separator row 2
        electrode_ckbox.grid(row=3, column=0, sticky='ew')
        n_electrodes_entry.grid(row=3, column=2, sticky='ew')
        # Separator row 4
        electrode_mode_label.grid(row=5, column=0,)
        mode_electrode_cbox.grid(row=5, column=2, sticky='ew')
        # Separator row 6
        electrode_metric_label.grid(row=7, column=0,)
        metric_electrode_cbox.grid(row=7, column=2, sticky='ew')
        
        # Separator row 8
        # Separator row 9

        sampling_ckbox.grid(row=10, column=0, sticky='ew')
        sampling_entry.grid(row=10, column=2, sticky='ew')
        # Separator row 11
        fft_ckbox.grid(row=12, column=0, sticky='ew')
        sampling_fft_entry.grid(row=12, column=2, sticky='ew')
        # Separator row 13
        average_ckbox.grid(row=14, column=0, sticky='ew')
        # Separator row 15
        interpolation_ckbox.grid(row=16, column=0, sticky='ew')
        interpolation_entry.grid(row=16, column=2, sticky='ew')
        # Separator row 17
        # Separator row 18
       
        filter_ckbox.grid(row=19, column=0, sticky='ew')
        # Separator row 20
        order_filter_label.grid(row=21, column=0, )
        order_filter_entry.grid(row=21, column=2, sticky='ew')
        # Separator row 22
        sampling_filter_label.grid(row=23, column=0, )
        sampling_filter_entry.grid(row=23, column=2, sticky='ew')
        # Separator row 24
        type_filter_label.grid(row=25, column=0,)
        type_filter_cbox.grid(row=25, column=2, sticky='ew')
        # Separator row 26
        frequency1_filter_label.grid(row=27, column=0, )
        frequency1_filter_entry.grid(row=27, column=2, sticky='ew')
        # Separator row 28
        frequency2_filter_label.grid(row=29, column=0, )
        frequency2_filter_entry.grid(row=29, column=2, sticky='ew')
        # Separator row 30
        # Separator row 31
        harmonics_filter_ckbox.grid(row=32, column=0, sticky='ew')
        # Separator row 33
        type_harmonics_label.grid(row=34, column=0,)
        type_harmonics_cbox.grid(row=34, column=2, sticky='ew')
        # Separator row 35
        freq_harmonics_label.grid(row=36, column=0, )
        frequency_harmonics_entry.grid(row=36, column=2, sticky='ew')
        # Separator row 37
        nth_harmonics_label.grid(row=38, column=0,)
        nth_harmonics_entry.grid(row=38, column=2, sticky='ew')
        
        
        # ------ SEPARATORS ------------
        signal_frame.grid_columnconfigure(0, weight=1)
        signal_frame.grid_columnconfigure(1, weight=1)
        signal_frame.grid_columnconfigure(2, weight=20)
        for col in [1, ]:
            sep = Separator(master=signal_frame, orient='v')
            sep.grid(row=0, column=col, rowspan=39, sticky="ns")
            
        for row in range(0, 39, 1):
            if row in [1, 2, 4, 6, 8, 9, 11, 13, 15, 17, 18, 20, 22, 24, 26, 28, 30, 31, 33, 35, 37]:
                sep = Separator(master=signal_frame, orient='h')
                sep.grid(row=row, column=0, columnspan=3, sticky="ew")
                signal_frame.grid_rowconfigure(row, weight=1)
            else:
                signal_frame.grid_rowconfigure(row, weight=10)
        
        # ------ STORE VARIABLES --------
        
        self.ckboxes["signal ckbox behead"] = behead_ckbox
        self.vars["signal ckbox behead"] = behead_ckbox_var
        self.vars["signal behead"] = behead_sv
        self.entries["signal behead"] = behead_entry
        
        self.ckboxes["signal select columns"] = electrode_ckbox
        self.cbboxes["signal select columns mode"] = mode_electrode_cbox
        self.cbboxes["signal select columns metric"] = metric_electrode_cbox
        self.vars["signal select columns number"] = n_electrode_sv
        self.vars["signal select columns ckbox"] = electrode_ckbox_var
        self.vars["signal select columns mode"] = metric_electrode_var
        self.vars["signal select columns metric"] = mode_electrode_var
        self.entries["signal select columns number"] = n_electrodes_entry
        
        self.ckboxes["signal sampling"] = sampling_ckbox
        self.entries["signal sampling"] = sampling_entry
        self.vars["signal sampling"] = sampling_sv
        self.vars["signal sampling ckbox"] = sampling_var
        
        self.ckboxes["signal fft"] = fft_ckbox
        self.ckboxes["signal average"] = average_ckbox
        self.entries["signal interpolation"] = interpolation_entry
        self.entries["signal fft sf"] = sampling_fft_entry
        self.ckboxes["signal interpolation"] = interpolation_ckbox
        self.vars["signal fft sf"] = sampling_fft_sv
        self.vars["signal interpolation"] = interpolation_entry_var
        self.vars["signal interpolation ckbox"] = interpolation_ckbox_var
        self.vars["signal fft"] = fft_ckbox_var
        self.vars["signal average"] = average_ckbox_var
        
        
        self.vars["signal filter"] = filter_var
        self.vars["signal filter type"] = filter_type_var
        self.vars["signal filter first cut"] = f1_filter_sv
        self.vars["signal filter second cut"] = f2_filter_sv
        self.vars["signal filter order"] = order_filter_sv
        self.vars["signal filter sf"] = sampling_filter_sv
        self.ckboxes["signal filter"] = filter_ckbox
        self.entries["signal filter order"] = order_filter_entry
        self.entries["signal filter sf"] = sampling_filter_entry
        self.entries["signal filter first frequency"] = frequency1_filter_entry
        self.entries["signal filter second frequency"] = frequency2_filter_entry
        self.cbboxes["signal filter type"] = type_filter_cbox
        
        self.ckboxes["signal filter harmonic"] = harmonics_filter_ckbox
        self.cbboxes["signal filter harmonic type"] = type_harmonics_cbox
        self.vars["signal filter harmonic frequency"] = freq_harmonics_sv
        self.entries["signal filter harmonic frequency"] = frequency_harmonics_entry
        self.vars["signal filter nth harmonic"] = nth_harmonics_sv
        self.entries["signal filter nth harmonic"] = nth_harmonics_entry
        self.vars["signal harmonics ckbox"] = harmonics_filter_var
        self.vars["signal harmonics type"] = harmonics_type_var
        
        # --------- TRACE
        behead_sv.trace("w", self.trace_behead_checkbox_and_entry)
        behead_ckbox_var.trace("w", self.trace_behead_checkbox_and_entry)
        
        electrode_ckbox_var.trace("w", self.trace_select_columns)
        n_electrode_sv.trace("w", self.trace_select_columns)
        mode_electrode_var.trace("w", self.trace_select_columns)
        metric_electrode_var.trace("w", self.trace_select_columns)
        
        sampling_var.trace("w", self.trace_divide)
        sampling_sv.trace("w", self.trace_divide)
        
        fft_ckbox_var.trace("w", self.trace_fft)
        sampling_fft_sv.trace("w", self.trace_fft)
        interpolation_ckbox_var.trace("w", self.trace_interpolation)
        interpolation_entry_var.trace("w", self.trace_interpolation)
        average_ckbox_var.trace("w", self.trace_average)
        
        filter_var.trace("w", self.trace_filter)
        filter_type_var.trace("w", self.trace_filter)
        order_filter_sv.trace("w", self.trace_filter)
        f1_filter_sv.trace("w", self.trace_filter)
        f2_filter_sv.trace("w", self.trace_filter)
        sampling_filter_sv.trace("w", self.trace_filter)
        
        harmonics_type_var.trace("w", self.trace_harmonics)
        harmonics_filter_var.trace("w", self.trace_harmonics)
        nth_harmonics_sv.trace("w", self.trace_harmonics)
        freq_harmonics_sv.trace("w", self.trace_harmonics)
        
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
        
        interpolation_entry.configure(validate='focus',
                               validatecommand=(
                                   self.register(partial(self.parent_view.is_positive_int_or_emtpy, interpolation_entry)),
                                   '%P'))
        sampling_fft_entry.configure(validate='focus',
                                     validatecommand=(self.register(
                                         partial(self.parent_view.is_positive_int_or_emtpy, sampling_fft_entry)), '%P'))
    
    def generate_filename_content(self):
        filename_frame = self.frames["filename"]
        
        filename_frame.place(relwidth=0.9, relheight=0.9, rely=0.05, relx=0.05)
        filename_frame.grid_columnconfigure(0, weight=1)
        filename_frame.grid_columnconfigure(1, weight=1)
        filename_frame.grid_columnconfigure(2, weight=10)

        # ----- EXECUTE
        random_key_var = ctk.IntVar(value=0)
        random_key_exec_ckbox = ctk.CTkCheckBox(master=filename_frame, text="Add random key to file names", 
                                                variable=random_key_var)
        timestamp_exec_var = ctk.IntVar(value=0)
        timestamp_exec_ckbox = ctk.CTkCheckBox(master=filename_frame, text="Add timestamp to file names",
                                               variable=timestamp_exec_var)
        keyword_exec_var = ctk.IntVar(value=0)
        keyword_exec_ckbox = ctk.CTkCheckBox(master=filename_frame, text="Add keyword to file names", variable=keyword_exec_var)
        keyword_sv = ctk.StringVar()
        keyword_entry = ErrEntry(master=filename_frame, state='normal', textvariable=keyword_sv)
        
        make_dataset_var = ctk.IntVar(value=0)
        make_dataset_ckbox = ctk.CTkCheckBox(master=filename_frame,
                                            text="Make files as datasets", variable=make_dataset_var)
        save_files_exec_label = ctk.CTkLabel(master=filename_frame, text="Save processed files under:",
                                             text_color=gp.enabled_label_color)
        save_exec_sv = ctk.StringVar()
        save_entry = ErrEntry(master=filename_frame, textvariable=save_exec_sv, state='disabled')
        save_exec_button = ctk.CTkButton(master=filename_frame, text="Open", width=40)
        
        filename_ckbox_var = ctk.IntVar(value=0)
        filename_ckbox= ctk.CTkCheckBox(master=filename_frame, text="Specify file name", variable=filename_ckbox_var)
        filename_var = ctk.StringVar()
        filename_entry = ErrEntry(master=filename_frame, state='normal', textvariable=filename_var)
        
        random_key_exec_ckbox.grid(row=0, column=0, sticky='w')
        # separator row 1
        timestamp_exec_ckbox.grid(row=2, column=0, sticky='w')
        # separator row 3
        keyword_exec_ckbox.grid(row=4, column=0, sticky='w')
        keyword_entry.grid(row=4, column=2, sticky='we')
        # separator row 5
        make_dataset_ckbox.grid(row=6, column=0, sticky='w')
        # separator row 7

        filename_ckbox.grid(row=8, column=0, sticky='w')
        filename_entry.grid(row=8, column=2, sticky='we')
        # separator row 9
        save_files_exec_label.grid(row=10, column=0, sticky='w')
        save_entry.grid(row=10, column=2, sticky='we')
        save_exec_button.grid(row=10, column=0, sticky='e')
        
        # ----- SEPARATORS ---------
        for col in range(0, 3, 1):
            if col in [1, ]:
                sep = Separator(master=filename_frame, orient='v')
                sep.grid(row=0, column=col, rowspan=11, sticky="ns")
                filename_frame.grid_columnconfigure(col, weight=1)
            else:
                filename_frame.grid_columnconfigure(col, weight=20)
        for row in range(0, 11, 1):
            if row in [1, 3, 5, 7, 9]:
                sep = Separator(master=filename_frame, orient='h')
                sep.grid(row=row, column=0, columnspan=3, sticky="ew")
                filename_frame.grid_rowconfigure(row, weight=1)
            else:
                filename_frame.grid_rowconfigure(row, weight=10)
        
        self.ckboxes["filename random key"] = random_key_exec_ckbox
        self.ckboxes["filename timestamp"] = timestamp_exec_ckbox
        self.ckboxes["filename keyword"] = keyword_exec_ckbox
        self.ckboxes["filename"] = filename_ckbox
        self.ckboxes["make dataset"] = make_dataset_ckbox
        self.entries["filename keyword"] = keyword_entry
        self.entries["filename"] = filename_entry
        self.entries["filename save under"] = save_entry
        self.vars["filename keyword"] = keyword_sv
        self.vars["filename save under"] = save_exec_sv
        self.vars["filename random key"] = random_key_var
        self.vars["filename timestamp"] = timestamp_exec_var
        self.vars["filename keyword ckbox"] = keyword_exec_var
        self.vars["filename make dataset"] = make_dataset_var
        self.vars["filename filename ckbox"] = filename_ckbox_var
        self.vars["filename filename"] = filename_var
        
        
        # ----------- TRACE
        keyword_sv.trace("w", self.trace_filename)
        save_exec_sv.trace("w", self.trace_filename)
        random_key_var.trace("w", self.trace_filename)
        keyword_exec_var.trace("w", self.trace_filename)
        make_dataset_var.trace("w", self.trace_filename)
        filename_var.trace("w", self.trace_filename)
        filename_ckbox_var.trace("w", self.trace_filename)
        timestamp_exec_var.trace("w", self.trace_filename)
        
        # ----------- CONFIGURE
        
        keyword_exec_ckbox.configure(
            command=partial(self.controller.modulate_entry_state_by_switch, keyword_exec_ckbox,
                            keyword_entry))
        
        filename_ckbox.configure(
            command=partial(self.controller.modulate_entry_state_by_switch, filename_ckbox,
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

