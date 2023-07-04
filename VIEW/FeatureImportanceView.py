import tkinter as tk
from functools import partial
from tkinter import ttk

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import params as p
from CONTROLLER.FeatureImportanceController import FeatureImportanceController


class FeatureImportanceView(ctk.CTkFrame):
    def __init__(self, app, master, parent_view):
        super().__init__(master=app)
        self.master = master
        self.parent_view = parent_view
        self.controller = FeatureImportanceController(self,)

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
        init_frame = ctk.CTkFrame(master=self.master)
        init_frame.place(relx=0, rely=0, relheight=0.1, relwidth=0.6)

        params_frame = ctk.CTkFrame(master=self.master)
        params_frame.place(relx=0, rely=0.13, relheight=0.87, relwidth=0.6)

        plot_frame = ctk.CTkFrame(master=self.master)
        plot_frame.place(relx=0.63, rely=0, relheight=0.8, relwidth=0.37)

        exec_frame = ctk.CTkFrame(master=self.master)
        exec_frame.place(relx=0.63, rely=0.85, relheight=0.15, relwidth=0.37)

        # --------------- INIT FRAME
        load_clf_label = ctk.CTkLabel(master=init_frame, text="Loaded trained classifier:")
        load_clf_label.place(relx=0, rely=0)

        load_clf_button = ctk.CTkButton(master=init_frame, text="Load Classifier")
        load_clf_button.place(relx=0.15, rely=0)
        self.buttons["load clf"] = load_clf_button

        load_clf_strvar = tk.StringVar()
        load_clf_entry = ctk.CTkEntry(master=init_frame, state='disabled', textvariable=load_clf_strvar)
        load_clf_entry.place(relx=0, rely=0.5, relwidth=0.3)
        self.vars["load clf"] = load_clf_strvar
        self.entries["load clf"] = load_clf_entry

        clf_type_strvar = tk.StringVar()
        clf_type_strvar.set("Classifier type:")
        clf_type_label = ctk.CTkLabel(master=init_frame, textvariable=clf_type_strvar)
        clf_type_label.place(relx=0.35, rely=0.5)
        self.vars["clf type"] = clf_type_strvar

        # --------------- PARAMS
        body_frame = ctk.CTkFrame(master=params_frame, )
        body_frame.place(relx=0.02, rely=0.02, relwidth=0.46, relheight=1)
        axes_frame = ctk.CTkFrame(master=params_frame, )
        axes_frame.place(relx=0.5, rely=0.02, relwidth=0.48, relheight=0.38)
        ticks_frame = ctk.CTkFrame(master=params_frame, )
        ticks_frame.place(relx=0.5, rely=0.42, relwidth=0.48, relheight=0.58)

        # ----- BODY
        body_label = ctk.CTkLabel(master=body_frame, text="BODY")
        body_label.place(relx=0, rely=0)

        title_font_label = ctk.CTkLabel(master=body_frame, text="Title font:")
        title_font_label.place(relx=0, rely=0.1)
        title_font_cbbox = tk.ttk.Combobox(master=body_frame, values=p.FONTS, state='readonly')
        title_font_cbbox.set(p.DEFAULT_FONT)
        title_font_cbbox.place(relx=0, rely=0.18, relwidth=0.4)
        self.cbboxes["fi title font"] = title_font_cbbox

        title_label = ctk.CTkLabel(master=body_frame, text="Title:")
        title_label.place(relx=0.45, rely=0.0)
        title_strvar = tk.StringVar()
        title_entry = ctk.CTkEntry(master=body_frame, textvariable=title_strvar, state='normal')
        title_entry.place(relx=0.45, rely=0.07, relwidth=0.5)
        self.entries["fi title"] = title_entry
        self.vars["fi title"] = title_strvar

        title_size_label = ctk.CTkLabel(master=body_frame, text="Title size:")
        title_size_label.place(relx=0.5, rely=0.15)
        title_size_slider = ctk.CTkSlider(master=body_frame, from_=8, to=32, number_of_steps=24)
        title_size_slider.set(p.DEFAULT_FONTSIZE)
        title_size_slider.place(relx=0.5, rely=0.23, relwidth=0.4)
        title_size_strvar = tk.StringVar()
        title_size_strvar.set(str(title_size_slider.get()))
        title_size_value_label = ctk.CTkLabel(master=body_frame, textvariable=title_size_strvar)
        title_size_value_label.place(relx=0.8, rely=0.15)
        self.vars["fi title size"] = title_size_strvar
        self.sliders["fi title size"] = title_size_slider

        linestyle_label = ctk.CTkLabel(master=body_frame, text="Linestyle:")
        linestyle_label.place(relx=0, rely=0.30)
        linestyle_cbbox = tk.ttk.Combobox(master=body_frame, values=list(p.LINESTYLES.keys()), state='readonly')
        linestyle_cbbox.set("solid")
        linestyle_cbbox.place(relx=0, rely=0.38, relwidth=0.40)
        self.cbboxes["fi linestyle"] = linestyle_cbbox

        linewidth_label = ctk.CTkLabel(master=body_frame, text="Linewidth:")
        linewidth_label.place(relx=0.5, rely=0.30)
        linewidth_strvar = tk.StringVar()
        linewidth_strvar.set("1")
        linewidth_entry = ctk.CTkEntry(master=body_frame, textvariable=linewidth_strvar)
        linewidth_entry.place(relx=0.5, rely=0.38, relwidth=0.2)
        self.entries["fi linewidth"] = linewidth_entry
        self.vars["fi linewidth"] = linewidth_strvar

        color_label = ctk.CTkLabel(master=body_frame, text="Color:")
        color_label.place(relx=0, rely=0.50)
        color_var = tk.StringVar()
        color_var.set("green")
        color_button = ctk.CTkButton(master=body_frame, textvariable=color_var,
                                     fg_color=color_var.get(), text_color='black')
        color_button.place(relx=0, rely=0.58)
        self.buttons["fi color"] = color_button
        self.vars["fi color"] = color_var

        alpha_label = ctk.CTkLabel(master=body_frame, text="Alpha:")
        alpha_label.place(relx=0, rely=0.68)
        alpha_slider = ctk.CTkSlider(master=body_frame, from_=0, to=1, number_of_steps=10)
        alpha_slider.set(p.DEFAULT_LINEALPHA)
        alpha_slider.place(relx=0, rely=0.77, relwidth=0.4)
        alpha_strvar = tk.StringVar()
        alpha_strvar.set(str(alpha_slider.get()))
        alpha_value_label = ctk.CTkLabel(master=body_frame, textvariable=alpha_strvar)
        alpha_value_label.place(relx=0.2, rely=0.68)
        self.vars["fi alpha"] = alpha_strvar
        self.sliders["fi alpha"] = alpha_slider

        fill_label = ctk.CTkLabel(master=body_frame, text="Fill:")
        fill_label.place(relx=0.5, rely=0.5)
        fill_cbbox = tk.ttk.Combobox(master=body_frame, values=["None", "Above", "Below"], state='readonly')
        fill_cbbox.set("None")
        fill_cbbox.place(relx=0.5, rely=0.58, relwidth=0.40)
        self.cbboxes["fi fill"] = fill_cbbox

        alpha_fill_label = ctk.CTkLabel(master=body_frame, text="Fill alpha:")
        alpha_fill_label.place(relx=0.5, rely=0.68)
        alpha_fill_slider = ctk.CTkSlider(master=body_frame, from_=0, to=1, number_of_steps=10)
        alpha_fill_slider.set(p.DEFAULT_FILLALPHA)
        alpha_fill_slider.place(relx=0.5, rely=0.77, relwidth=0.4)
        alpha_fill_strvar = tk.StringVar()
        alpha_fill_strvar.set(str(alpha_fill_slider.get()))
        alpha_fill_value_label = ctk.CTkLabel(master=body_frame, textvariable=alpha_fill_strvar)
        alpha_fill_value_label.place(relx=0.7, rely=0.68)
        self.vars["fi alpha fill"] = alpha_fill_strvar
        self.sliders["fi alpha fill"] = alpha_fill_slider

        dpi_label = ctk.CTkLabel(master=body_frame, text="Figure dpi:")
        dpi_label.place(relx=0, rely=0.85)
        dpi_strvar = tk.StringVar()
        dpi_strvar.set("100")
        dpi_entry = ctk.CTkEntry(master=body_frame, textvariable=dpi_strvar)
        dpi_entry.place(relx=0, rely=0.9, relwidth=0.2)
        self.entries["fi dpi"] = dpi_entry
        self.vars["fi dpi"] = dpi_strvar

        # ----- AXES
        axes_label = ctk.CTkLabel(master=axes_frame, text="AXES")
        axes_label.place(relx=0, rely=0)

        x_label = ctk.CTkLabel(master=axes_frame, text="x-axis label:")
        x_label.place(relx=0, rely=0.1)
        x_label_entry = ctk.CTkEntry(master=axes_frame, )
        x_label_entry.place(relx=0, rely=0.2, relwidth=0.4)
        self.entries["fi x label"] = x_label_entry

        y_label = ctk.CTkLabel(master=axes_frame, text="y-axis label:")
        y_label.place(relx=0.5, rely=0.1)
        y_label_entry = ctk.CTkEntry(master=axes_frame, )
        y_label_entry.place(relx=0.5, rely=0.2, relwidth=0.4)
        self.entries["fi y label"] = y_label_entry

        axes_font_label = ctk.CTkLabel(master=axes_frame, text="Axes font:")
        axes_font_label.place(relx=0, rely=0.4)
        axes_font_cbbox = tk.ttk.Combobox(master=axes_frame, values=p.FONTS, state='readonly')
        axes_font_cbbox.set(p.DEFAULT_FONT)
        axes_font_cbbox.place(relx=0, rely=0.5, relwidth=0.4)
        self.cbboxes["fi axes font"] = axes_font_cbbox

        x_size_label = ctk.CTkLabel(master=axes_frame, text="x-axis label size:")
        x_size_label.place(relx=0, rely=0.7)
        x_label_slider = ctk.CTkSlider(master=axes_frame, from_=8, to=32, number_of_steps=24)
        x_label_slider.set(p.DEFAULT_FONTSIZE)
        x_label_slider.place(relx=0, rely=0.85, relwidth=0.4)
        x_label_strvar = tk.StringVar()
        x_label_strvar.set(str(x_label_slider.get()))
        x_label_value_label = ctk.CTkLabel(master=axes_frame, textvariable=x_label_strvar)
        x_label_value_label.place(relx=0.3, rely=0.7)
        self.vars["fi x label size"] = x_label_strvar
        self.sliders["fi x label size"] = x_label_slider

        y_size_label = ctk.CTkLabel(master=axes_frame, text="y-axis label size:")
        y_size_label.place(relx=0.5, rely=0.7)
        y_label_slider = ctk.CTkSlider(master=axes_frame, from_=8, to=32, number_of_steps=24)
        y_label_slider.set(p.DEFAULT_FONTSIZE)
        y_label_slider.place(relx=0.5, rely=0.85, relwidth=0.4)
        y_label_strvar = tk.StringVar()
        y_label_strvar.set(str(y_label_slider.get()))
        y_label_value_label = ctk.CTkLabel(master=axes_frame, textvariable=y_label_strvar)
        y_label_value_label.place(relx=0.8, rely=0.7)
        self.vars["fi y label size"] = y_label_strvar
        self.sliders["fi y label size"] = y_label_slider

        # -----TICKS
        ticks_label = ctk.CTkLabel(master=ticks_frame, text="TICKS")
        ticks_label.place(relx=0, rely=0)

        n_xticks_label = ctk.CTkLabel(master=ticks_frame, text="Number of x ticks:")
        n_xticks_label.place(relx=0, rely=0.1)
        n_xticks_strvar = tk.StringVar()
        n_xticks_strvar.set(p.DEFAULT_NTICKS)
        n_xticks_entry = ctk.CTkEntry(master=ticks_frame, textvariable=n_xticks_strvar)
        n_xticks_entry.place(relx=0, rely=0.2, relwidth=0.2)
        self.entries["fi n x ticks"] = n_xticks_entry
        self.vars["fi n x ticks"] = n_xticks_strvar

        n_yticks_label = ctk.CTkLabel(master=ticks_frame, text="Number of y ticks:")
        n_yticks_label.place(relx=0.5, rely=0.1)
        n_yticks_strvar = tk.StringVar()
        n_yticks_strvar.set(p.DEFAULT_NTICKS)
        n_yticks_entry = ctk.CTkEntry(master=ticks_frame, textvariable=n_yticks_strvar)
        n_yticks_entry.place(relx=0.5, rely=0.2, relwidth=0.2)
        self.entries["fi n y ticks"] = n_yticks_entry
        self.vars["fi n y ticks"] = n_yticks_strvar

        x_ticks_rotation_label = ctk.CTkLabel(master=ticks_frame, text="x-axis tick rotation:")
        x_ticks_rotation_label.place(relx=0, rely=0.3)
        x_ticks_rotation_slider = ctk.CTkSlider(master=ticks_frame, from_=-180, to=180, number_of_steps=36)
        x_ticks_rotation_slider.set(p.DEFAULT_FONTROTATION)
        x_ticks_rotation_slider.place(relx=0, rely=0.4, relwidth=0.4)
        x_ticks_rotation_strvar = tk.StringVar()
        x_ticks_rotation_strvar.set(str(x_ticks_rotation_slider.get()))
        x_ticks_rotation_value_label = ctk.CTkLabel(master=ticks_frame, textvariable=x_ticks_rotation_strvar)
        x_ticks_rotation_value_label.place(relx=0.3, rely=0.3)
        self.vars["fi x ticks rotation"] = x_ticks_rotation_strvar
        self.sliders["fi x ticks rotation"] = x_ticks_rotation_slider

        y_ticks_rotation_label = ctk.CTkLabel(master=ticks_frame, text="y-axis tick rotation:")
        y_ticks_rotation_label.place(relx=0.5, rely=0.3)
        y_ticks_rotation_slider = ctk.CTkSlider(master=ticks_frame, from_=-180, to=180, number_of_steps=36)
        y_ticks_rotation_slider.set(p.DEFAULT_FONTROTATION)
        y_ticks_rotation_slider.place(relx=0.5, rely=0.4, relwidth=0.4)
        y_ticks_rotation_strvar = tk.StringVar()
        y_ticks_rotation_strvar.set(str(y_ticks_rotation_slider.get()))
        y_ticks_rotation_value_label = ctk.CTkLabel(master=ticks_frame, textvariable=y_ticks_rotation_strvar)
        y_ticks_rotation_value_label.place(relx=0.8, rely=0.3)
        self.vars["fi y ticks rotation"] = y_ticks_rotation_strvar
        self.sliders["fi y ticks rotation"] = y_ticks_rotation_slider

        x_ticks_label = ctk.CTkLabel(master=ticks_frame, text="x-axis tick size:")
        x_ticks_label.place(relx=0, rely=0.6)
        x_ticks_slider = ctk.CTkSlider(master=ticks_frame, from_=8, to=32, number_of_steps=24)
        x_ticks_slider.set(p.DEFAULT_FONTSIZE)
        x_ticks_slider.place(relx=0, rely=0.7, relwidth=0.4)
        x_ticks_strvar = tk.StringVar()
        x_ticks_strvar.set(str(x_ticks_slider.get()))
        x_ticks_value_label = ctk.CTkLabel(master=ticks_frame, textvariable=x_ticks_strvar)
        x_ticks_value_label.place(relx=0.3, rely=0.6)
        self.vars["fi x ticks size"] = x_ticks_strvar
        self.sliders["fi x ticks size"] = x_ticks_slider

        y_ticks_label = ctk.CTkLabel(master=ticks_frame, text="y-axis tick size:")
        y_ticks_label.place(relx=0.5, rely=0.6)
        y_ticks_slider = ctk.CTkSlider(master=ticks_frame, from_=8, to=32, number_of_steps=24)
        y_ticks_slider.set(p.DEFAULT_FONTSIZE)
        y_ticks_slider.place(relx=0.5, rely=0.7, relwidth=0.4)
        y_ticks_strvar = tk.StringVar()
        y_ticks_strvar.set(str(y_ticks_slider.get()))
        y_ticks_value_label = ctk.CTkLabel(master=ticks_frame, textvariable=y_ticks_strvar)
        y_ticks_value_label.place(relx=0.8, rely=0.6)
        self.vars["fi y ticks size"] = y_ticks_strvar
        self.sliders["fi y ticks size"] = y_ticks_slider

        round_xticks_label = ctk.CTkLabel(master=ticks_frame, text="Round x ticks:")
        round_xticks_label.place(relx=0, rely=0.8)
        round_xticks_strvar = tk.StringVar()
        round_xticks_strvar.set(p.DEFAULT_ROUND)
        round_xticks_entry = ctk.CTkEntry(master=ticks_frame, textvariable=round_xticks_strvar)
        round_xticks_entry.place(relx=0, rely=0.9, relwidth=0.2)
        self.entries["fi round x ticks"] = round_xticks_entry
        self.vars["fi round x ticks"] = round_xticks_strvar

        round_yticks_label = ctk.CTkLabel(master=ticks_frame, text="Round y ticks:")
        round_yticks_label.place(relx=0.5, rely=0.8)
        round_yticks_strvar = tk.StringVar()
        round_yticks_strvar.set(p.DEFAULT_ROUND)
        round_yticks_entry = ctk.CTkEntry(master=ticks_frame, textvariable=round_yticks_strvar)
        round_yticks_entry.place(relx=0.5, rely=0.9, relwidth=0.2)
        self.entries["fi round y ticks"] = round_yticks_entry
        self.vars["fi round y ticks"] = round_yticks_strvar

        # --------------- PLOT
        fig, ax = self.dummy_figure()
        self.figures["feature importance"] = (fig, ax)
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.get_tk_widget().place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.96)
        self.canvas["feature importance"] = canvas

        # --------------- EXEC
        export_button = ctk.CTkButton(master=exec_frame, text="Export data", fg_color="green")
        export_button.place(anchor=tk.CENTER, relx=0.5, rely=0.33)
        self.buttons["fi export"] = export_button
        save_figure_button = ctk.CTkButton(master=exec_frame, text="Save figure", fg_color="green")
        save_figure_button.place(anchor=tk.CENTER, relx=0.5, rely=0.66)
        self.buttons["fi save fig"] = save_figure_button
        load_config_button = ctk.CTkButton(master=exec_frame, text="Load config", fg_color="lightslategray")
        load_config_button.place(anchor=tk.CENTER, relx=0.25, rely=0.33)
        self.buttons["fi load config"] = load_config_button
        save_config_button = ctk.CTkButton(master=exec_frame, text="Save config", fg_color="lightslategray")
        save_config_button.place(anchor=tk.CENTER, relx=0.25, rely=0.66)
        self.buttons["fi save config"] = save_config_button
        draw_button = ctk.CTkButton(master=exec_frame, text="Draw", fg_color="green")
        draw_button.place(anchor=tk.CENTER, relx=0.75, rely=0.5, relheight=0.5)
        self.buttons["fi draw"] = draw_button

        # ---------------- CONFIGURE
        load_clf_button.configure(command=self.load_clf)
        draw_button.configure(command=self.draw_figure)
        title_size_slider.configure(command=partial(self.update_slider_value, var=title_size_strvar))
        alpha_slider.configure(command=partial(self.update_slider_value, var=alpha_strvar))
        alpha_fill_slider.configure(command=partial(self.update_slider_value, var=alpha_fill_strvar))
        color_button.configure(command=partial(self.select_color, 'fi color'))

        y_label_slider.configure(command=partial(self.update_slider_value, var=y_label_strvar))
        x_label_slider.configure(command=partial(self.update_slider_value, var=x_label_strvar))
        x_ticks_slider.configure(command=partial(self.update_slider_value, var=x_ticks_strvar))
        y_ticks_slider.configure(command=partial(self.update_slider_value, var=y_ticks_strvar))
        x_ticks_rotation_slider.configure(command=partial(self.update_slider_value, var=x_ticks_rotation_strvar))
        y_ticks_rotation_slider.configure(command=partial(self.update_slider_value, var=y_ticks_rotation_strvar))

        save_figure_button.configure(command=partial(self.save_figure, self.figures["feature importance"][0]))
        export_button.configure(command=partial(self.export_figure_data, self.figures["feature importance"][1]))

        save_config_button.configure(command=self.save_config)
        load_config_button.configure(command=self.load_config)

    def select_color(self):
        self.parent_view.select_color()
        
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

