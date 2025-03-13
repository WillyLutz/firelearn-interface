import tkinter as tk
from functools import partial
from tkinter import ttk

import customtkinter as ctk
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,  NavigationToolbar2Tk
from matplotlib.figure import Figure

from scripts import params as p
from scripts.CONTROLLER.ConfusionController import ConfusionController
from scripts.WIDGETS.ErrEntry import ErrEntry
from scripts.WIDGETS.Separator import Separator


class ConfusionView(ctk.CTkFrame):
    def __init__(self, app, master, parent_view):
        super().__init__(master=app)
        self.master = master
        self.parent_view = parent_view
        self.main_view = self.parent_view.parent_view
        self.controller = ConfusionController(self, )
        self.app = app

        self.frames = {}
        self.entries = {}
        self.buttons = {}
        self.ckboxes = {}
        self.cbboxes = {}
        self.vars = {}
        self.trace_ids = {}
        self.switches = {}
        self.sliders = {}
        self.textboxes = {}
        self.canvas = {}
        self.lines = {}
        self.figures = {}
        self.scrollable_frames = {}

        self.ydata_subframes = {}
        self.manage_confusion_tab()

    def set_controller(self, controller):
        self.controller = controller

    def manage_general_params(self, general_params_scrollable_frame):
        # row separator 0
        # row separator 1
        
        general_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="GENERAL PARAMETERS", font=('', 20))
        
        # row separator 3
        # row separator 4
        title_var = tk.StringVar(value=self.controller.model.plot_general_settings['title'])
        title_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="Figure title:")
        title_entry = ErrEntry(master=general_params_scrollable_frame, width=180, textvariable=title_var)
        # row separator 6
        title_font_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="Title font:")
        title_font_var = tk.StringVar(value=self.controller.model.plot_general_settings['title font'])
        title_font_cbbox = tk.ttk.Combobox(master=general_params_scrollable_frame, values=p.FONTS, state='readonly',
                                           textvariable=title_font_var)
        # row separator 8
        title_size_var = tk.IntVar(value=self.controller.model.plot_general_settings['title size'])
        title_size_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="Title size:")
        title_size_slider = ctk.CTkSlider(master=general_params_scrollable_frame, from_=8, to=32, number_of_steps=24,
                                          variable=title_size_var)
        title_size_value_label = ctk.CTkLabel(master=general_params_scrollable_frame, textvariable=title_size_var)
        # row separator 10
        dpi_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="Figure dpi:")
        dpi_strvar = tk.StringVar(value=self.controller.model.plot_general_settings['dpi'])
        dpi_entry = ErrEntry(master=general_params_scrollable_frame, textvariable=dpi_strvar, width=180)
        # row separator 12
        empty_frame1 = ctk.CTkFrame(master=general_params_scrollable_frame, fg_color='transparent', height=30)
        # row separator 14
        # row separator 15
        axes_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="AXES PARAMETERS", font=('', 20))
        # row separator 17
        # row separator 18
        both_axes_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="X AND Y AXIS")
        # row separator 20
        axes_font_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="Axes font:")
        axes_font_var = tk.StringVar(value=self.controller.model.plot_axes['axes font'])
        axes_font_cbbox = tk.ttk.Combobox(master=general_params_scrollable_frame, values=p.FONTS, state='readonly',
                                          textvariable=axes_font_var)
        
        # row separator 22
        x_major_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="X-AXIS")
        # row separator 24
        x_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="Label:")
        x_label_var = tk.StringVar(value=self.controller.model.plot_axes['x label'])
        x_label_entry = ErrEntry(master=general_params_scrollable_frame, width=200, textvariable=x_label_var)
        # row separator 26
        x_label_size = ctk.CTkLabel(master=general_params_scrollable_frame, text="Label size:")
        x_label_size_var = tk.IntVar(value=self.controller.model.plot_axes['x label size'])
        x_label_size_slider = ctk.CTkSlider(master=general_params_scrollable_frame, from_=8, to=32, number_of_steps=24,
                                            variable=x_label_size_var)
        x_label_size_value_label = ctk.CTkLabel(master=general_params_scrollable_frame, textvariable=x_label_size_var)
        # row separator 28
        xticks_rotation_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="Tick rotation:")
        xticks_rotation_var = tk.IntVar(value=self.controller.model.plot_axes['x ticks rotation'])
        xticks_rotation_slider = ctk.CTkSlider(master=general_params_scrollable_frame, from_=-180, to=180,
                                               number_of_steps=36,
                                               variable=xticks_rotation_var)
        xticks_rotation_value_label = ctk.CTkLabel(master=general_params_scrollable_frame,
                                                   textvariable=xticks_rotation_var)
        # row separator 30
        xticks_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="Tick size:")
        xticks_size_var = tk.IntVar(value=self.controller.model.plot_axes['x ticks size'])
        xticks_slider = ctk.CTkSlider(master=general_params_scrollable_frame, from_=8, to=32, number_of_steps=24,
                                      variable=xticks_size_var)
        xticks_value_label = ctk.CTkLabel(master=general_params_scrollable_frame, textvariable=xticks_size_var)
        
        # row separator 32
        y_major_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="Y-AXIS")
        # row separator 34
        y_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="Label:")
        y_label_var = tk.StringVar(value=self.controller.model.plot_axes['y label'])
        y_label_entry = ErrEntry(master=general_params_scrollable_frame, width=200, textvariable=y_label_var)
        # row separator 36
        y_label_size = ctk.CTkLabel(master=general_params_scrollable_frame, text="Label size:")
        y_label_size_var = tk.IntVar(value=self.controller.model.plot_axes['y label size'])
        y_label_size_slider = ctk.CTkSlider(master=general_params_scrollable_frame, from_=8, to=32, number_of_steps=24,
                                            variable=y_label_size_var)
        y_label_size_value_label = ctk.CTkLabel(master=general_params_scrollable_frame, textvariable=y_label_size_var)
        # row separator 38
        yticks_rotation_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="Tick rotation:")
        yticks_rotation_var = tk.IntVar(value=self.controller.model.plot_axes['y ticks rotation'])
        yticks_rotation_slider = ctk.CTkSlider(master=general_params_scrollable_frame, from_=-180, to=180,
                                               number_of_steps=36,
                                               variable=yticks_rotation_var)
        yticks_rotation_value_label = ctk.CTkLabel(master=general_params_scrollable_frame,
                                                   textvariable=yticks_rotation_var)
        # row separator 40
        yticks_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="Tick size:")
        yticks_size_var = tk.IntVar(value=self.controller.model.plot_axes['y ticks size'])
        yticks_slider = ctk.CTkSlider(master=general_params_scrollable_frame, from_=8, to=32, number_of_steps=24,
                                      variable=yticks_size_var)
        yticks_value_label = ctk.CTkLabel(master=general_params_scrollable_frame, textvariable=yticks_size_var)
        
        # separator row 42
        empty_frame2 = ctk.CTkFrame(master=general_params_scrollable_frame, fg_color='transparent', height=30)
        # row separator 44
        # row separator 45
        legend_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="LEGEND PARAMETERS", font=('', 20))
        # row separator 47
        # row separator 48
        show_legend_var = tk.IntVar(value=self.controller.model.plot_legend['show legend'])
        show_legend_ckbox = ctk.CTkCheckBox(master=general_params_scrollable_frame, text="Show legend",
                                            variable=show_legend_var)
        # row separator 50
        draggable_var = tk.BooleanVar(value=self.controller.model.plot_legend["legend draggable"])
        draggable_ckbox = ctk.CTkCheckBox(master=general_params_scrollable_frame, text="Draggable",
                                          variable=draggable_var, )
        # row separator 52
        legend_anchor_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="Anchor:")
        legend_anchor_var = tk.StringVar(value=self.controller.model.plot_legend["legend anchor"])
        legend_anchor_cbbox = tk.ttk.Combobox(master=general_params_scrollable_frame, values=p.LEGEND_POS,
                                              state='readonly',
                                              textvariable=legend_anchor_var)
        # row separator 54
        legend_alpha_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="Alpha:")
        legend_alpha_var = tk.DoubleVar(value=self.controller.model.plot_legend['legend alpha'])
        legend_alpha_slider = ctk.CTkSlider(master=general_params_scrollable_frame, from_=0, to=1, number_of_steps=10,
                                            variable=legend_alpha_var)
        legend_alpha_value_label = ctk.CTkLabel(master=general_params_scrollable_frame, textvariable=legend_alpha_var)
        # row separator 56
        legend_xpos_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="X position:")
        legend_xpos_var = tk.DoubleVar(value=self.controller.model.plot_legend['legend x pos'])
        legend_xpos_slider = ctk.CTkSlider(master=general_params_scrollable_frame, from_=0, to=1, number_of_steps=10,
                                           variable=legend_xpos_var)
        legend_xpos_value_label = ctk.CTkLabel(master=general_params_scrollable_frame, textvariable=legend_xpos_var)
        # row separator 58
        legend_ypos_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="Y position:")
        legend_ypos_var = tk.DoubleVar(value=self.controller.model.plot_legend['legend y pos'])
        legend_ypos_slider = ctk.CTkSlider(master=general_params_scrollable_frame, from_=0, to=1, number_of_steps=10,
                                           variable=legend_ypos_var)
        legend_ypos_value_label = ctk.CTkLabel(master=general_params_scrollable_frame, textvariable=legend_ypos_var)
        # row separator 60
        ncols_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="Number of columns:")
        ncols_var = tk.StringVar(value=self.controller.model.plot_legend["legend ncols"])
        ncols_entry = ErrEntry(master=general_params_scrollable_frame, width=50, textvariable=ncols_var)
        # row separator 62
        fontsize_var = tk.IntVar(value=self.controller.model.plot_legend['legend fontsize'])
        fontsize_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="Font size:")
        fontsize_slider = ctk.CTkSlider(master=general_params_scrollable_frame, from_=8, to=32, number_of_steps=24,
                                        variable=fontsize_var)
        fontsize_value_label = ctk.CTkLabel(master=general_params_scrollable_frame, textvariable=fontsize_var)
        # row separator 64
        
        # --------------- MANAGE SEPARATORS
        general_params_separators_indices = [0, 1, 3, 4, 6, 8, 10, 12, 14, 15, 17, 18, 20,
                                             22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44,
                                             45, 47, 48, 50, 52, 54, 56, 58, 60, 62, 64, ]
        general_params_vertical_separator_ranges = [(4, 13), (21, 22), (25, 32), (35, 42), (49, 64)]
        for r in range(general_params_separators_indices[-1] + 2):
            if r in general_params_separators_indices:
                sep = Separator(master=general_params_scrollable_frame, orient='h')
                sep.grid(row=r, column=0, columnspan=3, sticky='ew')
        for couple in general_params_vertical_separator_ranges:
            general_v_sep = Separator(master=general_params_scrollable_frame, orient='v')
            general_v_sep.grid(row=couple[0], column=1, rowspan=couple[1] - couple[0], sticky='ns')
        
        # --------------- MANAGE WIDGETS

        
        general_label.grid(row=2, column=0, columnspan=3, sticky='we')
        
        title_label.grid(row=5, column=0, sticky='w')
        title_entry.grid(row=5, column=2, sticky='we')
        title_font_label.grid(row=7, column=0, sticky='w')
        title_font_cbbox.grid(row=7, column=2, sticky='ew')
        title_size_label.grid(row=9, column=0, sticky="w")
        title_size_value_label.grid(row=9, column=0, sticky='e')
        title_size_slider.grid(row=9, column=2, sticky='we')
        dpi_label.grid(row=11, column=0, sticky="w")
        dpi_entry.grid(row=11, column=2, sticky="we")
        
        empty_frame1.grid(row=13, column=0, columnspan=3)
        axes_label.grid(row=16, column=0, columnspan=3, sticky='we')
        
        both_axes_label.grid(row=19, column=0, columnspan=3, sticky='we')
        axes_font_label.grid(row=21, column=0, sticky='w')
        axes_font_cbbox.grid(row=21, column=2, sticky='we')
        
        x_major_label.grid(row=23, column=0, columnspan=3, sticky='we')
        x_label.grid(row=25, column=0, sticky='w')
        x_label_entry.grid(row=25, column=2, sticky='we')
        x_label_size.grid(row=27, column=0, sticky='w')
        x_label_size_value_label.grid(row=27, column=0, sticky='e')
        x_label_size_slider.grid(row=27, column=2, sticky='we')
        xticks_rotation_label.grid(row=29, column=0, sticky='w')
        xticks_rotation_value_label.grid(row=29, column=0, sticky='e')
        xticks_rotation_slider.grid(row=29, column=2, sticky='we')
        xticks_label.grid(row=31, column=0, sticky='w')
        xticks_value_label.grid(row=31, column=0, sticky='e')
        xticks_slider.grid(row=31, column=2, sticky='we')
        
        y_major_label.grid(row=33, column=0, columnspan=3, sticky='we')
        y_label.grid(row=35, column=0, sticky='w')
        y_label_entry.grid(row=35, column=2, sticky='we')
        y_label_size.grid(row=37, column=0, sticky='w')
        y_label_size_value_label.grid(row=37, column=0, sticky='e')
        y_label_size_slider.grid(row=37, column=2, sticky='we')
        yticks_rotation_label.grid(row=39, column=0, sticky='w')
        yticks_rotation_value_label.grid(row=39, column=0, sticky='e')
        yticks_rotation_slider.grid(row=39, column=2, sticky='we')
        yticks_label.grid(row=41, column=0, sticky='w')
        yticks_value_label.grid(row=41, column=0, sticky='e')
        yticks_slider.grid(row=41, column=2, sticky='we')
        
        empty_frame2.grid(row=43, column=0, columnspan=3)
        legend_label.grid(row=46, column=0, columnspan=3, sticky="we")
        show_legend_ckbox.grid(row=49, column=0, sticky='w')
        draggable_ckbox.grid(row=51, column=0, sticky='w')
        legend_anchor_label.grid(row=53, column=0, sticky='w')
        legend_anchor_cbbox.grid(row=53, column=2, sticky='we')
        legend_alpha_label.grid(row=55, column=0, sticky='w')
        legend_alpha_value_label.grid(row=55, column=0, sticky='e')
        legend_alpha_slider.grid(row=55, column=2, sticky='we')
        legend_xpos_label.grid(row=57, column=0, sticky='w')
        legend_xpos_value_label.grid(row=57, column=0, sticky='e')
        legend_xpos_slider.grid(row=57, column=2, sticky='we')
        legend_ypos_label.grid(row=59, column=0, sticky='w')
        legend_ypos_value_label.grid(row=59, column=0, sticky='e')
        legend_ypos_slider.grid(row=59, column=2, sticky='we')
        ncols_label.grid(row=61, column=0, sticky='w')
        ncols_entry.grid(row=61, column=2, sticky='we')
        fontsize_label.grid(row=63, column=0, sticky='w')
        fontsize_value_label.grid(row=63, column=0, sticky='e')
        fontsize_slider.grid(row=63, column=2, sticky='we')

        
        # -------------- STORE WIDGETS
        self.vars["title"] = title_var
        self.entries["title"] = title_entry
        self.vars["title font"] = title_font_var
        self.cbboxes["title font"] = title_font_cbbox
        self.vars["title size"] = title_size_var
        self.sliders["title size"] = title_size_slider
        self.entries["dpi"] = dpi_entry
        self.vars["dpi"] = dpi_strvar
        
        self.entries["x label"] = x_label_entry
        self.vars['x label'] = x_label_var
        self.entries["y label"] = y_label_entry
        self.vars['y label'] = y_label_var
        self.vars["x label size"] = x_label_size_var
        self.sliders["x label size"] = x_label_size_slider
        self.vars["y label size"] = y_label_size_var
        self.sliders["y label size"] = y_label_size_slider
        self.vars["x ticks rotation"] = xticks_rotation_var
        self.sliders["x ticks rotation"] = xticks_rotation_slider
        self.vars["y ticks rotation"] = yticks_rotation_var
        self.sliders["y ticks rotation"] = yticks_rotation_slider
        self.vars["x ticks size"] = xticks_size_var
        self.sliders["x ticks size"] = xticks_slider
        self.vars["y ticks size"] = yticks_size_var
        self.sliders["y ticks size"] = yticks_slider
        self.cbboxes["axes font"] = axes_font_cbbox
        self.vars["axes font"] = axes_font_var
        
        self.ckboxes["show legend"] = show_legend_ckbox
        self.vars["show legend"] = show_legend_var
        self.ckboxes["legend draggable"] = draggable_ckbox
        self.vars["legend draggable"] = draggable_var
        self.cbboxes["legend anchor"] = legend_anchor_cbbox
        self.vars["legend anchor"] = legend_anchor_var
        self.vars["legend alpha"] = legend_alpha_var
        self.sliders["legend alpha"] = legend_alpha_slider
        self.vars["legend x pos"] = legend_xpos_var
        self.sliders["legend x pos"] = legend_xpos_slider
        self.vars["legend y pos"] = legend_ypos_var
        self.sliders["legend y pos"] = legend_ypos_slider
        self.vars["legend ncols"] = ncols_var
        self.entries["legend ncols"] = ncols_entry
        self.vars["legend fontsize"] = fontsize_var
        self.sliders["legend fontsize"] = fontsize_slider
        
        # --------------- CONFIGURE
        dpi_entry.configure(validate='focus',
                            validatecommand=(self.register(partial(self.main_view.is_positive_int,
                                                                   dpi_entry)), '%P'))
        ncols_entry.configure(validate='focus',
                              validatecommand=(self.register(partial(self.main_view.is_positive_int,
                                                                     ncols_entry)), '%P'))
        
        # --------------- TRACE
        title_var.trace("w", partial(self.controller.trace_vars_to_model, 'title'))
        title_size_var.trace("w", partial(self.controller.trace_vars_to_model, 'title size'))
        title_font_var.trace("w", partial(self.controller.trace_vars_to_model, 'title font'))
        dpi_strvar.trace("w", partial(self.controller.trace_vars_to_model, 'dpi'))
        
        x_label_var.trace("w", partial(self.controller.trace_vars_to_model, 'x label'))
        y_label_var.trace("w", partial(self.controller.trace_vars_to_model, 'y label'))
        x_label_size_var.trace("w", partial(self.controller.trace_vars_to_model, 'x label size'))
        y_label_size_var.trace("w", partial(self.controller.trace_vars_to_model, 'y label size'))
        xticks_rotation_var.trace("w", partial(self.controller.trace_vars_to_model, 'x ticks rotation'))
        yticks_rotation_var.trace("w", partial(self.controller.trace_vars_to_model, 'y ticks rotation'))
        xticks_size_var.trace("w", partial(self.controller.trace_vars_to_model, 'x ticks size'))
        yticks_size_var.trace("w", partial(self.controller.trace_vars_to_model, 'y ticks size'))
        axes_font_var.trace("w", partial(self.controller.trace_vars_to_model, 'axes font'))
        
        show_legend_var.trace("w", partial(self.controller.trace_vars_to_model, 'show legend'))
        fontsize_var.trace("w", partial(self.controller.trace_vars_to_model, 'legend fontsize'))
        legend_xpos_var.trace("w", partial(self.controller.trace_vars_to_model, 'legend x pos'))
        legend_ypos_var.trace("w", partial(self.controller.trace_vars_to_model, 'legend y pos'))
        legend_alpha_var.trace("w", partial(self.controller.trace_vars_to_model, 'legend alpha'))
        legend_anchor_var.trace("w", partial(self.controller.trace_vars_to_model, 'legend anchor'))
        ncols_var.trace("w", partial(self.controller.trace_vars_to_model, 'legend ncols'))
        draggable_var.trace("w", partial(self.controller.trace_vars_to_model, 'legend draggable'))
        
        
    def manage_specific_params_frame(self, specific_params_scrollable_frame):
        # row separator 0
        # row separator 1
        specific_label = ctk.CTkLabel(master=specific_params_scrollable_frame, text="SPECIFIC PARAMETERS", font=('', 20))
        
        # row separator 3
        # row separator 4
        load_model_var = tk.StringVar()
        load_model_entry = ErrEntry(master=specific_params_scrollable_frame, textvariable=load_model_var, state='disabled')
        load_model_button = ctk.CTkButton(master=specific_params_scrollable_frame, text="Load test classifier", )
        # row separator 6
        load_dataset_button = ctk.CTkButton(master=specific_params_scrollable_frame, text="Load dataset", )
        load_dataset_var = tk.StringVar()
        load_dataset_entry = ErrEntry(master=specific_params_scrollable_frame, textvariable=load_dataset_var, state='disabled')
        # row separator 8
        label_column_label = ctk.CTkLabel(master=specific_params_scrollable_frame, text='Label column:')
        label_column_var = tk.StringVar(value='None')
        label_column_cbbox = tk.ttk.Combobox(master=specific_params_scrollable_frame, values=['None', ], textvariable=label_column_var,
                                             state='readonly')
        # row separator 10
        training_label = ctk.CTkLabel(master=specific_params_scrollable_frame, text="Training")
        training_index_label = ctk.CTkLabel(master=specific_params_scrollable_frame, text="Training indices")
        # row separator 12
        training_frame = ctk.CTkScrollableFrame(master=specific_params_scrollable_frame, )
        training_frame.grid_columnconfigure(0, weight=10)
        training_frame.grid_columnconfigure(1, weight=1)
        training_frame.grid_columnconfigure(2, weight=10)
        # row separator 14
        testing_label = ctk.CTkLabel(master=specific_params_scrollable_frame, text="Testing")
        testing_index_label = ctk.CTkLabel(master=specific_params_scrollable_frame, text="Testing indices")

        # row separator 16
        testing_frame = ctk.CTkScrollableFrame(master=specific_params_scrollable_frame)
        testing_frame.grid_columnconfigure(0, weight=10)
        testing_frame.grid_columnconfigure(1, weight=1)
        testing_frame.grid_columnconfigure(2, weight=10)
        # row separator 18
        iteration_label = ctk.CTkLabel(master=specific_params_scrollable_frame, text='iterations: ')
        iteration_var = tk.IntVar(value=1)
        iteration_value_label = ctk.CTkLabel(master=specific_params_scrollable_frame, textvariable=iteration_var)
        iteration_slider = ctk.CTkSlider(master=specific_params_scrollable_frame, variable=iteration_var, from_=1, to=10, number_of_steps=10)

        # separator row 20
        select_all_button = ctk.CTkButton(master=specific_params_scrollable_frame, text="Select all",
                                          command=self.controller.select_all_test_targets)
        deselect_all_button = ctk.CTkButton(master=specific_params_scrollable_frame, text="Deselect all",
                                            command=self.controller.deselect_all_test_targets)
        
        # separator row 22
        annot_mode_label = ctk.CTkLabel(master=specific_params_scrollable_frame, text="Annotation mode:")
        annot_mode_var = ctk.StringVar(value=self.controller.model.plot_specific_settings["annot mode"])
        annot_mode_cbbox = tk.ttk.Combobox(master=specific_params_scrollable_frame, textvariable=annot_mode_var,
                                           values=["percent", "numeric"], state='readonly',)
        # separator row 24
        annot_size_label = ctk.CTkLabel(master=specific_params_scrollable_frame, text="Annotation size:")
        annot_size_var = ctk.IntVar(value=12)
        annot_size_slider = ctk.CTkSlider(master=specific_params_scrollable_frame, variable=annot_size_var,
                                          from_=8, to=32, number_of_steps=24,)
        annot_size_label_value = ctk.CTkLabel(master=specific_params_scrollable_frame, textvariable=annot_size_var)
        # separator row 26
        annot_font_label = ctk.CTkLabel(master=specific_params_scrollable_frame, text="Annotation font:")
        annot_font_var = ctk.StringVar(value=p.DEFAULT_FONT)
        annot_font_cbbox = tk.ttk.Combobox(master=specific_params_scrollable_frame, values=p.FONTS,
                                           textvariable=annot_font_var, state='readonly')
        #separator row 28
        only_cup_var = ctk.IntVar(value=0)
        only_cup_checkbox = ctk.CTkCheckBox(master=specific_params_scrollable_frame, variable=only_cup_var,
                                            text="Only CUP" )
        #separator row 30
        # --------------- MANAGE SEPARATORS
        general_params_separators_indices = [0, 1, 3, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
        general_params_vertical_separator_ranges = [(5, 9), (18, 25)]
        for r in range(general_params_separators_indices[-1] + 2):
            if r in general_params_separators_indices:
                sep = Separator(master=specific_params_scrollable_frame, orient='h')
                sep.grid(row=r, column=0, columnspan=3, sticky='ew')
        for couple in general_params_vertical_separator_ranges:
            general_v_sep = Separator(master=specific_params_scrollable_frame, orient='v')
            general_v_sep.grid(row=couple[0], column=1, rowspan=couple[1] - couple[0], sticky='ns')
            
        # -------- MANAGE WIDGETS
        
        specific_label.grid(row=2, column=0, columnspan=3, sticky='we')
        
        load_model_button.grid(row=5, column=0, sticky='e')
        load_model_entry.grid(row=5, column=2, sticky='we')
        load_dataset_button.grid(row=7, column=0, sticky='e')
        load_dataset_entry.grid(row=7, column=2, sticky='we')
        label_column_label.grid(row=9, column=0, sticky='w')
        label_column_cbbox.grid(row=9, column=2, sticky='we')
        training_label.grid(row=11, column=0, sticky='w')
        training_frame.grid(row=13, column=0, columnspan=3, sticky='nsew')
        training_index_label.grid(row=13, column=2, sticky='ew')
        testing_label.grid(row=15, column=0, sticky='w')
        testing_index_label.grid(row=15, column=2, sticky='ew')
        testing_frame.grid(row=17, column=0, columnspan=3, sticky='nsew')
        iteration_label.grid(row=19, column=0, sticky='w')
        iteration_value_label.grid(row=19, column=0, sticky='e')
        iteration_slider.grid(row=19, column=2, sticky='we')
        select_all_button.grid(row=21, column=0, sticky='w')
        deselect_all_button.grid(row=21, column=2, sticky='e')
        annot_mode_label.grid(row=23, column=0, sticky='w')
        annot_mode_cbbox.grid(row=23, column=2, sticky='we')
        annot_size_label.grid(row=25, column=0, sticky='w')
        annot_size_label_value.grid(row=25, column=0, sticky='e')
        annot_size_slider.grid(row=25, column=2, sticky='we')
        annot_font_label.grid(row=27, column=0, sticky='w')
        annot_font_cbbox.grid(row=27, column=2, sticky='we')
        only_cup_checkbox.grid(row=27, column=0, sticky='w', columnspan=2)
        
        
        # --------- STORE WIDGETS
        self.vars["load dataset"] = load_dataset_var
        self.vars["load clf"] = load_model_var
        self.vars["label column"] = label_column_var
        self.cbboxes["label column"] = label_column_cbbox
        self.scrollable_frames["training"] = training_frame
        self.scrollable_frames["testing"] = testing_frame
        self.vars['iterations'] = iteration_var
        
        self.vars["annot mode"] = annot_mode_var
        self.vars["annot size"] = annot_size_var
        self.vars["annot font"] = annot_font_var
        self.vars["annot only cup"] = only_cup_var
        
        
        # self.figures["confusion"] = (fig, ax)
        # self.canvas["confusion"] = canvas
        
        # --------------- CONFIGURE
        load_model_button.configure(command=self.controller.load_clf)
        load_dataset_button.configure(command=self.controller.load_dataset)
        
  
        load_model_entry.configure(validate='focus',
                                   validatecommand=(self.register(partial(self.main_view.is_valid_directory,
                                                                          load_model_entry)), '%P'))
        load_dataset_entry.configure(validate='focus',
                                     validatecommand=(self.register(partial(self.main_view.is_valid_directory,
                                                                            load_dataset_entry)), '%P'))
        # --------------- TRACE
        for key, widget in {"load dataset": load_dataset_var, "load clf": load_model_var,
                            "label column": label_column_var, "iterations": iteration_var,
                            "annot font": annot_font_var, "annot size": annot_size_var,
                            "annot mode": annot_mode_var, "annot only cup": only_cup_var}.items():
            widget.trace("w", partial(self.controller.trace_vars_to_model, key))
        label_column_var.trace("w", self.controller.trace_testing_labels)
    
    
    def manage_plot_frame(self, plot_frame):
        plot_frame.grid_rowconfigure(0, weight=20)
        plot_frame.grid_rowconfigure(1, weight=1)
        plot_frame.grid_columnconfigure(0, weight=20)
        
        # the figure that will contain the plot
        fig, ax = plt.subplots(figsize=(4, 4))
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        # canvas.draw()
        
        canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
        
        # creating the Matplotlib toolbar
        toolbar = NavigationToolbar2Tk(canvas,
                                       plot_frame, pack_toolbar=False)
        toolbar.update()
        toolbar.grid(row=1, column=0, sticky='we')

        self.canvas["confusion"] = canvas
        self.canvas["confusion toolbar"] = toolbar
        
        self.frames['plot frame'] = plot_frame
        self.figures["confusion"] = (fig, ax)

    def manage_execution_frame(self, execution_frame):

     
        # save_figure_button = ctk.CTkButton(master=execution_frame, text="Save figure", fg_color="green", width=120,
        #                                    height=40)
        draw_figure_button = ctk.CTkButton(master=execution_frame, text='Compute confusion', fg_color='tomato', width=120,
                                           height=40)
        # export_data_button = ctk.CTkButton(master=execution_frame, text="Export data", fg_color="green", width=120,
        #                                    height=40)
        update_figure_button = ctk.CTkButton(master=execution_frame, text="Update figure", width=120, height=40)
        
        
        # --------- MANAGE WIDGETS
        
        # save_figure_button.grid(row=0, column=2, padx=10, pady=10, sticky='e')
        # export_data_button.grid(row=1, column=0, padx=10, pady=10, sticky='w')
        draw_figure_button.grid(row=1, column=1, padx=10, pady=10)
        update_figure_button.grid(row=1, column=2, padx=10, pady=10, sticky='e')
        
        # ------------ CONFIGURE
        
        # export_data_button.configure(command=partial(self.controller.export_figure_data, self.figures["confusion"][1])) todo : export conf matrix data
        draw_figure_button.configure(command=self.controller.compute_confusion)
        update_figure_button.configure(command=self.controller.update_figure)
        
        # ------------- STORE
        # self.buttons["save figure"] = save_figure_button

        
    def manage_confusion_tab(self):
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_columnconfigure(2, weight=2)
        self.master.grid_rowconfigure(0, weight=3)
        self.master.grid_rowconfigure(1, weight=1)
        # --------------- GENERAL PARAMS FRAME
        general_params_scrollable_frame = ctk.CTkScrollableFrame(master=self.master, )
        general_params_scrollable_frame.grid_columnconfigure(0, weight=10)
        general_params_scrollable_frame.grid_columnconfigure(1, weight=1)
        general_params_scrollable_frame.grid_columnconfigure(2, weight=20)
        
        self.manage_general_params(general_params_scrollable_frame)
        general_params_scrollable_frame.grid(row=0, column=0, rowspan=2, sticky='nsew', padx=3)
        
        # --------------- SPECIFIC PARAMS FRAME
        specific_params_scrollable_frame = ctk.CTkScrollableFrame(master=self.master, )
        specific_params_scrollable_frame.grid_columnconfigure(0, weight=10)
        specific_params_scrollable_frame.grid_columnconfigure(1, weight=1)
        specific_params_scrollable_frame.grid_columnconfigure(2, weight=20)
        self.manage_specific_params_frame(specific_params_scrollable_frame)
        specific_params_scrollable_frame.grid(row=0, column=1, rowspan=2, sticky='nsew', padx=3)

        # --------------- PLOT FRAME
        plot_frame = ctk.CTkFrame(master=self.master, )
        self.manage_plot_frame(plot_frame)
        plot_frame.grid(row=0, column=2, sticky='nsew', padx=3, pady=3)

        # --------------- EXECUTION FRAME
        execution_frame = ctk.CTkFrame(master=self.master, )
        self.manage_execution_frame(execution_frame)
        execution_frame.grid(row=1, column=2, sticky='nsew', padx=3, pady=3)
