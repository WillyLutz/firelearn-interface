import tkinter as tk
from functools import partial
from tkinter import ttk, messagebox

import customtkinter as ctk
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import params as p
from CONTROLLER.ConfusionController import ConfusionController


class ConfusionView(ctk.CTkFrame):
    def __init__(self, app, master, parent_view):
        super().__init__(master=app)
        self.master = master
        self.parent_view = parent_view
        self.controller = ConfusionController(self, )

        self.frames = {}
        self.entries = {}
        self.buttons = {}
        self.cbboxes = {}
        self.vars = {}
        self.trace_ids = {}
        self.switches = {}
        self.sliders = {}
        self.checkboxes = {}
        self.textboxes = {}
        self.canvas = {}
        self.lines = {}
        self.figures = {}
        self.scrollable_frames = {}

        self.ydata_subframes = {}
        self.manage_confusion_tab()
        self.axes_toplevel()
        self.general_settings_toplevel()
        self.legend_toplevel()

    def set_controller(self, controller):
        self.controller = controller

    def manage_confusion_tab(self):

        # --------------- INIT FRAME
        load_frame = ctk.CTkFrame(master=self.master)
        load_frame.place(relx=0, rely=0, relwidth=0.31, relheight=0.1)

        load_model_button = ctk.CTkButton(master=load_frame, text="Load classifier", )
        load_dataset_button = ctk.CTkButton(master=load_frame, text="Load dataset", )
        load_model_var = tk.StringVar()
        load_model_entry = ctk.CTkEntry(master=load_frame, textvariable=load_model_var, state='disabled')
        load_dataset_var = tk.StringVar()
        load_dataset_entry = ctk.CTkEntry(master=load_frame, textvariable=load_dataset_var, state='disabled')

        load_model_button.place(relx=0.05, rely=0)
        load_dataset_button.place(relx=0.5, rely=0)
        load_model_entry.place(relx=0.05, rely=0.5, relwidth=0.4)
        load_dataset_entry.place(relx=0.5, rely=0.5, relwidth=0.4)

        self.vars["load dataset"] = load_dataset_var
        self.vars["load clf"] = load_model_var

        # --------------- BODY FRAME
        body_frame = ctk.CTkFrame(master=self.master)
        body_frame.place(relx=0, rely=0.12, relwidth=0.31, relheight=0.88)

        label_column_label = ctk.CTkLabel(master=body_frame, text='Label column:')
        label_column_var = tk.StringVar(value='None')
        label_column_cbbox = tk.ttk.Combobox(master=body_frame, values=['None', ], textvariable=label_column_var,
                                             state='readonly')
        self.vars["label column"] = label_column_var
        self.cbboxes["label column"] = label_column_cbbox

        label_column_label.place(relx=0.05, rely=0)
        label_column_cbbox.place(relx=0.25, rely=0)

        training_label = ctk.CTkLabel(master=body_frame, text="Training")
        training_frame = ctk.CTkScrollableFrame(master=body_frame, )
        training_frame.grid_columnconfigure(0, weight=1)
        training_frame.grid_columnconfigure(1, weight=1)
        training_frame.grid_columnconfigure(2, weight=1)
        self.scrollable_frames["training"] = training_frame

        training_label.place(relx=0.05, rely=0.1)
        training_frame.place(relx=0.05, rely=0.15, relwidth=0.9, relheight=0.2)

        testing_label = ctk.CTkLabel(master=body_frame, text="Testing")
        iteration_label = ctk.CTkLabel(master=body_frame, text='iterations: ')
        iteration_var = tk.IntVar(value=1)
        iteration_value_label = ctk.CTkLabel(master=body_frame, textvariable=iteration_var)
        iteration_slider = ctk.CTkSlider(master=body_frame, variable=iteration_var, from_=1, to=10, number_of_steps=10)
        testing_frame = ctk.CTkScrollableFrame(master=body_frame)
        testing_frame.grid_columnconfigure(0, weight=1)
        testing_frame.grid_columnconfigure(1, weight=1)
        testing_frame.grid_columnconfigure(2, weight=1)
        self.scrollable_frames["testing"] = testing_frame
        self.vars['iterations'] = iteration_var

        label_column_label.place(relx=0.05, rely=0)
        label_column_cbbox.place(relx=0.25, rely=0)
        training_label.place(relx=0.05, rely=0.1)
        training_frame.place(relx=0.05, rely=0.15, relwidth=0.9, relheight=0.2)

        testing_label.place(relx=0.05, rely=0.4)
        iteration_label.place(relx=0.25, rely=0.4)
        iteration_value_label.place(relx=0.4, rely=0.4)
        iteration_slider.place(relx=0.45, rely=0.4, relwidth=0.45)
        testing_frame.place(relx=0.05, rely=0.45, relwidth=0.90, relheight=0.3)

        select_all_button = ctk.CTkButton(master=body_frame, text="Select all",
                                          command=self.controller.select_all_test_targets)
        deselect_all_button = ctk.CTkButton(master=body_frame, text="Deselect all",
                                            command=self.controller.deselect_all_test_targets)

        select_all_button.place(relx=0.05, rely=0.8)
        deselect_all_button.place(relx=0.35, rely=0.8)

        # --------------- EXEC_FRAME
        exec_frame = ctk.CTkFrame(master=self.master)
        exec_frame.place(relx=0.33, rely=0, relwidth=0.1, relheight=1)

        general_settings_button = ctk.CTkButton(master=exec_frame, text='General settings', )
        axes_button = ctk.CTkButton(master=exec_frame, text='Axes', command=self.axes_toplevel)
        legend_button = ctk.CTkButton(master=exec_frame, text='Legend', command=self.legend_toplevel)
        load_config_button = ctk.CTkButton(master=exec_frame, text="Load config", fg_color="lightslategray", )
        save_config_button = ctk.CTkButton(master=exec_frame, text="Save config", fg_color="lightslategray", )
        save_figure_button = ctk.CTkButton(master=exec_frame, text="Save figure", fg_color="green", )
        draw_figure_button = ctk.CTkButton(master=exec_frame, text='Draw figure', fg_color='green', )
        export_data_button = ctk.CTkButton(master=exec_frame, text="Export data", fg_color="green", )
        update_figure_button = ctk.CTkButton(master=exec_frame, text="Update figure")

        general_settings_button.place(anchor=tk.CENTER, relx=0.5, rely=0.1, relheight=0.05, )
        axes_button.place(anchor=tk.CENTER, relx=0.5, rely=0.2, relheight=0.05)
        legend_button.place(anchor=tk.CENTER, relx=0.5, rely=0.3, relheight=0.05)
        load_config_button.place(anchor=tk.CENTER, relx=0.5, rely=0.4, relheight=0.05)
        save_config_button.place(anchor=tk.CENTER, relx=0.5, rely=0.5, relheight=0.05)
        save_figure_button.place(anchor=tk.CENTER, relx=0.5, rely=0.6, relheight=0.05)
        export_data_button.place(anchor=tk.CENTER, relx=0.5, rely=0.7, relheight=0.05)
        draw_figure_button.place(anchor=tk.CENTER, relx=0.5, rely=0.85, relheight=0.1)
        update_figure_button.place(anchor=tk.CENTER, relx=0.5, rely=0.95, relheight=0.05)
        
        self.buttons["general settings"] = general_settings_button
        self.buttons["legend"] = legend_button
        self.buttons["axes"] = axes_button

        # --------------- PLOT_FRAME
        plot_frame = ctk.CTkFrame(master=self.master)
        plot_frame.place(relx=0.45, rely=0, relwidth=0.55, relheight=1)
        self.frames['plot frame'] = plot_frame

        fig, ax = plt.subplots(figsize=(p.DEFAULT_FIGUREWIDTH, p.DEFAULT_FIGUREHEIGHT))
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.get_tk_widget().place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.96)
        self.figures["confusion"] = (fig, ax)
        self.canvas["confusion"] = canvas

        # --------------- CONFIGURE
        load_model_button.configure(command=self.controller.load_model)
        load_dataset_button.configure(command=self.controller.load_dataset)

        save_config_button.configure(command=self.controller.save_config)
        load_config_button.configure(command=self.controller.load_dataset)
        save_figure_button.configure(command=partial(self.controller.save_figure, self.figures["confusion"][0]))
        export_data_button.configure(command=partial(self.controller.export_figure_data, self.figures["confusion"][1]))
        draw_figure_button.configure(command=self.controller.draw_figure)
        update_figure_button.configure(command=self.controller.update_figure)


        # --------------- TRACE
        for key, widget in {"load dataset": load_dataset_var, "load clf": load_model_var,
                            "label column": label_column_var, "iterations": iteration_var}.items():
            widget.trace("w", partial(self.controller.trace_vars_to_model, key))
        label_column_var.trace("w", self.controller.trace_testing_labels)

    def legend_toplevel(self):
        # todo : allow single window

        width = 450
        height = 400
        general_toplevel = ctk.CTkToplevel(width=width, height=height)
        general_toplevel.protocol('WM_DELETE_WINDOW', general_toplevel.withdraw)
        general_toplevel.withdraw()
        self.buttons["legend"].configure(command=partial(self.parent_view.parent_view.deiconify_toplevel, general_toplevel))
        
        general_toplevel.title("Legend (Confusion)")
        general_toplevel.resizable(False, False)
        general_toplevel.attributes("-topmost", 1)

        show_legend_var = tk.IntVar(value=self.controller.model.plot_legend['show legend'])
        show_legend_switch = ctk.CTkSwitch(master=general_toplevel, text="Show legend", variable=show_legend_var)
        show_legend_switch.place(x=0, y=0)
        self.switches["show legend"] = show_legend_switch
        self.vars["show legend"] = show_legend_var

        draggable_var = tk.BooleanVar(value=self.controller.model.plot_legend["legend draggable"])
        draggable_switch = ctk.CTkSwitch(master=general_toplevel, text="Mouse draggable", variable=draggable_var, )
        draggable_switch.place(x=225, y=0)
        self.switches["legend draggable"] = draggable_switch
        self.vars["legend draggable"] = draggable_var

        legend_anchor_label = ctk.CTkLabel(master=general_toplevel, text="Anchor:")
        legend_anchor_var = tk.StringVar(value=self.controller.model.plot_legend["legend anchor"])
        legend_anchor_cbbox = tk.ttk.Combobox(master=general_toplevel, values=p.LEGEND_POS, state='readonly',
                                              textvariable=legend_anchor_var)
        legend_anchor_label.place(x=0, y=60)
        legend_anchor_cbbox.place(x=0, y=100)
        self.cbboxes["legend anchor"] = legend_anchor_cbbox
        self.vars["legend anchor"] = legend_anchor_var

        legend_alpha_label = ctk.CTkLabel(master=general_toplevel, text="Alpha:")
        legend_alpha_var = tk.DoubleVar(value=self.controller.model.plot_legend['legend alpha'])
        legend_alpha_slider = ctk.CTkSlider(master=general_toplevel, from_=0, to=1, number_of_steps=10,
                                            variable=legend_alpha_var)
        legend_alpha_value_label = ctk.CTkLabel(master=general_toplevel, textvariable=legend_alpha_var)

        legend_alpha_slider.place(x=225, y=100, relwidth=0.4)
        legend_alpha_value_label.place(x=270, y=60)
        legend_alpha_label.place(x=225, y=60)
        self.vars["legend alpha"] = legend_alpha_var
        self.sliders["legend alpha"] = legend_alpha_slider

        legend_xpos_label = ctk.CTkLabel(master=general_toplevel, text="X position:")
        legend_xpos_var = tk.DoubleVar(value=self.controller.model.plot_legend['legend x pos'])
        legend_xpos_slider = ctk.CTkSlider(master=general_toplevel, from_=0, to=1, number_of_steps=10,
                                           variable=legend_xpos_var)
        legend_xpos_value_label = ctk.CTkLabel(master=general_toplevel, textvariable=legend_xpos_var)

        legend_xpos_label.place(x=0, y=150)
        legend_xpos_slider.place(x=0, y=190, relwidth=0.4)
        legend_xpos_value_label.place(x=80, y=150)
        self.vars["legend x pos"] = legend_xpos_var
        self.sliders["legend x pos"] = legend_xpos_slider

        legend_ypos_label = ctk.CTkLabel(master=general_toplevel, text="Y position:")
        legend_ypos_var = tk.DoubleVar(value=self.controller.model.plot_legend['legend y pos'])
        legend_ypos_slider = ctk.CTkSlider(master=general_toplevel, from_=0, to=1, number_of_steps=10,
                                           variable=legend_ypos_var)
        legend_ypos_value_label = ctk.CTkLabel(master=general_toplevel, textvariable=legend_ypos_var)

        legend_ypos_label.place(x=225, y=150)
        legend_ypos_slider.place(x=225, y=190, relwidth=0.4)
        legend_ypos_value_label.place(x=300, y=150)
        self.vars["legend y pos"] = legend_ypos_var
        self.sliders["legend y pos"] = legend_ypos_slider

        ncols_label = ctk.CTkLabel(master=general_toplevel, text="Number of columns:")
        ncols_var = tk.StringVar(value=self.controller.model.plot_legend["legend ncols"])
        ncols_entry = ctk.CTkEntry(master=general_toplevel, width=50, textvariable=ncols_var)

        ncols_label.place(x=0, y=240)
        ncols_entry.place(x=0, y=280, )
        self.vars["legend ncols"] = ncols_var
        self.entries["legend ncols"] = ncols_entry

        fontsize_var = tk.IntVar(value=self.controller.model.plot_legend['legend fontsize'])
        fontsize_label = ctk.CTkLabel(master=general_toplevel, text="Font size:")
        fontsize_slider = ctk.CTkSlider(master=general_toplevel, from_=8, to=32, number_of_steps=24,
                                        variable=fontsize_var)
        fontsize_value_label = ctk.CTkLabel(master=general_toplevel, textvariable=fontsize_var)

        fontsize_label.place(x=225, y=240)
        fontsize_slider.place(x=225, y=280, relwidth=0.4)
        fontsize_value_label.place(x=300, y=240)
        self.vars["legend fontsize"] = fontsize_var
        self.sliders["legend fontsize"] = fontsize_slider

        # ----- TRACE
        show_legend_var.trace("w", partial(self.controller.trace_vars_to_model, 'show legend'))
        fontsize_var.trace("w", partial(self.controller.trace_vars_to_model, 'legend fontsize'))
        legend_xpos_var.trace("w", partial(self.controller.trace_vars_to_model, 'legend x pos'))
        legend_ypos_var.trace("w", partial(self.controller.trace_vars_to_model, 'legend y pos'))
        legend_alpha_var.trace("w", partial(self.controller.trace_vars_to_model, 'legend alpha'))
        legend_anchor_var.trace("w", partial(self.controller.trace_vars_to_model, 'legend anchor'))
        ncols_var.trace("w", partial(self.controller.trace_vars_to_model, 'legend ncols'))
        draggable_var.trace("w", partial(self.controller.trace_vars_to_model, 'legend draggable'))

    def general_settings_toplevel(self):
        # todo : allow single window

        width = 450
        height = 250
        general_toplevel = ctk.CTkToplevel(width=width, height=height)
        general_toplevel.protocol('WM_DELETE_WINDOW', general_toplevel.withdraw)
        general_toplevel.withdraw()
        self.buttons["general settings"].configure(command=partial(self.parent_view.parent_view.deiconify_toplevel, general_toplevel))
        
        general_toplevel.title("General settings (Confusion)")
        general_toplevel.resizable(False, False)
        general_toplevel.attributes("-topmost", 1)

        title_label = ctk.CTkLabel(master=general_toplevel, text="Title:")
        title_var = tk.StringVar()
        title_var.set(self.controller.model.plot_general_settings['title'])
        title_entry = ctk.CTkEntry(master=general_toplevel, width=180, textvariable=title_var)

        title_label.place(x=0, y=0)
        title_entry.place(x=0, y=40, )
        self.vars["title"] = title_var
        self.entries["title"] = title_entry

        title_font_var = tk.StringVar()
        title_font_var.set(self.controller.model.plot_general_settings['title font'])
        title_font_label = ctk.CTkLabel(master=general_toplevel, text="Title font:")
        title_font_cbbox = tk.ttk.Combobox(master=general_toplevel, values=p.FONTS, state='readonly',
                                           textvariable=title_font_var)

        title_font_label.place(x=225, y=0)
        title_font_cbbox.place(x=225, y=40, relwidth=0.4)
        self.vars["title font"] = title_font_var
        self.cbboxes["title font"] = title_font_cbbox

        title_size_var = tk.IntVar(value=self.controller.model.plot_general_settings['title size'])
        title_size_label = ctk.CTkLabel(master=general_toplevel, text="Title size:")
        title_size_slider = ctk.CTkSlider(master=general_toplevel, from_=8, to=32, number_of_steps=24,
                                          variable=title_size_var)
        title_size_value_label = ctk.CTkLabel(master=general_toplevel, textvariable=title_size_var)

        title_size_label.place(x=0, y=100)
        title_size_slider.place(x=0, y=140, relwidth=0.4)
        title_size_value_label.place(x=60, y=100)
        self.vars["title size"] = title_size_var
        self.sliders["title size"] = title_size_slider

        dpi_label = ctk.CTkLabel(master=general_toplevel, text="Figure dpi:")
        dpi_strvar = tk.StringVar()
        dpi_strvar.set(self.controller.model.plot_general_settings['dpi'])
        dpi_entry = ctk.CTkEntry(master=general_toplevel, textvariable=dpi_strvar, width=180)

        dpi_label.place(x=225, y=100)
        dpi_entry.place(x=225, y=140)
        self.entries["dpi"] = dpi_entry
        self.vars["dpi"] = dpi_strvar

        # ----- TRACE
        title_var.trace("w", partial(self.controller.trace_vars_to_model, 'title'))
        title_size_var.trace("w", partial(self.controller.trace_vars_to_model, 'title size'))
        title_font_var.trace("w", partial(self.controller.trace_vars_to_model, 'title font'))
        dpi_strvar.trace("w", partial(self.controller.trace_vars_to_model, 'dpi'))

    def axes_toplevel(self):
        width = 500
        height = 800
        general_toplevel = ctk.CTkToplevel(width=width, height=height)
        general_toplevel.protocol('WM_DELETE_WINDOW', general_toplevel.withdraw)
        general_toplevel.withdraw()
        self.buttons["axes"].configure(command=partial(self.parent_view.parent_view.deiconify_toplevel, general_toplevel))

        general_toplevel.title("Axes settings (Confusion)")
        general_toplevel.resizable(False, False)
        general_toplevel.attributes("-topmost", 1)

        x_major_label = ctk.CTkLabel(master=general_toplevel, text="X-AXIS")
        x_major_label.place(anchor=tk.CENTER, x=125, y=20)
        y_major_label = ctk.CTkLabel(master=general_toplevel, text="Y-AXIS")
        y_major_label.place(anchor=tk.CENTER, x=375, y=20)

        x_label = ctk.CTkLabel(master=general_toplevel, text="Label:")
        x_label_var = tk.StringVar(value=self.controller.model.plot_axes['x label'])
        x_label_entry = ctk.CTkEntry(master=general_toplevel, width=200, textvariable=x_label_var)
        x_label.place(x=0, y=50)
        x_label_entry.place(x=0, y=90)
        self.entries["x label"] = x_label_entry
        self.vars['x label'] = x_label_var

        y_label = ctk.CTkLabel(master=general_toplevel, text="Label:")
        y_label_var = tk.StringVar(value=self.controller.model.plot_axes['y label'])
        y_label_entry = ctk.CTkEntry(master=general_toplevel, width=200, textvariable=y_label_var)
        y_label.place(x=250, y=50)
        y_label_entry.place(x=250, y=90)
        self.entries["y label"] = y_label_entry
        self.vars['y label'] = y_label_var

        x_size_label = ctk.CTkLabel(master=general_toplevel, text="Label size:")
        x_label_size_var = tk.IntVar(value=self.controller.model.plot_axes['x label size'])
        x_label_slider = ctk.CTkSlider(master=general_toplevel, from_=8, to=32, number_of_steps=24,
                                       variable=x_label_size_var)
        x_label_value_label = ctk.CTkLabel(master=general_toplevel, textvariable=x_label_size_var)
        x_label_value_label.place(x=100, y=130)
        x_label_slider.place(x=0, y=170, relwidth=0.4)
        x_size_label.place(x=0, y=130)
        self.vars["x label size"] = x_label_size_var
        self.sliders["x label size"] = x_label_slider

        y_size_label = ctk.CTkLabel(master=general_toplevel, text="Label size:")
        y_label_size_var = tk.IntVar(value=self.controller.model.plot_axes['y label size'])
        y_label_slider = ctk.CTkSlider(master=general_toplevel, from_=8, to=32, number_of_steps=24,
                                       variable=y_label_size_var)
        y_label_value_label = ctk.CTkLabel(master=general_toplevel, textvariable=y_label_size_var)
        y_label_value_label.place(x=350, y=130)
        y_label_slider.place(x=250, y=170, relwidth=0.4)
        y_size_label.place(x=250, y=130)
        self.vars["y label size"] = y_label_size_var
        self.sliders["y label size"] = y_label_slider

        # -----TICKS

        xticks_rotation_label = ctk.CTkLabel(master=general_toplevel, text="Tick rotation:")
        xticks_rotation_var = tk.IntVar(value=self.controller.model.plot_axes['x ticks rotation'])
        xticks_rotation_slider = ctk.CTkSlider(master=general_toplevel, from_=-180, to=180, number_of_steps=36,
                                               variable=xticks_rotation_var)
        xticks_rotation_value_label = ctk.CTkLabel(master=general_toplevel, textvariable=xticks_rotation_var)
        xticks_rotation_slider.place(x=0, y=290, relwidth=0.4)
        xticks_rotation_label.place(x=0, y=250)
        xticks_rotation_value_label.place(x=100, y=250)
        self.vars["x ticks rotation"] = xticks_rotation_var
        self.sliders["x ticks rotation"] = xticks_rotation_slider

        yticks_rotation_label = ctk.CTkLabel(master=general_toplevel, text="Tick rotation:")
        yticks_rotation_var = tk.IntVar(value=self.controller.model.plot_axes['y ticks rotation'])
        yticks_rotation_slider = ctk.CTkSlider(master=general_toplevel, from_=-180, to=180, number_of_steps=36,
                                               variable=yticks_rotation_var)
        yticks_rotation_value_label = ctk.CTkLabel(master=general_toplevel, textvariable=yticks_rotation_var)
        yticks_rotation_slider.place(x=250, y=290, relwidth=0.4)
        yticks_rotation_label.place(x=250, y=250)
        yticks_rotation_value_label.place(x=350, y=250)
        self.vars["y ticks rotation"] = yticks_rotation_var
        self.sliders["y ticks rotation"] = yticks_rotation_slider

        xticks_label = ctk.CTkLabel(master=general_toplevel, text="Tick size:")
        xticks_size_var = tk.IntVar(value=self.controller.model.plot_axes['x ticks size'])
        xticks_slider = ctk.CTkSlider(master=general_toplevel, from_=8, to=32, number_of_steps=24,
                                      variable=xticks_size_var)
        xticks_value_label = ctk.CTkLabel(master=general_toplevel, textvariable=xticks_size_var)
        xticks_label.place(x=0, y=330)
        xticks_slider.place(x=0, y=370, relwidth=0.4)
        xticks_value_label.place(x=100, y=330)
        self.vars["x ticks size"] = xticks_size_var
        self.sliders["x ticks size"] = xticks_slider

        yticks_label = ctk.CTkLabel(master=general_toplevel, text="Tick size:")
        yticks_size_var = tk.IntVar(value=self.controller.model.plot_axes['y ticks size'])
        yticks_slider = ctk.CTkSlider(master=general_toplevel, from_=8, to=32, number_of_steps=24,
                                      variable=yticks_size_var)
        yticks_value_label = ctk.CTkLabel(master=general_toplevel, textvariable=yticks_size_var)
        yticks_label.place(x=250, y=330)
        yticks_slider.place(x=250, y=370, relwidth=0.4)
        yticks_value_label.place(x=350, y=330)
        self.vars["y ticks size"] = yticks_size_var
        self.sliders["y ticks size"] = yticks_slider

        general_label = ctk.CTkLabel(master=general_toplevel, text='GENERAL')
        general_label.place(x=0, y=400)

        axes_font_label = ctk.CTkLabel(master=general_toplevel, text="Axes font:")
        axes_font_var = tk.StringVar(value=self.controller.model.plot_axes['axes font'])
        axes_font_cbbox = tk.ttk.Combobox(master=general_toplevel, values=p.FONTS, state='readonly',
                                          textvariable=axes_font_var)
        axes_font_label.place(x=0, y=440)
        axes_font_cbbox.place(x=80, y=440, relwidth=0.4)
        self.cbboxes["axes font"] = axes_font_cbbox
        self.vars["axes font"] = axes_font_var

        ticks_train_scrollable = ctk.CTkScrollableFrame(master=general_toplevel, height=300, width=200)
        ticks_train_scrollable.grid_columnconfigure(0, weight=1)
        ticks_train_scrollable.place(relx=0.05, y=470, )
        self.scrollable_frames["ticks train"] = ticks_train_scrollable

        ticks_test_scrollable = ctk.CTkScrollableFrame(master=general_toplevel, height=300, width=200)
        ticks_test_scrollable.grid_columnconfigure(0, weight=1)
        ticks_test_scrollable.place(relx=0.55, y=470, )
        self.scrollable_frames["ticks test"] = ticks_test_scrollable

        update_ticks_button = ctk.CTkButton(master=general_toplevel, text='Update train/test ticks',
                                            command=self.controller.update_confusion_ticks)
        update_ticks_button.place(x=300, y=440)
        if self.controller.model.dataset_path:
            self.controller.update_confusion_ticks()

        # ----- TRACE
        x_label_var.trace("w", partial(self.controller.trace_vars_to_model, 'x label'))
        y_label_var.trace("w", partial(self.controller.trace_vars_to_model, 'y label'))
        x_label_size_var.trace("w", partial(self.controller.trace_vars_to_model, 'x label size'))
        y_label_size_var.trace("w", partial(self.controller.trace_vars_to_model, 'y label size'))
        xticks_rotation_var.trace("w", partial(self.controller.trace_vars_to_model, 'x ticks rotation'))
        yticks_rotation_var.trace("w", partial(self.controller.trace_vars_to_model, 'y ticks rotation'))
        xticks_size_var.trace("w", partial(self.controller.trace_vars_to_model, 'x ticks size'))
        yticks_size_var.trace("w", partial(self.controller.trace_vars_to_model, 'y ticks size'))
        axes_font_var.trace("w", partial(self.controller.trace_vars_to_model, 'axes font'))


