import tkinter as tk
from functools import partial
from tkinter import ttk, messagebox

import customtkinter as ctk
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import params as p
from CONTROLLER.PlotController import PlotController


class PlotView(ctk.CTkFrame):
    def __init__(self, app, master, parent_view):
        super().__init__(master=app)
        self.master = master
        self.parent_view = parent_view
        self.controller = PlotController(self, )

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
        self.manage_plot_tab()

    def set_controller(self, controller):
        self.controller = controller

    def manage_plot_tab(self):

        # --------------- INIT FRAME
        init_frame = ctk.CTkFrame(master=self.master)
        load_dataset_button = ctk.CTkButton(master=init_frame, text="Load dataset:")

        init_frame.place(relx=0, rely=0, relheight=0.1, relwidth=0.31)
        load_dataset_button.place(relx=0.0, rely=0)
        self.buttons["load dataset"] = load_dataset_button

        load_dataset_var = tk.StringVar()
        load_dataset_entry = ctk.CTkEntry(master=init_frame, state='disabled', textvariable=load_dataset_var)

        load_dataset_entry.place(relx=0, rely=0.5, relwidth=0.5)
        self.vars["load dataset"] = load_dataset_var
        self.entries["load dataset"] = load_dataset_entry

        # ----- TITLE
        curves_frame = ctk.CTkFrame(master=self.master)

        curves_frame.place(relx=0, rely=0.13, relheight=0.87, relwidth=0.31)

        # ----- X DATA
        xdata_frame = ctk.CTkFrame(master=curves_frame)
        xdata_label = ctk.CTkLabel(master=xdata_frame, text="X-data column:")
        xdata_var = tk.StringVar(value="None")
        xdata_cbbox = tk.ttk.Combobox(master=xdata_frame, values=["None", ], state='readonly',
                                      textvariable=xdata_var)
        xdata_cbbox.set(xdata_var.get())

        ydata_label = ctk.CTkLabel(master=xdata_frame, text="Y-data column:")
        add_ydata_button = ctk.CTkButton(master=xdata_frame, text="+", width=25, height=25, state='normal')
        subtract_ydata_button = ctk.CTkButton(master=xdata_frame, text="-", width=25, height=25,
                                              state='normal')

        xdata_frame.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.1)
        xdata_label.place(relx=0, rely=0)
        xdata_cbbox.place(relx=0.5, rely=0)
        ydata_label.place(relx=0, rely=0.6)
        subtract_ydata_button.place(anchor=tk.NE, relx=0.38, rely=0.6)
        add_ydata_button.place(anchor=tk.NE, relx=0.25, rely=0.6)
        self.cbboxes["xdata"] = xdata_cbbox
        self.vars["xdata"] = xdata_var
        self.buttons[f"add ydata"] = add_ydata_button
        self.buttons[f"subtract ydata"] = subtract_ydata_button

        # ----- Y DATA
        ydata_frame = ctk.CTkScrollableFrame(master=curves_frame)
        ydata_frame.grid_columnconfigure(0, weight=1)
        n_ydata = self.controller.model.n_ydata

        ydata_frame.place(relx=0.01, rely=0.15, relwidth=0.98, relheight=0.84)
        self.scrollable_frames["ydata"] = ydata_frame

        # --------------- PLOT
        plot_frame = ctk.CTkFrame(master=self.master)
        plot_frame.place(relx=0.45, rely=0, relheight=1, relwidth=0.55)

        fig, ax = plt.subplots(figsize=(p.DEFAULT_FIGUREWIDTH, p.DEFAULT_FIGUREHEIGHT))
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.get_tk_widget().place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.96)
        self.figures["plot"] = (fig, ax)
        self.canvas["plot"] = canvas

        # ----- CUSTOM PLOT
        custom_plot_frame = ctk.CTkFrame(master=self.master)
        custom_plot_frame.place(relx=0.32, rely=0.0, relwidth=0.12, relheight=1)

        general_settings_button = ctk.CTkButton(master=custom_plot_frame, text='General settings')
        general_settings_button.place(anchor=tk.CENTER, relx=0.5, rely=0.1, relwidth=0.5, relheight=0.05)

        axes_button = ctk.CTkButton(master=custom_plot_frame, text='Axes')
        axes_button.place(anchor=tk.CENTER, relx=0.5, rely=0.2, relwidth=0.5, relheight=0.05)

        legend_button = ctk.CTkButton(master=custom_plot_frame, text='Legend')
        legend_button.place(anchor=tk.CENTER, relx=0.5, rely=0.3, relwidth=0.5, relheight=0.05)

        load_config_button = ctk.CTkButton(master=custom_plot_frame, text="Load config", fg_color="lightslategray")
        load_config_button.place(anchor=tk.CENTER, relx=0.5, rely=0.4, relheight=0.05)

        save_config_button = ctk.CTkButton(master=custom_plot_frame, text="Save config", fg_color="lightslategray")
        save_config_button.place(anchor=tk.CENTER, relx=0.5, rely=0.5, relheight=0.05)

        save_figure_button = ctk.CTkButton(master=custom_plot_frame, text="Save figure", fg_color="green")
        save_figure_button.place(anchor=tk.CENTER, relx=0.5, rely=0.6, relheight=0.05)

        draw_figure_button = ctk.CTkButton(master=custom_plot_frame, text='Draw figure',
                                           fg_color='green')
        draw_figure_button.place(anchor=tk.CENTER, relx=0.5, rely=0.8, relheight=0.1)

        self.buttons["general settings"] = general_settings_button
        self.buttons["axes"] = axes_button
        self.buttons["legend"] = legend_button
        self.buttons["save fig"] = save_figure_button
        self.buttons["load config"] = load_config_button
        self.buttons["save config"] = save_config_button
        self.buttons["draw figure"] = draw_figure_button

        # ---------------- CONFIGURE
        add_ydata_button.configure(command=partial(self.add_ydata, ydata_frame))
        subtract_ydata_button.configure(command=partial(self.remove_ydata))
        load_dataset_button.configure(command=self.load_plot_dataset)
        save_config_button.configure(command=self.save_config)
        load_config_button.configure(command=self.load_config)

        save_figure_button.configure(command=partial(self.save_figure, self.figures["plot"][0]))

        general_settings_button.configure(command=self.general_settings_toplevel)
        axes_button.configure(command=self.axes_toplevel)
        legend_button.configure(command=self.legend_toplevel)

        draw_figure_button.configure(command=self.draw_figure)

        # ---- TRACE
        xdata_var.trace("w", partial(self.trace_vars_to_model, 'xdata'))

    def add_ydata(self, scrollable_frame):
        if self.controller:
            self.controller.add_ydata(scrollable_frame)

    def remove_ydata(self,):
        if self.controller:
            self.controller.remove_ydata()

    def update_slider_value(self, value, var):
        self.parent_view.parent_view.update_slider_value(value, var)

    def select_color(self, view, selection_button_name):
        self.parent_view.parent_view.select_color(view=view, selection_button_name=selection_button_name)

    def load_plot_dataset(self):
        if self.controller:
            self.controller.load_plot_dataset()

    def load_config(self):
        if self.controller:
            self.controller.load_config()

    def save_config(self):
        if self.controller:
            self.controller.save_config()

    def save_figure(self, fig):
        if self.controller:
            self.controller.save_figure(fig)

    @staticmethod
    def rename_dict_key(d, old_key, new_key):
        if old_key in d:
            d[new_key] = d.pop(old_key)

    def legend_toplevel(self):
        # todo : allow single window

        width = 450
        height = 400
        general_toplevel = ctk.CTkToplevel(width=width, height=height)
        general_toplevel.title("Legend (Plot)")
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
        legend_anchor_cbbox.set(legend_anchor_var.get())
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
        show_legend_var.trace("w", partial(self.trace_vars_to_model, 'show legend'))
        fontsize_var.trace("w", partial(self.trace_vars_to_model, 'legend fontsize'))
        legend_xpos_var.trace("w", partial(self.trace_vars_to_model, 'legend x pos'))
        legend_ypos_var.trace("w", partial(self.trace_vars_to_model, 'legend y pos'))
        legend_alpha_var.trace("w", partial(self.trace_vars_to_model, 'legend alpha'))
        legend_anchor_var.trace("w", partial(self.trace_vars_to_model, 'legend anchor'))
        ncols_var.trace("w", partial(self.trace_vars_to_model, 'legend ncols'))
        draggable_var.trace("w", partial(self.trace_vars_to_model, 'legend draggable'))

    def general_settings_toplevel(self):
        # todo : allow single window

        width = 450
        height = 250
        general_toplevel = ctk.CTkToplevel(width=width, height=height)
        general_toplevel.title("General settings (Plot)")
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
        title_font_cbbox.set(title_font_var.get())

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
        title_var.trace("w", partial(self.trace_vars_to_model, 'title'))
        title_size_var.trace("w", partial(self.trace_vars_to_model, 'title size'))
        title_font_var.trace("w", partial(self.trace_vars_to_model, 'title font'))
        dpi_strvar.trace("w", partial(self.trace_vars_to_model, 'dpi'))

    def axes_toplevel(self):
        width = 500
        height = 800
        general_toplevel = ctk.CTkToplevel(width=width, height=height)
        general_toplevel.title("Axes settings (Plot)")
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

        n_xticks_label = ctk.CTkLabel(master=general_toplevel, text="Number of ticks:")
        n_xticks_var = tk.StringVar(value=self.controller.model.plot_axes['n x ticks'])
        n_xticks_entry = ctk.CTkEntry(master=general_toplevel, textvariable=n_xticks_var)
        n_xticks_label.place(x=0, y=250)
        n_xticks_entry.place(x=0, y=290, relwidth=0.2)
        self.entries["n x ticks"] = n_xticks_entry
        self.vars["n x ticks"] = n_xticks_var

        n_yticks_label = ctk.CTkLabel(master=general_toplevel, text="Number of ticks:")
        n_yticks_var = tk.StringVar(value=self.controller.model.plot_axes['n y ticks'])
        n_yticks_entry = ctk.CTkEntry(master=general_toplevel, textvariable=n_yticks_var)
        n_yticks_label.place(x=250, y=250)
        n_yticks_entry.place(x=250, y=290, relwidth=0.2)
        self.entries["n y ticks"] = n_yticks_entry
        self.vars["n y ticks"] = n_yticks_var

        xticks_rotation_label = ctk.CTkLabel(master=general_toplevel, text="Tick rotation:")
        xticks_rotation_var = tk.IntVar(value=self.controller.model.plot_axes['x ticks rotation'])
        xticks_rotation_slider = ctk.CTkSlider(master=general_toplevel, from_=-180, to=180, number_of_steps=36,
                                               variable=xticks_rotation_var)
        xticks_rotation_value_label = ctk.CTkLabel(master=general_toplevel, textvariable=xticks_rotation_var)
        xticks_rotation_slider.place(x=0, y=370, relwidth=0.4)
        xticks_rotation_label.place(x=0, y=330)
        xticks_rotation_value_label.place(x=100, y=330)
        self.vars["x ticks rotation"] = xticks_rotation_var
        self.sliders["x ticks rotation"] = xticks_rotation_slider

        yticks_rotation_label = ctk.CTkLabel(master=general_toplevel, text="Tick rotation:")
        yticks_rotation_var = tk.IntVar(value=self.controller.model.plot_axes['y ticks rotation'])
        yticks_rotation_slider = ctk.CTkSlider(master=general_toplevel, from_=-180, to=180, number_of_steps=36,
                                               variable=yticks_rotation_var)
        yticks_rotation_value_label = ctk.CTkLabel(master=general_toplevel, textvariable=yticks_rotation_var)
        yticks_rotation_slider.place(x=250, y=370, relwidth=0.4)
        yticks_rotation_label.place(x=250, y=330)
        yticks_rotation_value_label.place(x=350, y=330)
        self.vars["y ticks rotation"] = yticks_rotation_var
        self.sliders["y ticks rotation"] = yticks_rotation_slider

        xticks_label = ctk.CTkLabel(master=general_toplevel, text="Tick size:")
        xticks_size_var = tk.IntVar(value=self.controller.model.plot_axes['x ticks size'])
        xticks_slider = ctk.CTkSlider(master=general_toplevel, from_=8, to=32, number_of_steps=24,
                                      variable=xticks_size_var)
        xticks_value_label = ctk.CTkLabel(master=general_toplevel, textvariable=xticks_size_var)
        xticks_label.place(x=0, y=410)
        xticks_slider.place(x=0, y=440, relwidth=0.4)
        xticks_value_label.place(x=100, y=410)
        self.vars["x ticks size"] = xticks_size_var
        self.sliders["x ticks size"] = xticks_slider

        yticks_label = ctk.CTkLabel(master=general_toplevel, text="Tick size:")
        yticks_size_var = tk.IntVar(value=self.controller.model.plot_axes['y ticks size'])
        yticks_slider = ctk.CTkSlider(master=general_toplevel, from_=8, to=32, number_of_steps=24,
                                      variable=yticks_size_var)
        yticks_value_label = ctk.CTkLabel(master=general_toplevel, textvariable=yticks_size_var)
        yticks_label.place(x=250, y=410)
        yticks_slider.place(x=250, y=440, relwidth=0.4)
        yticks_value_label.place(x=350, y=410)
        self.vars["y ticks size"] = yticks_size_var
        self.sliders["y ticks size"] = yticks_slider

        round_xticks_label = ctk.CTkLabel(master=general_toplevel, text="Round ticks:")
        round_xticks_strvar = tk.StringVar(value=self.controller.model.plot_axes['round x ticks'])
        round_xticks_entry = ctk.CTkEntry(master=general_toplevel, textvariable=round_xticks_strvar)
        round_xticks_label.place(x=0, y=480)
        round_xticks_entry.place(x=0, y=520, relwidth=0.2)
        self.entries["round x ticks"] = round_xticks_entry
        self.vars["round x ticks"] = round_xticks_strvar

        round_yticks_label = ctk.CTkLabel(master=general_toplevel, text="Round ticks:")
        round_yticks_strvar = tk.StringVar(value=self.controller.model.plot_axes['round y ticks'])
        round_yticks_entry = ctk.CTkEntry(master=general_toplevel, textvariable=round_yticks_strvar)
        round_yticks_label.place(x=250, y=480)
        round_yticks_entry.place(x=250, y=520, relwidth=0.2)
        self.entries["round y ticks"] = round_yticks_entry
        self.vars["round y ticks"] = round_yticks_strvar

        general_label = ctk.CTkLabel(master=general_toplevel, text='GENERAL')
        general_label.place(x=0, y=600)

        axes_font_label = ctk.CTkLabel(master=general_toplevel, text="Axes font:")
        axes_font_var = tk.StringVar(value=self.controller.model.plot_axes['axes font'])
        axes_font_cbbox = tk.ttk.Combobox(master=general_toplevel, values=p.FONTS, state='readonly',
                                          textvariable=axes_font_var)
        axes_font_cbbox.set(axes_font_var.get())
        axes_font_label.place(x=0, y=640)
        axes_font_cbbox.place(x=0, y=680, relwidth=0.4)
        self.cbboxes["axes font"] = axes_font_cbbox
        self.vars["axes font"] = axes_font_var

        # ----- TRACE
        x_label_var.trace("w", partial(self.trace_vars_to_model, 'x label'))
        y_label_var.trace("w", partial(self.trace_vars_to_model, 'y label'))
        x_label_size_var.trace("w", partial(self.trace_vars_to_model, 'x label size'))
        y_label_size_var.trace("w", partial(self.trace_vars_to_model, 'y label size'))
        n_xticks_var.trace("w", partial(self.trace_vars_to_model, 'n x ticks'))
        n_yticks_var.trace("w", partial(self.trace_vars_to_model, 'n y ticks'))
        xticks_rotation_var.trace("w", partial(self.trace_vars_to_model, 'x ticks rotation'))
        yticks_rotation_var.trace("w", partial(self.trace_vars_to_model, 'y ticks rotation'))
        xticks_size_var.trace("w", partial(self.trace_vars_to_model, 'x ticks size'))
        yticks_size_var.trace("w", partial(self.trace_vars_to_model, 'y ticks size'))
        round_xticks_strvar.trace("w", partial(self.trace_vars_to_model, 'round x ticks'))
        round_yticks_strvar.trace("w", partial(self.trace_vars_to_model, 'round y ticks'))
        axes_font_var.trace("w", partial(self.trace_vars_to_model, 'axes font'))

    def draw_figure(self):
        if self.controller:
            self.controller.draw_figure()

    def trace_vars_to_model(self, key, *args):
        if self.controller:
            self.controller.trace_vars_to_model(key, *args)
