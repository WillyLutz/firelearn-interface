import tkinter as tk
from functools import partial
from tkinter import ttk

import customtkinter as ctk
from PIL import Image
from customtkinter import CTkLabel
from matplotlib import pyplot as plt
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from scripts import params as p
from scripts.CONTROLLER.PlotController import PlotController
from scripts.WIDGETS.ErrEntry import ErrEntry
from scripts.WIDGETS.ImageButton import ImageButton
from scripts.WIDGETS.Separator import Separator
from scripts.params import resource_path


class PlotView(ctk.CTkFrame):
    def __init__(self, app, master, parent_view):
        super().__init__(master=app)
        self.master = master
        self.app = app
        self.parent_view = parent_view
        self.main_view = self.parent_view.parent_view
        self.controller = PlotController(self, )
        
        self.entries = {}
        self.buttons = {}
        self.cbboxes = {}
        self.ckboxes = {}
        self.frames = {}
        self.vars = {}
        self.trace_ids = {}
        self.switches = {}
        self.sliders = {}
        self.checkboxes = {}
        self.textboxes = {}
        self.canvas = {}
        self.figures = {}
        self.scrollable_frames = {}
        self.image_buttons = {}
        self.separators = {}
        
        self.content_frame = ctk.CTkFrame(master=self.master)
        self.content_frame.place(relx=0.1, rely=0, relwidth=0.40, relheight=1)
        self.step_check = {"plotparams": 2, "axes": 2, "figname": 2, "legend": 2}
        
        self.ydata_subframes = {}
        self.manage_plot_tab()
        # self.axes_toplevel()
        # self.general_settings_toplevel()
        # self.legend_toplevel()
    
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
        n_xticks_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="Number of ticks:")
        n_xticks_var = tk.StringVar(value=self.controller.model.plot_axes['n x ticks'])
        n_xticks_entry = ErrEntry(master=general_params_scrollable_frame, textvariable=n_xticks_var)
        # row separator 34
        xticks_round_label: CTkLabel = ctk.CTkLabel(master=general_params_scrollable_frame, text="Round:")
        xticks_round_var = ctk.StringVar(value=self.controller.model.plot_axes["round x ticks"])
        xticks_round_entry = ErrEntry(master=general_params_scrollable_frame, textvariable=xticks_round_var)
        
        # row separator 36
        y_major_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="Y-AXIS")
        # row separator 38
        y_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="Label:")
        y_label_var = tk.StringVar(value=self.controller.model.plot_axes['y label'])
        y_label_entry = ErrEntry(master=general_params_scrollable_frame, width=200, textvariable=y_label_var)
        # row separator 40
        y_label_size = ctk.CTkLabel(master=general_params_scrollable_frame, text="Label size:")
        y_label_size_var = tk.IntVar(value=self.controller.model.plot_axes['y label size'])
        y_label_size_slider = ctk.CTkSlider(master=general_params_scrollable_frame, from_=8, to=32, number_of_steps=24,
                                            variable=y_label_size_var)
        y_label_size_value_label = ctk.CTkLabel(master=general_params_scrollable_frame, textvariable=y_label_size_var)
        # row separator 42
        yticks_rotation_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="Tick rotation:")
        yticks_rotation_var = tk.IntVar(value=self.controller.model.plot_axes['y ticks rotation'])
        yticks_rotation_slider = ctk.CTkSlider(master=general_params_scrollable_frame, from_=-180, to=180,
                                               number_of_steps=36,
                                               variable=yticks_rotation_var)
        yticks_rotation_value_label = ctk.CTkLabel(master=general_params_scrollable_frame,
                                                   textvariable=yticks_rotation_var)
        # row separator 44
        yticks_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="Tick size:")
        yticks_size_var = tk.IntVar(value=self.controller.model.plot_axes['y ticks size'])
        yticks_slider = ctk.CTkSlider(master=general_params_scrollable_frame, from_=8, to=32, number_of_steps=24,
                                      variable=yticks_size_var)
        yticks_value_label = ctk.CTkLabel(master=general_params_scrollable_frame, textvariable=yticks_size_var)
        # separator row 46
        n_yticks_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="Number of ticks:")
        n_yticks_var = tk.StringVar(value=self.controller.model.plot_axes['n y ticks'])
        n_yticks_entry = ErrEntry(master=general_params_scrollable_frame, textvariable=n_yticks_var)
        # separator row 48
        yticks_round_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="Round:")
        yticks_round_var = ctk.StringVar(value=self.controller.model.plot_axes["round y ticks"])
        yticks_round_entry = ErrEntry(master=general_params_scrollable_frame, textvariable=yticks_round_var)
        # separator row 50
        empty_frame2 = ctk.CTkFrame(master=general_params_scrollable_frame, fg_color='transparent', height=30)
        # row separator 52
        # row separator 53
        legend_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="LEGEND PARAMETERS", font=('', 20))
        # row separator 55
        # row separator 56
        show_legend_var = tk.IntVar(value=self.controller.model.plot_legend['show legend'])
        show_legend_ckbox = ctk.CTkCheckBox(master=general_params_scrollable_frame, text="Show legend",
                                            variable=show_legend_var)
        # row separator 58
        draggable_var = tk.BooleanVar(value=self.controller.model.plot_legend["legend draggable"])
        draggable_ckbox = ctk.CTkCheckBox(master=general_params_scrollable_frame, text="Draggable",
                                          variable=draggable_var, )
        # row separator 60
        legend_anchor_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="Anchor:")
        legend_anchor_var = tk.StringVar(value=self.controller.model.plot_legend["legend anchor"])
        legend_anchor_cbbox = tk.ttk.Combobox(master=general_params_scrollable_frame, values=p.LEGEND_POS,
                                              state='readonly',
                                              textvariable=legend_anchor_var)
        # row separator 62
        legend_alpha_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="Alpha:")
        legend_alpha_var = tk.DoubleVar(value=self.controller.model.plot_legend['legend alpha'])
        legend_alpha_slider = ctk.CTkSlider(master=general_params_scrollable_frame, from_=0, to=1, number_of_steps=10,
                                            variable=legend_alpha_var)
        legend_alpha_value_label = ctk.CTkLabel(master=general_params_scrollable_frame, textvariable=legend_alpha_var)
        # row separator 64
        legend_xpos_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="X position:")
        legend_xpos_var = tk.DoubleVar(value=self.controller.model.plot_legend['legend x pos'])
        legend_xpos_slider = ctk.CTkSlider(master=general_params_scrollable_frame, from_=0, to=1, number_of_steps=10,
                                           variable=legend_xpos_var)
        legend_xpos_value_label = ctk.CTkLabel(master=general_params_scrollable_frame, textvariable=legend_xpos_var)
        # row separator 66
        legend_ypos_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="Y position:")
        legend_ypos_var = tk.DoubleVar(value=self.controller.model.plot_legend['legend y pos'])
        legend_ypos_slider = ctk.CTkSlider(master=general_params_scrollable_frame, from_=0, to=1, number_of_steps=10,
                                           variable=legend_ypos_var)
        legend_ypos_value_label = ctk.CTkLabel(master=general_params_scrollable_frame, textvariable=legend_ypos_var)
        # row separator 68
        ncols_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="Number of columns:")
        ncols_var = tk.StringVar(value=self.controller.model.plot_legend["legend ncols"])
        ncols_entry = ErrEntry(master=general_params_scrollable_frame, width=50, textvariable=ncols_var)
        # row separator 70
        fontsize_var = tk.IntVar(value=self.controller.model.plot_legend['legend fontsize'])
        fontsize_label = ctk.CTkLabel(master=general_params_scrollable_frame, text="Font size:")
        fontsize_slider = ctk.CTkSlider(master=general_params_scrollable_frame, from_=8, to=32, number_of_steps=24,
                                        variable=fontsize_var)
        fontsize_value_label = ctk.CTkLabel(master=general_params_scrollable_frame, textvariable=fontsize_var)
        # row separator 72
        
        # --------------- MANAGE SEPARATORS
        general_params_separators_indices = [0, 1, 3, 4, 6, 8, 10, 12, 14, 15, 17, 18, 20,
                                             22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42,
                                             44, 46, 48, 50, 52, 53, 55, 56, 58, 60, 62, 64, 66, 68, 70, 72]
        general_params_vertical_separator_ranges = [(4, 13), (21, 22), (25, 36), (39, 50), (56, 73)]
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
        n_xticks_label.grid(row=33, column=0, sticky='w')
        n_xticks_entry.grid(row=33, column=2, sticky='we')
        xticks_round_label.grid(row=35, column=0, sticky='w')
        xticks_round_entry.grid(row=35, column=2, sticky='we')
        
        y_major_label.grid(row=37, column=0, columnspan=3, sticky='we')
        y_label.grid(row=39, column=0, sticky='w')
        y_label_entry.grid(row=39, column=2, sticky='we')
        y_label_size.grid(row=41, column=0, sticky='w')
        y_label_size_value_label.grid(row=41, column=0, sticky='e')
        y_label_size_slider.grid(row=41, column=2, sticky='we')
        yticks_rotation_label.grid(row=43, column=0, sticky='w')
        yticks_rotation_value_label.grid(row=43, column=0, sticky='e')
        yticks_rotation_slider.grid(row=43, column=2, sticky='we')
        yticks_label.grid(row=45, column=0, sticky='w')
        yticks_value_label.grid(row=45, column=0, sticky='e')
        yticks_slider.grid(row=45, column=2, sticky='we')
        n_yticks_label.grid(row=47, column=0, sticky='w')
        n_yticks_entry.grid(row=47, column=2, sticky='we')
        yticks_round_label.grid(row=49, column=0, sticky='w')
        yticks_round_entry.grid(row=49, column=2, sticky='we')
        
        empty_frame2.grid(row=51, column=0, columnspan=3)
        legend_label.grid(row=54, column=0, columnspan=3, sticky="we")
        show_legend_ckbox.grid(row=57, column=0, sticky='w')
        draggable_ckbox.grid(row=59, column=0, sticky='w')
        legend_anchor_label.grid(row=61, column=0, sticky='w')
        legend_anchor_cbbox.grid(row=61, column=2, sticky='we')
        legend_alpha_label.grid(row=63, column=0, sticky='w')
        legend_alpha_value_label.grid(row=63, column=0, sticky='e')
        legend_alpha_slider.grid(row=63, column=2, sticky='we')
        legend_xpos_label.grid(row=65, column=0, sticky='w')
        legend_xpos_value_label.grid(row=65, column=0, sticky='e')
        legend_xpos_slider.grid(row=65, column=2, sticky='we')
        legend_ypos_label.grid(row=67, column=0, sticky='w')
        legend_ypos_value_label.grid(row=67, column=0, sticky='e')
        legend_ypos_slider.grid(row=67, column=2, sticky='we')
        ncols_label.grid(row=69, column=0, sticky='w')
        ncols_entry.grid(row=69, column=2, sticky='we')
        fontsize_label.grid(row=71, column=0, sticky='w')
        fontsize_value_label.grid(row=71, column=0, sticky='e')
        fontsize_slider.grid(row=71, column=2, sticky='we')
        
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
        self.vars["n x ticks"] = n_xticks_var
        self.vars["n y ticks"] = n_yticks_var
        self.vars["round x ticks"] = xticks_round_var
        self.vars["round y ticks"] = yticks_round_var
        self.entries["round x ticks"] = xticks_round_entry
        self.entries["round y ticks"] = yticks_round_entry
        self.entries["n x ticks"] = n_xticks_entry
        self.entries["n y ticks"] = n_yticks_entry
        
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
        n_xticks_entry.configure(validate='focus',
                                 validatecommand=(self.register(partial(self.main_view.is_positive_int,
                                                                        n_xticks_entry)), '%P'))
        n_yticks_entry.configure(validate='focus',
                                 validatecommand=(self.register(partial(self.main_view.is_positive_int,
                                                                        n_yticks_entry)), '%P'))
        xticks_round_entry.configure(validate='focus',
                                     validatecommand=(self.register(partial(self.main_view.is_positive_int,
                                                                            xticks_round_entry)), '%P'))
        yticks_round_entry.configure(validate='focus',
                                     validatecommand=(self.register(partial(self.main_view.is_positive_int,
                                                                            yticks_round_entry)), '%P'))
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
        n_yticks_var.trace("w", partial(self.controller.trace_vars_to_model, 'n y ticks'))
        n_xticks_var.trace("w", partial(self.controller.trace_vars_to_model, 'n x ticks'))
        xticks_round_var.trace("w", partial(self.controller.trace_vars_to_model, 'round x ticks'))
        yticks_round_var.trace("w", partial(self.controller.trace_vars_to_model, 'round y ticks'))
        
        show_legend_var.trace("w", partial(self.controller.trace_vars_to_model, 'show legend'))
        fontsize_var.trace("w", partial(self.controller.trace_vars_to_model, 'legend fontsize'))
        legend_xpos_var.trace("w", partial(self.controller.trace_vars_to_model, 'legend x pos'))
        legend_ypos_var.trace("w", partial(self.controller.trace_vars_to_model, 'legend y pos'))
        legend_alpha_var.trace("w", partial(self.controller.trace_vars_to_model, 'legend alpha'))
        legend_anchor_var.trace("w", partial(self.controller.trace_vars_to_model, 'legend anchor'))
        ncols_var.trace("w", partial(self.controller.trace_vars_to_model, 'legend ncols'))
        draggable_var.trace("w", partial(self.controller.trace_vars_to_model, 'legend draggable'))
    
    def manage_plot_frame(self, plot_frame):
        plot_frame.grid_rowconfigure(0, weight=20)
        plot_frame.grid_rowconfigure(1, weight=1)
        plot_frame.grid_columnconfigure(0, weight=20)
        
        # the figure that will contain the plot
        fig, ax = plt.subplots(figsize=(3, 3))
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        
        canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
        
        # creating the Matplotlib toolbar
        toolbar = NavigationToolbar2Tk(canvas,
                                       plot_frame, pack_toolbar=False)
        toolbar.update()
        toolbar.grid(row=1, column=0, sticky='we')
        
        self.canvas["plot"] = canvas
        self.canvas["plot toolbar"] = toolbar
        
        self.frames['plot frame'] = plot_frame
        self.figures["plot"] = (fig, ax)
    
    def manage_execution_frame(self, execution_frame):
        
        load_config_button = ctk.CTkButton(master=execution_frame, text="Load config", fg_color="lightslategray",
                                           width=120, height=40)
        save_config_button = ctk.CTkButton(master=execution_frame, text="Save config", fg_color="lightslategray",
                                           width=120, height=40)
        draw_figure_button = ctk.CTkButton(master=execution_frame, text='Draw figure', fg_color='tomato',
                                           width=120,
                                           height=40)
        export_data_button = ctk.CTkButton(master=execution_frame, text="Export data", fg_color="green", width=120,
                                           height=40)
        
        # --------- MANAGE WIDGETS
        
        load_config_button.grid(row=0, column=0, padx=10, pady=10, sticky='w')
        save_config_button.grid(row=0, column=1, padx=10, pady=10)
        export_data_button.grid(row=1, column=0, padx=10, pady=10, sticky='w')
        draw_figure_button.grid(row=1, column=1, padx=10, pady=10)
        
        # ------------ CONFIGURE
        
        save_config_button.configure(command=self.controller.save_config)
        load_config_button.configure(command=self.controller.load_config)
        draw_figure_button.configure(command=self.controller.draw_figure)
        
        # ------------- STORE
    
    def manage_specific_params_frame(self, specific_params_scrollable_frame):
        
        # row separator 0
        # row separator 1
        
        specific_label = ctk.CTkLabel(master=specific_params_scrollable_frame, text="SPECIFIC PARAMETERS",
                                      font=('', 20))
        
        # row separator 3
        # row separator 4
        load_dataset_button = ctk.CTkButton(master=specific_params_scrollable_frame, text="Load dataset:")
        load_dataset_var = tk.StringVar()
        load_dataset_entry = ErrEntry(master=specific_params_scrollable_frame, state='disabled', textvariable=load_dataset_var)
        # row separator 6
        xdata_label = ctk.CTkLabel(master=specific_params_scrollable_frame, text="X-data column:")
        xdata_var = tk.StringVar(value="None")
        xdata_cbbox = tk.ttk.Combobox(master=specific_params_scrollable_frame, values=["None", ], state='readonly',
                                      textvariable=xdata_var)
        # row separator 8
        ydata_label = ctk.CTkLabel(master=specific_params_scrollable_frame, text="Y-data column:")
        add_ydata_button = ctk.CTkButton(master=specific_params_scrollable_frame, text="+", width=25, height=25, state='normal')
        subtract_ydata_button = ctk.CTkButton(master=specific_params_scrollable_frame, text="-", width=25, height=25,
                                              state='normal')
        
        
        
        # --------------- MANAGE SEPARATORS
        general_params_separators_indices = [0, 1, 3, 4, 6, 8, 10,]
        general_params_vertical_separator_ranges = [(5, 10), ]
        for r in range(general_params_separators_indices[-1] + 2):
            if r in general_params_separators_indices:
                sep = Separator(master=specific_params_scrollable_frame, orient='h')
                sep.grid(row=r, column=0, columnspan=3, sticky='ew')
        for couple in general_params_vertical_separator_ranges:
            general_v_sep = Separator(master=specific_params_scrollable_frame, orient='v')
            general_v_sep.grid(row=couple[0], column=1, rowspan=couple[1] - couple[0], sticky='ns')
        
        # -------- MANAGE WIDGETS
        
        specific_label.grid(row=2, column=0, columnspan=3, sticky='we')
        load_dataset_button.grid(row=5, column=0, sticky="we")
        load_dataset_entry.grid(row=5, column=2, sticky='we')
        xdata_label.grid(row=7, column=0, sticky='w')
        xdata_cbbox.grid(row=7, column=2, sticky='we')
        ydata_label.grid(row=9, column=0, sticky='w')
        add_ydata_button.grid(row=9, column=2, sticky='e')
        subtract_ydata_button.grid(row=9, column=2, sticky='w')
        
        
        
        # --------- STORE WIDGETS
        self.buttons["load dataset"] = load_dataset_button
        self.vars["load dataset"] = load_dataset_var
        self.entries["load dataset"] = load_dataset_entry
        self.cbboxes["xdata"] = xdata_cbbox
        self.vars["xdata"] = xdata_var
        self.buttons[f"add ydata"] = add_ydata_button
        self.buttons[f"subtract ydata"] = subtract_ydata_button
        
        # --------------- CONFIGURE
        add_ydata_button.configure(command=partial(self.controller.add_ydata, specific_params_scrollable_frame))
        subtract_ydata_button.configure(command=partial(self.controller.remove_ydata))
        load_dataset_button.configure(command=self.controller.load_plot_dataset)
        
        # ---- TRACE
        xdata_var.trace("w", partial(self.controller.trace_vars_to_model, 'xdata'))
        
        for key, widget in {}.items():
            widget.trace("w", partial(self.controller.trace_vars_to_model, key))
            
    def manage_plot_tab(self):
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
        
    def deprecated(self):
        # ---------- VARIABLE CONTENT
        plotparams_frame = ctk.CTkFrame(master=self.content_frame)
        axes_frame = ctk.CTkFrame(master=self.content_frame)
        legend_frame = ctk.CTkFrame(master=self.content_frame)
        figname_frame = ctk.CTkFrame(master=self.content_frame)
        
        # ----------- PLOT
        plot_frame = ctk.CTkFrame(master=self.master)
        # fig, ax = plt.subplots(figsize=(p.DEFAULT_FIGUREWIDTH, p.DEFAULT_FIGUREHEIGHT))
        # canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        draw_figure_button = ctk.CTkButton(master=self.master, text='Draw figure',)
        
        
        self.frames["axes"] = axes_frame
        self.frames["plotparams"] = plotparams_frame
        self.frames["legend"] = legend_frame
        self.frames["figname"] = figname_frame
        
        # ------------ WIDGET MANAGEMENT
        draw_figure_button.place(anchor=tk.SE, relx=0.98, rely=0.98, relheight=0.08)
        
        plot_frame.place(relx=0.55, rely=0, relheight=0.9, relwidth=0.45)
        
        # ------ MANAGE WIDGETS
        
        # canvas.get_tk_widget().place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.96)
        #
        # self.figures["plot"] = (fig, ax)
        # self.canvas["plot"] = canvas
        self.buttons["draw figure"] = draw_figure_button
        
        # ---------------- CONFIGURE
        draw_figure_button.configure(command=self.controller.draw_figure)
        
        self.generate_plotparams_content()
        self.generate_axes_content()
        self.generate_legend_content()
        self.generate_figname_content()
        self.show_frame("plotparams")
    
    def generate_plotparams_content(self):
        plotparams_frame = self.frames["plotparams"]
        
        # --------------- INIT FRAME
       
        
        # ----- Y DATA
        ydata_frame = ctk.CTkScrollableFrame(master=plotparams_frame)
        ydata_frame.grid_columnconfigure(0, weight=1)
        n_ydata = self.controller.model.n_ydata
        
        # ----------------- MANAGE WIDGETS
       
        ydata_frame.place(relx=0.01, rely=0.2, relwidth=0.98, relheight=0.8)
        
        self.buttons["load dataset"] = load_dataset_button
        self.vars["load dataset"] = load_dataset_var
        self.entries["load dataset"] = load_dataset_entry
        self.cbboxes["xdata"] = xdata_cbbox
        self.vars["xdata"] = xdata_var
        self.buttons[f"add ydata"] = add_ydata_button
        self.buttons[f"subtract ydata"] = subtract_ydata_button
        self.scrollable_frames["ydata"] = ydata_frame
        
        # ---------------- CONFIGURE
        add_ydata_button.configure(command=partial(self.controller.add_ydata, ydata_frame))
        subtract_ydata_button.configure(command=partial(self.controller.remove_ydata))
        load_dataset_button.configure(command=self.controller.load_plot_dataset)
        
        # ---- TRACE
        xdata_var.trace("w", partial(self.controller.trace_vars_to_model, 'xdata'))
        
        # --------- ENTRY VALIDATION
        
    
    def generate_axes_content(self):
        axes_frame = self.frames["axes"]
        
        x_major_label = ctk.CTkLabel(master=axes_frame, text="X-AXIS")
        y_major_label = ctk.CTkLabel(master=axes_frame, text="Y-AXIS")
        
        x_label = ctk.CTkLabel(master=axes_frame, text="Label:")
        x_label_var = tk.StringVar(value=self.controller.model.plot_axes['x label'])
        x_label_entry = ErrEntry(master=axes_frame, width=200, textvariable=x_label_var)
        
        y_label = ctk.CTkLabel(master=axes_frame, text="Label:")
        y_label_var = tk.StringVar(value=self.controller.model.plot_axes['y label'])
        y_label_entry = ErrEntry(master=axes_frame, width=200, textvariable=y_label_var)
        
        x_size_label = ctk.CTkLabel(master=axes_frame, text="Label size:")
        x_label_size_var = tk.IntVar(value=self.controller.model.plot_axes['x label size'])
        x_label_slider = ctk.CTkSlider(master=axes_frame, from_=8, to=32, number_of_steps=24,
                                       variable=x_label_size_var)
        x_label_value_label = ctk.CTkLabel(master=axes_frame, textvariable=x_label_size_var)
        
        y_size_label = ctk.CTkLabel(master=axes_frame, text="Label size:")
        y_label_size_var = tk.IntVar(value=self.controller.model.plot_axes['y label size'])
        y_label_slider = ctk.CTkSlider(master=axes_frame, from_=8, to=32, number_of_steps=24,
                                       variable=y_label_size_var)
        y_label_value_label = ctk.CTkLabel(master=axes_frame, textvariable=y_label_size_var)
        
        # -----TICKS
        
        n_xticks_label = ctk.CTkLabel(master=axes_frame, text="Number of ticks:")
        n_xticks_var = tk.StringVar(value=self.controller.model.plot_axes['n x ticks'])
        n_xticks_entry = ErrEntry(master=axes_frame, textvariable=n_xticks_var)
        
        n_yticks_label = ctk.CTkLabel(master=axes_frame, text="Number of ticks:")
        n_yticks_var = tk.StringVar(value=self.controller.model.plot_axes['n y ticks'])
        n_yticks_entry = ErrEntry(master=axes_frame, textvariable=n_yticks_var)
        
        xticks_rotation_label = ctk.CTkLabel(master=axes_frame, text="Tick rotation:")
        xticks_rotation_var = tk.IntVar(value=self.controller.model.plot_axes['x ticks rotation'])
        xticks_rotation_slider = ctk.CTkSlider(master=axes_frame, from_=-180, to=180, number_of_steps=36,
                                               variable=xticks_rotation_var)
        xticks_rotation_value_label = ctk.CTkLabel(master=axes_frame, textvariable=xticks_rotation_var)
        
        yticks_rotation_label = ctk.CTkLabel(master=axes_frame, text="Tick rotation:")
        yticks_rotation_var = tk.IntVar(value=self.controller.model.plot_axes['y ticks rotation'])
        yticks_rotation_slider = ctk.CTkSlider(master=axes_frame, from_=-180, to=180, number_of_steps=36,
                                               variable=yticks_rotation_var)
        yticks_rotation_value_label = ctk.CTkLabel(master=axes_frame, textvariable=yticks_rotation_var)
        
        xticks_label = ctk.CTkLabel(master=axes_frame, text="Tick size:")
        xticks_size_var = tk.IntVar(value=self.controller.model.plot_axes['x ticks size'])
        xticks_slider = ctk.CTkSlider(master=axes_frame, from_=8, to=32, number_of_steps=24,
                                      variable=xticks_size_var)
        xticks_value_label = ctk.CTkLabel(master=axes_frame, textvariable=xticks_size_var)
        
        yticks_label = ctk.CTkLabel(master=axes_frame, text="Tick size:")
        yticks_size_var = tk.IntVar(value=self.controller.model.plot_axes['y ticks size'])
        yticks_slider = ctk.CTkSlider(master=axes_frame, from_=8, to=32, number_of_steps=24,
                                      variable=yticks_size_var)
        yticks_value_label = ctk.CTkLabel(master=axes_frame, textvariable=yticks_size_var)
        
        round_xticks_label = ctk.CTkLabel(master=axes_frame, text="Round ticks:")
        round_xticks_strvar = tk.StringVar(value=self.controller.model.plot_axes['round x ticks'])
        round_xticks_entry = ErrEntry(master=axes_frame, textvariable=round_xticks_strvar)
        
        round_yticks_label = ctk.CTkLabel(master=axes_frame, text="Round ticks:")
        round_yticks_strvar = tk.StringVar(value=self.controller.model.plot_axes['round y ticks'])
        round_yticks_entry = ErrEntry(master=axes_frame, textvariable=round_yticks_strvar)
        
        general_label = ctk.CTkLabel(master=axes_frame, text='GENERAL')
        
        axes_font_label = ctk.CTkLabel(master=axes_frame, text="Axes font:")
        axes_font_var = tk.StringVar(value=self.controller.model.plot_axes['axes font'])
        axes_font_cbbox = tk.ttk.Combobox(master=axes_frame, values=p.FONTS, state='readonly',
                                          textvariable=axes_font_var)
        x_major_label.place(anchor=tk.CENTER, x=125, rely=0.03)
        y_major_label.place(anchor=tk.CENTER, x=375, rely=0.03)
        x_label.place(relx=0, rely=0.07)
        x_label_entry.place_errentry(relx=0, rely=0.13)
        y_label.place(relx=0.5, rely=0.07)
        y_label_entry.place_errentry(relx=0.5, rely=0.13)
        x_label_value_label.place(x=100, rely=0.19)
        x_label_slider.place(relx=0, rely=0.25, relwidth=0.4)
        x_size_label.place(relx=0, rely=0.19)
        y_label_value_label.place(x=350, rely=0.19)
        y_label_slider.place(relx=0.5, rely=0.25, relwidth=0.4)
        y_size_label.place(relx=0.5, rely=0.19)
        n_xticks_label.place(relx=0, rely=0.37)
        n_xticks_entry.place_errentry(relx=0, rely=0.43, relwidth=0.2)
        n_yticks_label.place(relx=0.5, rely=0.37)
        n_yticks_entry.place_errentry(relx=0.5, rely=0.43, relwidth=0.2)
        xticks_rotation_slider.place(relx=0, rely=0.54, relwidth=0.4)
        xticks_rotation_label.place(relx=0, rely=0.48)
        xticks_rotation_value_label.place(x=100, rely=0.48)
        yticks_rotation_slider.place(relx=0.5, rely=0.54, relwidth=0.4)
        yticks_rotation_label.place(relx=0.5, rely=0.48)
        yticks_rotation_value_label.place(x=350, rely=0.48)
        xticks_label.place(relx=0, rely=0.6)
        xticks_slider.place(relx=0, rely=0.64, relwidth=0.4)
        xticks_value_label.place(x=100, rely=0.6)
        yticks_label.place(relx=0.5, rely=0.6)
        yticks_slider.place(relx=0.5, rely=0.64, relwidth=0.4)
        yticks_value_label.place(x=350, rely=0.6)
        round_xticks_label.place(relx=0, rely=0.70)
        round_xticks_entry.place_errentry(relx=0, rely=0.76, relwidth=0.2)
        round_yticks_label.place(relx=0.5, rely=0.70)
        round_yticks_entry.place_errentry(relx=0.5, rely=0.76, relwidth=0.2)
        general_label.place(relx=0, rely=0.84)
        axes_font_label.place(relx=0, rely=0.88)
        axes_font_cbbox.place(relx=0, rely=0.92, relwidth=0.4)
        
        self.entries["x label"] = x_label_entry
        self.vars['x label'] = x_label_var
        self.entries["y label"] = y_label_entry
        self.vars['y label'] = y_label_var
        self.vars["x label size"] = x_label_size_var
        self.sliders["x label size"] = x_label_slider
        self.vars["y label size"] = y_label_size_var
        self.sliders["y label size"] = y_label_slider
        self.entries["n x ticks"] = n_xticks_entry
        self.vars["n x ticks"] = n_xticks_var
        self.entries["n y ticks"] = n_yticks_entry
        self.vars["n y ticks"] = n_yticks_var
        self.vars["x ticks rotation"] = xticks_rotation_var
        self.sliders["x ticks rotation"] = xticks_rotation_slider
        self.vars["y ticks rotation"] = yticks_rotation_var
        self.sliders["y ticks rotation"] = yticks_rotation_slider
        self.vars["x ticks size"] = xticks_size_var
        self.sliders["x ticks size"] = xticks_slider
        self.vars["y ticks size"] = yticks_size_var
        self.sliders["y ticks size"] = yticks_slider
        self.entries["round x ticks"] = round_xticks_entry
        self.vars["round x ticks"] = round_xticks_strvar
        self.entries["round y ticks"] = round_yticks_entry
        self.vars["round y ticks"] = round_yticks_strvar
        self.cbboxes["axes font"] = axes_font_cbbox
        self.vars["axes font"] = axes_font_var
        
        # ----- TRACE
        x_label_var.trace("w", partial(self.controller.trace_vars_to_model, 'x label'))
        y_label_var.trace("w", partial(self.controller.trace_vars_to_model, 'y label'))
        x_label_size_var.trace("w", partial(self.controller.trace_vars_to_model, 'x label size'))
        y_label_size_var.trace("w", partial(self.controller.trace_vars_to_model, 'y label size'))
        n_xticks_var.trace("w", partial(self.controller.trace_vars_to_model, 'n x ticks'))
        n_yticks_var.trace("w", partial(self.controller.trace_vars_to_model, 'n y ticks'))
        xticks_rotation_var.trace("w", partial(self.controller.trace_vars_to_model, 'x ticks rotation'))
        yticks_rotation_var.trace("w", partial(self.controller.trace_vars_to_model, 'y ticks rotation'))
        xticks_size_var.trace("w", partial(self.controller.trace_vars_to_model, 'x ticks size'))
        yticks_size_var.trace("w", partial(self.controller.trace_vars_to_model, 'y ticks size'))
        round_xticks_strvar.trace("w", partial(self.controller.trace_vars_to_model, 'round x ticks'))
        round_yticks_strvar.trace("w", partial(self.controller.trace_vars_to_model, 'round y ticks'))
        axes_font_var.trace("w", partial(self.controller.trace_vars_to_model, 'axes font'))
        
        n_xticks_entry.configure(validate='focus',
                                 validatecommand=(self.register(partial(self.main_view.is_positive_int,
                                                                        n_xticks_entry)), '%P'))
        n_yticks_entry.configure(validate='focus',
                                 validatecommand=(self.register(partial(self.main_view.is_positive_int,
                                                                        n_yticks_entry)), '%P'))
        round_xticks_entry.configure(validate='focus',
                                     validatecommand=(self.register(partial(self.main_view.is_positive_int,
                                                                            round_xticks_entry)), '%P'))
        round_yticks_entry.configure(validate='focus',
                                     validatecommand=(self.register(partial(self.main_view.is_positive_int,
                                                                            round_yticks_entry)), '%P'))
    
    def generate_legend_content(self):
        legend_frame = self.frames["legend"]
        
        # ---- title
        title_label = ctk.CTkLabel(master=legend_frame, text="Title:")
        title_var = tk.StringVar()
        title_var.set(self.controller.model.plot_general_settings['title'])
        title_entry = ErrEntry(master=legend_frame, width=180, textvariable=title_var)
        title_font_var = tk.StringVar()
        title_font_var.set(self.controller.model.plot_general_settings['title font'])
        title_font_label = ctk.CTkLabel(master=legend_frame, text="Title font:")
        title_font_cbbox = tk.ttk.Combobox(master=legend_frame, values=p.FONTS, state='readonly',
                                           textvariable=title_font_var)
        title_size_var = tk.IntVar(value=self.controller.model.plot_general_settings['title size'])
        title_size_label = ctk.CTkLabel(master=legend_frame, text="Title size:")
        title_size_slider = ctk.CTkSlider(master=legend_frame, from_=8, to=32, number_of_steps=24,
                                          variable=title_size_var)
        title_size_value_label = ctk.CTkLabel(master=legend_frame, textvariable=title_size_var)
        dpi_label = ctk.CTkLabel(master=legend_frame, text="Figure dpi:")
        dpi_strvar = tk.StringVar()
        dpi_strvar.set(self.controller.model.plot_general_settings['dpi'])
        dpi_entry = ErrEntry(master=legend_frame, textvariable=dpi_strvar, width=180)
        
        # ---- legend
        show_legend_var = tk.IntVar(value=self.controller.model.plot_legend['show legend'])
        show_legend_switch = ctk.CTkSwitch(master=legend_frame, text="Show legend", variable=show_legend_var)
        
        draggable_var = tk.BooleanVar(value=self.controller.model.plot_legend["legend draggable"])
        draggable_switch = ctk.CTkSwitch(master=legend_frame, text="Mouse draggable", variable=draggable_var, )
        
        legend_anchor_label = ctk.CTkLabel(master=legend_frame, text="Anchor:")
        legend_anchor_var = tk.StringVar(value=self.controller.model.plot_legend["legend anchor"])
        legend_anchor_cbbox = tk.ttk.Combobox(master=legend_frame, values=p.LEGEND_POS, state='readonly',
                                              textvariable=legend_anchor_var)
        
        legend_alpha_label = ctk.CTkLabel(master=legend_frame, text="Alpha:")
        legend_alpha_var = tk.DoubleVar(value=self.controller.model.plot_legend['legend alpha'])
        legend_alpha_slider = ctk.CTkSlider(master=legend_frame, from_=0, to=1, number_of_steps=10,
                                            variable=legend_alpha_var)
        legend_alpha_value_label = ctk.CTkLabel(master=legend_frame, textvariable=legend_alpha_var)
        
        legend_xpos_label = ctk.CTkLabel(master=legend_frame, text="X position:")
        legend_xpos_var = tk.DoubleVar(value=self.controller.model.plot_legend['legend x pos'])
        legend_xpos_slider = ctk.CTkSlider(master=legend_frame, from_=0, to=1, number_of_steps=10,
                                           variable=legend_xpos_var)
        legend_xpos_value_label = ctk.CTkLabel(master=legend_frame, textvariable=legend_xpos_var)
        
        legend_ypos_label = ctk.CTkLabel(master=legend_frame, text="Y position:")
        legend_ypos_var = tk.DoubleVar(value=self.controller.model.plot_legend['legend y pos'])
        legend_ypos_slider = ctk.CTkSlider(master=legend_frame, from_=0, to=1, number_of_steps=10,
                                           variable=legend_ypos_var)
        legend_ypos_value_label = ctk.CTkLabel(master=legend_frame, textvariable=legend_ypos_var)
        
        ncols_label = ctk.CTkLabel(master=legend_frame, text="Number of columns:")
        ncols_var = tk.StringVar(value=self.controller.model.plot_legend["legend ncols"])
        ncols_entry = ErrEntry(master=legend_frame, width=50, textvariable=ncols_var)
        
        fontsize_var = tk.IntVar(value=self.controller.model.plot_legend['legend fontsize'])
        fontsize_label = ctk.CTkLabel(master=legend_frame, text="Font size:")
        fontsize_slider = ctk.CTkSlider(master=legend_frame, from_=8, to=32, number_of_steps=24,
                                        variable=fontsize_var)
        fontsize_value_label = ctk.CTkLabel(master=legend_frame, textvariable=fontsize_var)
        
        # -------- WIDGET MANAGEMENT
        title_label.place(relx=0, rely=0)
        title_entry.place_errentry(relx=0, rely=0.06, )
        title_size_value_label.place(relx=0.15, rely=0.15)
        title_font_label.place(relx=0.5, rely=0)
        title_font_cbbox.place(relx=0.5, rely=0.06, relwidth=0.4)
        title_size_label.place(relx=0, rely=0.15)
        title_size_slider.place(relx=0, rely=0.2, relwidth=0.4)
        dpi_label.place(relx=0.5, rely=0.15)
        dpi_entry.place_errentry(relx=0.5, rely=0.2)
        
        show_legend_switch.place(relx=0, rely=0.32)
        draggable_switch.place(relx=0.5, rely=0.32)
        legend_anchor_label.place(relx=0, rely=0.38)
        legend_anchor_cbbox.place(relx=0, rely=0.47)
        legend_alpha_slider.place(relx=0.5, rely=0.47, relwidth=0.4)
        legend_alpha_value_label.place(relx=0.65, rely=0.38)
        legend_alpha_label.place(relx=0.5, rely=0.38)
        legend_xpos_label.place(relx=0, rely=0.54)
        legend_xpos_slider.place(relx=0, rely=0.6, relwidth=0.4)
        legend_xpos_value_label.place(relx=0.2, rely=0.54)
        legend_ypos_label.place(relx=0.5, rely=0.54)
        legend_ypos_slider.place(relx=0.5, rely=0.6, relwidth=0.4)
        legend_ypos_value_label.place(relx=0.65, rely=0.54)
        ncols_label.place(relx=0, rely=0.68)
        ncols_entry.place_errentry(relx=0, rely=0.73, )
        fontsize_label.place(relx=0.5, rely=0.68)
        fontsize_slider.place(relx=0.5, rely=0.73, relwidth=0.4)
        fontsize_value_label.place(relx=0.65, rely=0.68)
        
        self.vars["title"] = title_var
        self.entries["title"] = title_entry
        self.vars["title font"] = title_font_var
        self.cbboxes["title font"] = title_font_cbbox
        self.vars["title size"] = title_size_var
        self.sliders["title size"] = title_size_slider
        self.entries["dpi"] = dpi_entry
        self.vars["dpi"] = dpi_strvar
        
        self.switches["show legend"] = show_legend_switch
        self.vars["show legend"] = show_legend_var
        self.switches["legend draggable"] = draggable_switch
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
        
        # ----- TRACE
        title_var.trace("w", partial(self.controller.trace_vars_to_model, 'title'))
        title_size_var.trace("w", partial(self.controller.trace_vars_to_model, 'title size'))
        title_font_var.trace("w", partial(self.controller.trace_vars_to_model, 'title font'))
        dpi_strvar.trace("w", partial(self.controller.trace_vars_to_model, 'dpi'))
        
        show_legend_var.trace("w", partial(self.controller.trace_vars_to_model, 'show legend'))
        fontsize_var.trace("w", partial(self.controller.trace_vars_to_model, 'legend fontsize'))
        legend_xpos_var.trace("w", partial(self.controller.trace_vars_to_model, 'legend x pos'))
        legend_ypos_var.trace("w", partial(self.controller.trace_vars_to_model, 'legend y pos'))
        legend_alpha_var.trace("w", partial(self.controller.trace_vars_to_model, 'legend alpha'))
        legend_anchor_var.trace("w", partial(self.controller.trace_vars_to_model, 'legend anchor'))
        ncols_var.trace("w", partial(self.controller.trace_vars_to_model, 'legend ncols'))
        draggable_var.trace("w", partial(self.controller.trace_vars_to_model, 'legend draggable'))
        
        # ------ ENTRY VALIDATION
        
        dpi_entry.configure(validate='focus',
                                validatecommand=(
                                    self.register(partial(self.parent_view.parent_view.is_positive_int, dpi_entry)),
                                    '%P'))
        ncols_entry.configure(validate='focus',
                            validatecommand=(
                                self.register(partial(self.parent_view.parent_view.is_positive_int, ncols_entry)),
                                '%P'))
        
    
    def generate_figname_content(self):
        figname_frame = self.frames["figname"]
        load_config_button = ctk.CTkButton(master=figname_frame, text="Load config", fg_color="lightslategray")
        save_config_button = ctk.CTkButton(master=figname_frame, text="Save config", fg_color="lightslategray")
        save_figure_button = ctk.CTkButton(master=figname_frame, text="Save figure", fg_color="green")
        
        load_config_button.place(anchor=tk.CENTER, relx=0.5, rely=0.4, relheight=0.05)
        save_config_button.place(anchor=tk.CENTER, relx=0.5, rely=0.5, relheight=0.05)
        save_figure_button.place(anchor=tk.CENTER, relx=0.5, rely=0.6, relheight=0.05)
        
        self.buttons["save fig"] = save_figure_button
        self.buttons["load config"] = load_config_button
        self.buttons["save config"] = save_config_button
        
        save_config_button.configure(command=self.controller.save_config)
        load_config_button.configure(command=self.controller.load_config)
        # save_figure_button.configure(command=partial(self.controller.save_figure, self.figures["plot"][0]))
    
    def show_frame(self, frame_name, *args):
        self.select_check_processing_step(frame_name)
        
        for frame in self.step_check.keys():
            if frame != frame_name:
                self.frames[frame].place_forget()
            else:
                self.frames[frame_name].place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)
    
    def select_check_processing_step(self, step=None):
        for s in self.step_check.keys():
            if self.step_check[s] == 2:
                img = ctk.CTkImage(dark_image=Image.open(resource_path(f"data/firelearn_img/{s}_grey.png")),
                                   size=(120, 120))
                self.image_buttons[s].configure(image=img)
            if self.step_check[s] == 1:
                img = ctk.CTkImage(dark_image=Image.open(resource_path(f"data/firelearn_img/{s}_green.png")),
                                   size=(120, 120))
                self.image_buttons[s].configure(image=img)
            if self.step_check[s] == 0:
                img = ctk.CTkImage(dark_image=Image.open(resource_path(f"data/firelearn_img/{s}_red.png")),
                                   size=(120, 120))
                self.image_buttons[s].configure(image=img)
            if step:
                if s == str(step):
                    img = ctk.CTkImage(dark_image=Image.open(resource_path(f"data/firelearn_img/{s}_blue.png")),
                                       size=(120, 120))
                    self.image_buttons[s].configure(image=img)
    
    def update_slider_value(self, value, var):
        self.parent_view.parent_view.update_slider_value(value, var)
    
    def select_color(self, view, selection_button_name):
        self.parent_view.parent_view.select_color(view=view, selection_button_name=selection_button_name)
    
    @staticmethod
    def rename_dict_key(d, old_key, new_key):
        if old_key in d:
            d[new_key] = d.pop(old_key)
