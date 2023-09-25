import tkinter as tk
from functools import partial
from tkinter import ttk
import matplotlib.pyplot as plt

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk
import params as p
from CONTROLLER.FeatureImportanceController import FeatureImportanceController
from WIDGETS.ErrEntry import ErrEntry
from CONTROLLER import input_validation as ival


class FeatureImportanceView(ctk.CTkFrame):
    def __init__(self, app, master, parent_view):
        super().__init__(master=app)
        self.master = master
        self.parent_view = parent_view
        self.main_view = self.parent_view.parent_view
        self.controller = FeatureImportanceController(self, )

        self.toplevels = {}
        self.entries = {}
        self.buttons = {}
        self.cbboxes = {}
        self.vars = {}
        self.switches = {}
        self.sliders = {}
        self.checkboxes = {}
        self.textboxes = {}
        self.canvas = {}
        self.figures = {}

        self.manage_features_tab()

    def set_controller(self, controller):
        self.controller = controller

    def manage_features_tab(self):
        # ---------------- FRAMES

        # --------------- INIT FRAME
        init_frame = ctk.CTkFrame(master=self.master)
        init_frame.place(relx=0, rely=0, relheight=0.1, relwidth=0.31)

        load_clf_label = ctk.CTkLabel(master=init_frame, text="Loaded trained classifier:")
        load_clf_button = ctk.CTkButton(master=init_frame, text="Load Classifier")

        load_clf_label.place(relx=0, rely=0)
        load_clf_button.place(relx=0.15, rely=0)
        self.buttons["load clf"] = load_clf_button

        load_clf_var = tk.StringVar()
        load_clf_entry = ctk.CTkEntry(master=init_frame, state='disabled', textvariable=load_clf_var)
        load_clf_entry.place(relx=0, rely=0.5, relwidth=0.3)
        self.vars["load clf"] = load_clf_var

        clf_type_var = tk.StringVar(value="Classifier type:")
        clf_type_label = ctk.CTkLabel(master=init_frame, textvariable=clf_type_var)
        clf_type_label.place(relx=0.35, rely=0.5)
        self.vars["clf type"] = clf_type_var

        # --------------- PARAMS
        params_frame = ctk.CTkFrame(master=self.master)
        params_frame.place(relx=0, rely=0.13, relheight=0.87, relwidth=0.31)

        # ----- BODY
        body_label = ctk.CTkLabel(master=params_frame, text="BODY")
        title_font_label = ctk.CTkLabel(master=params_frame, text="Title font:")
        title_font_var = tk.StringVar(value=p.DEFAULT_FONT)
        title_font_cbbox = tk.ttk.Combobox(master=params_frame, values=p.FONTS, state='readonly',
                                           textvariable=title_font_var)
        body_label.place(relx=0, rely=0)
        title_font_label.place(relx=0, rely=0.1)
        title_font_cbbox.place(relx=0, rely=0.18, relwidth=0.4)
        self.vars["title font"] = title_font_var

        title_label = ctk.CTkLabel(master=params_frame, text="Title:")
        title_var = tk.StringVar()
        title_entry = ctk.CTkEntry(master=params_frame, textvariable=title_var, state='normal')
        title_label.place(relx=0.45, rely=0.0)
        title_entry.place(relx=0.45, rely=0.07, relwidth=0.5)
        self.vars["title"] = title_var

        title_size_label = ctk.CTkLabel(master=params_frame, text="Title size:")
        title_size_var = tk.IntVar(value=p.DEFAULT_FONTSIZE)
        title_size_slider = ctk.CTkSlider(master=params_frame, from_=8, to=32, number_of_steps=24,
                                          variable=title_size_var)
        title_size_value_label = ctk.CTkLabel(master=params_frame, textvariable=title_size_var)
        title_size_label.place(relx=0.5, rely=0.15)
        title_size_slider.place(relx=0.5, rely=0.23, relwidth=0.4)
        title_size_value_label.place(relx=0.8, rely=0.15)
        self.vars["title size"] = title_size_var

        linestyle_label = ctk.CTkLabel(master=params_frame, text="Linestyle:")
        linestyle_var = tk.StringVar(value=p.DEFAULT_LINESTYLE)
        linestyle_cbbox = tk.ttk.Combobox(master=params_frame, values=list(p.LINESTYLES.keys()), state='readonly',
                                          textvariable=linestyle_var)
        linestyle_label.place(relx=0, rely=0.30)
        linestyle_cbbox.place(relx=0, rely=0.38, relwidth=0.40)
        self.vars["linestyle"] = linestyle_var

        linewidth_label = ctk.CTkLabel(master=params_frame, text="Linewidth:")
        linewidth_var = tk.StringVar(value=p.DEFAULT_LINEWIDTH)
        linewidth_entry = ErrEntry(master=params_frame, textvariable=linewidth_var, )

        linewidth_label.place(relx=0.5, rely=0.30)
        linewidth_entry.place_errentry(relx=0.5, rely=0.38, relwidth=0.2, )
        self.vars["linewidth"] = linewidth_var
        self.entries["linewidth"] = linewidth_entry

        color_label = ctk.CTkLabel(master=params_frame, text="Color:")
        color_var = tk.StringVar(value="green")
        color_button = ctk.CTkButton(master=params_frame, textvariable=color_var,
                                     fg_color=color_var.get(), text_color='black')
        color_label.place(relx=0, rely=0.50)
        color_button.place(relx=0, rely=0.58)
        self.buttons['color'] = color_button
        self.vars["color"] = color_var

        alpha_label = ctk.CTkLabel(master=params_frame, text="Alpha:")
        alpha_var = tk.DoubleVar(value=p.DEFAULT_ALPHA)
        alpha_slider = ctk.CTkSlider(master=params_frame, from_=0, to=1, number_of_steps=10, variable=alpha_var)
        alpha_value_label = ctk.CTkLabel(master=params_frame, textvariable=alpha_var)
        alpha_label.place(relx=0, rely=0.68)
        alpha_slider.place(relx=0, rely=0.77, relwidth=0.4)
        alpha_value_label.place(relx=0.2, rely=0.68)
        self.vars["alpha"] = alpha_var

        fill_label = ctk.CTkLabel(master=params_frame, text="Fill:")
        fill_var = tk.StringVar(value="None")
        fill_cbbox = tk.ttk.Combobox(master=params_frame, values=["None", "Above", "Below"], state='readonly',
                                     textvariable=fill_var)
        fill_label.place(relx=0.5, rely=0.5)
        fill_cbbox.place(relx=0.5, rely=0.58, relwidth=0.40)
        self.vars["fill"] = fill_var

        alpha_fill_label = ctk.CTkLabel(master=params_frame, text="Fill alpha:")
        alpha_fill_var = tk.DoubleVar(value=p.DEFAULT_FILLALPHA)
        alpha_fill_slider = ctk.CTkSlider(master=params_frame, from_=0, to=1, number_of_steps=10,
                                          variable=alpha_fill_var)
        alpha_fill_value_label = ctk.CTkLabel(master=params_frame, textvariable=alpha_fill_var)
        alpha_fill_label.place(relx=0.5, rely=0.68)
        alpha_fill_slider.place(relx=0.5, rely=0.77, relwidth=0.4)
        alpha_fill_value_label.place(relx=0.7, rely=0.68)
        self.vars["alpha fill"] = alpha_fill_var

        dpi_label = ctk.CTkLabel(master=params_frame, text="Figure dpi:")
        dpi_var = tk.IntVar(value=p.DEFAULT_DPI)
        dpi_entry = ctk.CTkEntry(master=params_frame, textvariable=dpi_var)
        dpi_label.place(relx=0, rely=0.85)
        dpi_entry.place(relx=0, rely=0.9, relwidth=0.2)
        self.entries["dpi"] = dpi_entry
        self.vars["dpi"] = dpi_var

        # --------------- PLOT

        plot_frame = ctk.CTkFrame(master=self.master)
        plot_frame.place(relx=0.45, rely=0, relheight=1, relwidth=0.55)

        fig, ax = plt.subplots(figsize=(p.DEFAULT_FIGUREWIDTH, p.DEFAULT_FIGUREHEIGHT))
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.get_tk_widget().place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.96)
        self.figures["feature importance"] = (fig, ax)
        self.canvas["feature importance"] = canvas

        # --------------- CUSTOM PLOT
        custom_plot_frame = ctk.CTkFrame(master=self.master)
        custom_plot_frame.place(relx=0.32, rely=0.0, relwidth=0.12, relheight=1)

        axes_button = ctk.CTkButton(master=custom_plot_frame, text='Axes')
        axes_button.place(anchor=tk.CENTER, relx=0.5, rely=0.2, relwidth=0.9, relheight=0.05)

        export_button = ctk.CTkButton(master=custom_plot_frame, text="Export data", fg_color="green")
        export_button.place(anchor=tk.CENTER, relx=0.5, rely=0.33)
        load_config_button = ctk.CTkButton(master=custom_plot_frame, text="Load config", fg_color="lightslategray")
        load_config_button.place(anchor=tk.CENTER, relx=0.5, rely=0.4, relheight=0.05)
        save_config_button = ctk.CTkButton(master=custom_plot_frame, text="Save config", fg_color="lightslategray")
        save_config_button.place(anchor=tk.CENTER, relx=0.5, rely=0.5, relheight=0.05)
        save_figure_button = ctk.CTkButton(master=custom_plot_frame, text="Save figure", fg_color="green")
        save_figure_button.place(anchor=tk.CENTER, relx=0.5, rely=0.6, relheight=0.05)
        draw_button = ctk.CTkButton(master=custom_plot_frame, text="Draw", fg_color="green")
        draw_button.place(anchor=tk.CENTER, relx=0.5, rely=0.8, relheight=0.1)

        self.buttons["axes"] = axes_button
        self.buttons["export"] = export_button
        self.buttons["save fig"] = save_figure_button
        self.buttons["load config"] = load_config_button
        self.buttons["save config"] = save_config_button
        self.buttons["draw"] = draw_button

        # ---------------- CONFIGURE
        load_clf_button.configure(command=self.load_clf)
        draw_button.configure(command=self.draw_figure)
        color_button.configure(command=partial(self.select_color, view=self, selection_button_name='color'))
        axes_button.configure(command=self.axes_toplevel)
        save_figure_button.configure(command=partial(self.save_figure, self.figures["feature importance"][0]))
        export_button.configure(command=partial(self.export_figure_data, self.figures["feature importance"][1]))
        save_config_button.configure(command=self.save_config)
        load_config_button.configure(command=self.load_config)

        linewidth_entry.configure(validate='focus',
                                  validatecommand=(self.register(partial(self.main_view.is_positive_int,
                                                                         linewidth_entry)), '%P'), )
        dpi_entry.configure(validate='focus',
                            validatecommand=(self.register(partial(self.main_view.is_positive_int,
                                                                   dpi_entry)), '%P'), )
        title_entry.configure(validate='focus',
                              validatecommand=(self.register(partial(self.main_view.has_forbidden_characters,
                                                                     title_entry)), '%P'), )

        # ----- TRACE
        alpha_var.trace("w", partial(self.trace_vars_to_model, "alpha"))
        title_size_var.trace("w", partial(self.trace_vars_to_model, "title size"))
        alpha_fill_var.trace("w", partial(self.trace_vars_to_model, "alpha fill"))
        fill_var.trace("w", partial(self.trace_vars_to_model, "fill"))
        linestyle_var.trace("w", partial(self.trace_vars_to_model, "linestyle"))
        title_font_var.trace("w", partial(self.trace_vars_to_model, "title font"))
        color_var.trace("w", partial(self.trace_vars_to_model, "color"))
        clf_type_var.trace("w", partial(self.trace_vars_to_model, "clf type"))
        linewidth_var.trace("w", partial(self.trace_vars_to_model, "linewidth"))
        load_clf_var.trace("w", partial(self.trace_vars_to_model, "load clf"))
        title_var.trace("w", partial(self.trace_vars_to_model, "title"))

        self.axes_toplevel()

    def select_color(self, view, selection_button_name):
        self.parent_view.parent_view.select_color(view=view, selection_button_name=selection_button_name)

    def update_slider_value(self, value, var):
        self.parent_view.update_slider_value(value, var)

    def dummy_figure(self):
        if self.controller:
            return self.controller.dummy_figure()

    def draw_figure(self, ):
        if self.controller:
            self.controller.draw_figure()

    def load_clf(self):
        if self.controller:
            self.controller.load_clf()

    def load_config(self):
        if self.controller:
            self.controller.load_config()

    def save_config(self):
        if self.controller:
            self.controller.save_config()

    def export_figure_data(self, ax):
        if self.controller:
            self.controller.export_figure_data(ax)

    def save_figure(self, fig):
        if self.controller:
            self.controller.save_figure(fig)

    def axes_toplevel(self):
        width = 500
        height = 800
        general_toplevel = ctk.CTkToplevel(width=width, height=height)
        general_toplevel.protocol('WM_DELETE_WINDOW', general_toplevel.withdraw)
        general_toplevel.withdraw()
        self.buttons["axes"].configure(
            command=partial(self.parent_view.parent_view.deiconify_toplevel, general_toplevel))

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

    def trace_vars_to_model(self, key, *args):
        if self.controller:
            self.controller.trace_vars_to_model(key, *args)
