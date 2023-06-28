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
from typing import Callable

import numpy as np
import seaborn as sns
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class AnalysisView(ctk.CTkFrame):
    def __init__(self, app, master, controller):
        super().__init__(master=app)
        self.master = master
        self.controller = controller

        self.analysis_subtabs = ctk.CTkTabview(master=self.master, corner_radius=10)
        self.analysis_subtabs.place(relwidth=1.0, relheight=1.0)
        self.analysis_subtabs.add("Feature importance")
        self.analysis_subtabs.add("Plot")
        self.analysis_subtabs.add("PCA")
        self.analysis_subtabs.add("Confusion")
        self.analysis_subtabs.add("Spike detection")

        self.entries = {}
        self.buttons = {}
        self.cbboxes = {}
        self.vars = {}
        self.switches = {}
        self.sliders = {}
        self.checkboxes = {}
        self.checkvars = {}
        self.rfc_params_stringvar = {}
        self.textboxes = {}
        self.canvas = {}

        self.manage_features_tab()

    def set_controller(self, controller):
        self.controller = controller

    def manage_features_tab(self):
        # ---------------- FRAMES
        init_frame = ctk.CTkFrame(master=self.analysis_subtabs.tab("Feature importance"))
        init_frame.place(relx=0, rely=0, relheight=0.1, relwidth=0.6)

        params_frame = ctk.CTkFrame(master=self.analysis_subtabs.tab("Feature importance"))
        params_frame.place(relx=0, rely=0.13, relheight=0.87, relwidth=0.6)

        plot_frame = ctk.CTkFrame(master=self.analysis_subtabs.tab("Feature importance"))
        plot_frame.place(relx=0.63, rely=0, relheight=0.8, relwidth=0.37)

        exec_frame = ctk.CTkFrame(master=self.analysis_subtabs.tab("Feature importance"))
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
        self.entries["load clf"] = load_clf_button

        clf_type_strvar = tk.StringVar()
        clf_type_strvar.set("Classifier type:")
        clf_type_label = ctk.CTkLabel(master=init_frame, textvariable=clf_type_strvar)
        clf_type_label.place(relx=0.35, rely=0.5)
        self.vars["clf type"] = clf_type_strvar

        # --------------- PARAMS
        body_frame = ctk.CTkFrame(master=params_frame, )
        body_frame.place(relx=0.02, rely=0.02, relwidth=0.46, relheight=0.66)
        annotate_frame = ctk.CTkFrame(master=params_frame, )
        annotate_frame.place(relx=0.02, rely=0.7, relwidth=0.46, relheight=0.28)
        axes_frame = ctk.CTkFrame(master=params_frame, )
        axes_frame.place(relx=0.5, rely=0.02, relwidth=0.48, relheight=0.31)
        ticks_frame = ctk.CTkFrame(master=params_frame, )
        ticks_frame.place(relx=0.5, rely=0.35, relwidth=0.48, relheight=0.31)
        legend_frame = ctk.CTkFrame(master=params_frame, )
        legend_frame.place(relx=0.5, rely=0.68, relwidth=0.48, relheight=0.30)

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
        title_label.place(relx=0.45, rely=0.1)
        title_strvar = tk.StringVar()
        title_entry = ctk.CTkEntry(master=body_frame, textvariable=title_strvar, state='normal')
        title_entry.place(relx=0.45, rely=0.18, relwidth=0.5)
        self.entries["fi title"] = title_entry
        self.vars["fi title"] = title_strvar

        linestyle_label = ctk.CTkLabel(master=body_frame, text="Linestyle:")
        linestyle_label.place(relx=0, rely=0.30)
        linestyle_cbbox = tk.ttk.Combobox(master=body_frame, values=list(p.LINESTYLES.keys()), state='readonly')
        linestyle_cbbox.set("solid")
        linestyle_cbbox.place(relx=0, rely=0.38, relwidth=0.40)
        self.cbboxes["fi linestyle"] = linestyle_cbbox

        linewidth_label = ctk.CTkLabel(master=body_frame, text="Linewidth:")
        linewidth_label.place(relx=0.5, rely=0.30)
        linewidth_strvar = tk.StringVar()
        linewidth_entry = ctk.CTkEntry(master=body_frame, textvariable=linewidth_strvar)
        linewidth_entry.place(relx=0.5, rely=0.38, relwidth=0.2)
        self.entries["fi linewidth"] = linewidth_entry
        self.vars["fi linewidth"] = linewidth_strvar

        color_label = ctk.CTkLabel(master=body_frame, text="Color:")
        color_label.place(relx=0, rely=0.50)
        color_var = tk.StringVar()
        color_var.set("deepskyblue")
        color_button = ctk.CTkButton(master=body_frame, textvariable=color_var,
                                     fg_color=color_var.get(), text_color='black')
        color_button.place(relx=0, rely=0.58)
        self.buttons["fi color"] = color_button
        self.vars["fi color"] = color_var

        alpha_label = ctk.CTkLabel(master=body_frame, text="Alpha:")
        alpha_label.place(relx=0, rely=0.68)
        alpha_slider = ctk.CTkSlider(master=body_frame, from_=0, to=1, number_of_steps=10)
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
        alpha_fill_slider.place(relx=0.5, rely=0.77, relwidth=0.4)
        alpha_fill_strvar = tk.StringVar()
        alpha_fill_strvar.set(str(alpha_fill_slider.get()))
        alpha_fill_value_label = ctk.CTkLabel(master=body_frame, textvariable=alpha_fill_strvar)
        alpha_fill_value_label.place(relx=0.7, rely=0.68)
        self.vars["fi alpha fill"] = alpha_fill_strvar
        self.sliders["fi alpha fill"] = alpha_fill_slider

        figsize_x_label = ctk.CTkLabel(master=body_frame, text="figure width:")
        figsize_x_label.place(relx=0, rely=0.85)
        figsize_x_slider = ctk.CTkSlider(master=body_frame, from_=5, to=20, number_of_steps=15)
        figsize_x_slider.place(relx=0, rely=0.93, relwidth=0.4)
        figsize_x_strvar = tk.StringVar()
        figsize_x_strvar.set(str(figsize_x_slider.get()))
        figsize_x_value_label = ctk.CTkLabel(master=body_frame, textvariable=figsize_x_strvar)
        figsize_x_value_label.place(relx=0.3, rely=0.85)
        self.vars["fi figsize x"] = figsize_x_strvar
        self.sliders["fi figsize x"] = figsize_x_slider
        
        figsize_y_label = ctk.CTkLabel(master=body_frame, text="figure height:")
        figsize_y_label.place(relx=0.5, rely=0.85)
        figsize_y_slider = ctk.CTkSlider(master=body_frame, from_=5, to=20, number_of_steps=15)
        figsize_y_slider.place(relx=0.5, rely=0.93, relwidth=0.4)
        figsize_y_strvar = tk.StringVar()
        figsize_y_strvar.set(str(figsize_y_slider.get()))
        figsize_y_value_label = ctk.CTkLabel(master=body_frame, textvariable=figsize_y_strvar)
        figsize_y_value_label.place(relx=0.8, rely=0.85)
        self.vars["fi figsize y"] = figsize_y_strvar
        self.sliders["fi figsize y"] = figsize_y_slider

        # ----- AXES
        axes_label = ctk.CTkLabel(master=axes_frame, text="AXES")
        axes_label.place(relx=0, rely=0)

        x_label = ctk.CTkLabel(master=axes_frame, text="x-axes label:")
        x_label.place(relx=0, rely=0.1)
        x_label_entry = ctk.CTkEntry(master=axes_frame, )
        x_label_entry.place(relx=0, rely=0.2, relwidth=0.4)
        self.entries["fi x label"] = x_label_entry

        y_label = ctk.CTkLabel(master=axes_frame, text="y-axes label:")
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

        x_size_label = ctk.CTkLabel(master=axes_frame, text="x-axes label size:")
        x_size_label.place(relx=0, rely=0.7)
        x_label_slider = ctk.CTkSlider(master=axes_frame, from_=8, to=32, number_of_steps=24)
        x_label_slider.place(relx=0, rely=0.85, relwidth=0.4)
        x_label_strvar = tk.StringVar()
        x_label_strvar.set(str(x_label_slider.get()))
        x_label_value_label = ctk.CTkLabel(master=axes_frame, textvariable=x_label_strvar)
        x_label_value_label.place(relx=0.3, rely=0.7)
        self.vars["fi x label size"] = x_label_strvar
        self.sliders["fi x label size"] = x_label_slider

        y_size_label = ctk.CTkLabel(master=axes_frame, text="y-axes label size:")
        y_size_label.place(relx=0.5, rely=0.7)
        y_label_slider = ctk.CTkSlider(master=axes_frame, from_=8, to=32, number_of_steps=24)
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

        n_ticks_label = ctk.CTkLabel(master=ticks_frame, text="Number of ticks:")
        n_ticks_label.place(relx=0, rely=0.1)
        n_ticks_entry = ctk.CTkEntry(master=ticks_frame, )
        n_ticks_entry.place(relx=0, rely=0.2, relwidth=0.2)
        self.entries["fi n ticks"] = n_ticks_entry

        x_ticks_rotation_label = ctk.CTkLabel(master=ticks_frame, text="x-axis tick rotation:")
        x_ticks_rotation_label.place(relx=0, rely=0.4)
        x_ticks_rotation_slider = ctk.CTkSlider(master=ticks_frame, from_=-180, to=180, number_of_steps=36)
        x_ticks_rotation_slider.place(relx=0, rely=0.55, relwidth=0.4)
        x_ticks_rotation_strvar = tk.StringVar()
        x_ticks_rotation_strvar.set(str(x_ticks_rotation_slider.get()))
        x_ticks_rotation_value_label = ctk.CTkLabel(master=ticks_frame, textvariable=x_ticks_rotation_strvar)
        x_ticks_rotation_value_label.place(relx=0.3, rely=0.4)
        self.vars["fi x ticks rotation"] = x_ticks_rotation_strvar
        self.sliders["fi x ticks rotation"] = x_ticks_rotation_slider

        y_ticks_rotation_label = ctk.CTkLabel(master=ticks_frame, text="y-axis tick rotation:")
        y_ticks_rotation_label.place(relx=0.5, rely=0.4)
        y_ticks_rotation_slider = ctk.CTkSlider(master=ticks_frame, from_=-180, to=180, number_of_steps=36)
        y_ticks_rotation_slider.place(relx=0.5, rely=0.55, relwidth=0.4)
        y_ticks_rotation_strvar = tk.StringVar()
        y_ticks_rotation_strvar.set(str(y_ticks_rotation_slider.get()))
        y_ticks_rotation_value_label = ctk.CTkLabel(master=ticks_frame, textvariable=y_ticks_rotation_strvar)
        y_ticks_rotation_value_label.place(relx=0.8, rely=0.4)
        self.vars["fi y ticks rotation"] = y_ticks_rotation_strvar
        self.sliders["fi y ticks rotation"] = y_ticks_rotation_slider

        x_ticks_label = ctk.CTkLabel(master=ticks_frame, text="x-axis tick size:")
        x_ticks_label.place(relx=0, rely=0.7)
        x_ticks_slider = ctk.CTkSlider(master=ticks_frame, from_=8, to=32, number_of_steps=24)
        x_ticks_slider.place(relx=0, rely=0.85, relwidth=0.4)
        x_ticks_strvar = tk.StringVar()
        x_ticks_strvar.set(str(x_ticks_slider.get()))
        x_ticks_value_label = ctk.CTkLabel(master=ticks_frame, textvariable=x_ticks_strvar)
        x_ticks_value_label.place(relx=0.3, rely=0.7)
        self.vars["fi x ticks size"] = x_ticks_strvar
        self.sliders["fi x ticks size"] = x_ticks_slider

        y_ticks_label = ctk.CTkLabel(master=ticks_frame, text="y-axeis tick size:")
        y_ticks_label.place(relx=0.5, rely=0.7)
        y_ticks_slider = ctk.CTkSlider(master=ticks_frame, from_=8, to=32, number_of_steps=24)
        y_ticks_slider.place(relx=0.5, rely=0.85, relwidth=0.4)
        y_ticks_strvar = tk.StringVar()
        y_ticks_strvar.set(str(y_ticks_slider.get()))
        y_ticks_value_label = ctk.CTkLabel(master=ticks_frame, textvariable=y_ticks_strvar)
        y_ticks_value_label.place(relx=0.8, rely=0.7)
        self.vars["fi y label size"] = y_ticks_strvar
        self.sliders["fi y label size"] = y_ticks_slider

        # -----LEGEND
        legend_label = ctk.CTkLabel(master=legend_frame, text="LEGEND")
        legend_label.place(relx=0, rely=0)

        legend_font_label = ctk.CTkLabel(master=legend_frame, text="legend font:")
        legend_font_label.place(relx=0, rely=0.2)
        legend_font_cbbox = tk.ttk.Combobox(master=legend_frame, values=p.FONTS, state='readonly')
        legend_font_cbbox.set(p.DEFAULT_FONT)
        legend_font_cbbox.place(relx=0, rely=0.2, relwidth=0.4)
        self.cbboxes["fi legend font"] = legend_font_cbbox
        
        legend_size_label = ctk.CTkLabel(master=legend_frame, text="Legend size:")
        legend_size_label.place(relx=0, rely=0.4)
        legend_size_slider = ctk.CTkSlider(master=legend_frame,  from_=8, to=32, number_of_steps=24)
        legend_size_slider.place(relx=0, rely=0.55, relwidth=0.4)
        legend_size_strvar = tk.StringVar()
        legend_size_strvar.set(str(legend_size_slider.get()))
        legend_size_value_label = ctk.CTkLabel(master=legend_frame, textvariable=legend_size_strvar)
        legend_size_value_label.place(relx=0.3, rely=0.4)
        self.vars["fi legend size"] = legend_size_strvar
        self.sliders["fi legend size"] = legend_size_slider

        legend_autopos_intvar = tk.IntVar()
        legend_autopos_intvar.set(1)
        legend_autopos_ckbox = ctk.CTkCheckBox(master=legend_frame, variable=legend_autopos_intvar, text="Auto positioning")
        legend_autopos_ckbox.place(relx=0.5, rely=0.5)
        self.vars["fi legend autopos"] = legend_autopos_intvar
        self.checkboxes["fi legend autopos"] = legend_autopos_ckbox

        legend_x_pos_label = ctk.CTkLabel(master=legend_frame, text="Legend x position:")
        legend_x_pos_label.place(relx=0, rely=0.7)
        legend_x_pos_slider = ctk.CTkSlider(master=legend_frame, from_=0, to=1, number_of_steps=20)
        legend_x_pos_slider.place(relx=0, rely=0.85, relwidth=0.4)
        legend_x_pos_strvar = tk.StringVar()
        legend_x_pos_strvar.set(str(legend_x_pos_slider.get()))
        legend_x_pos_value_label = ctk.CTkLabel(master=legend_frame, textvariable=legend_x_pos_strvar)
        legend_x_pos_value_label.place(relx=0.3, rely=0.7)
        self.vars["fi legend x pos"] = legend_x_pos_strvar
        self.sliders["fi legend x pos"] = legend_x_pos_slider
        
        legend_y_pos_label = ctk.CTkLabel(master=legend_frame, text="Legend y position:")
        legend_y_pos_label.place(relx=0.5, rely=0.7)
        legend_y_pos_slider = ctk.CTkSlider(master=legend_frame, from_=0, to=1, number_of_steps=20)
        legend_y_pos_slider.place(relx=0.5, rely=0.85, relwidth=0.4)
        legend_y_pos_strvar = tk.StringVar()
        legend_y_pos_strvar.set(str(legend_y_pos_slider.get()))
        legend_y_pos_value_label = ctk.CTkLabel(master=legend_frame, textvariable=legend_y_pos_strvar)
        legend_y_pos_value_label.place(relx=0.8, rely=0.7)
        self.vars["fi legend y pos"] = legend_y_pos_strvar
        self.sliders["fi legend y pos"] = legend_y_pos_slider
        
        # ----- ANNOTATE
        annotate_label = ctk.CTkLabel(master=annotate_frame, text="ANNOTATE")
        annotate_label.place(relx=0, rely=0)

        annotate_text_label = ctk.CTkLabel(master=annotate_frame, text="Annotation text:")
        annotate_text_label.place(relx=0, rely=0.2)

        annotate_textbox = ctk.CTkTextbox(master=annotate_frame, wrap='word')
        annotate_textbox.place(relx=0, rely=0.35, relheight=0.55, relwidth=0.4)
        self.textboxes["fi annotate"] = annotate_textbox
        
        annotate_font_label = ctk.CTkLabel(master=annotate_frame, text="annotate font:")
        annotate_font_label.place(relx=0, rely=0.2)
        annotate_font_cbbox = tk.ttk.Combobox(master=annotate_frame, values=p.FONTS, state='readonly')
        annotate_font_cbbox.set(p.DEFAULT_FONT)
        annotate_font_cbbox.place(relx=0.5, rely=0.2, relwidth=0.4)
        self.cbboxes["fi annotate font"] = annotate_font_cbbox

        annotate_x_pos_label = ctk.CTkLabel(master=annotate_frame, text="x position:")
        annotate_x_pos_label.place(relx=0.5, rely=0.4)
        annotate_x_pos_slider = ctk.CTkSlider(master=annotate_frame, from_=0, to=1, number_of_steps=20)
        annotate_x_pos_slider.place(relx=0.5, rely=0.55, relwidth=0.4)
        annotate_x_pos_strvar = tk.StringVar()
        annotate_x_pos_strvar.set(str(annotate_x_pos_slider.get()))
        annotate_x_pos_value_label = ctk.CTkLabel(master=annotate_frame, textvariable=annotate_x_pos_strvar)
        annotate_x_pos_value_label.place(relx=0.8, rely=0.4)
        self.vars["fi annotate x pos"] = annotate_x_pos_strvar
        self.sliders["fi annotate x pos"] = annotate_x_pos_slider

        annotate_y_pos_label = ctk.CTkLabel(master=annotate_frame, text="y position:")
        annotate_y_pos_label.place(relx=0.5, rely=0.7)
        annotate_y_pos_slider = ctk.CTkSlider(master=annotate_frame, from_=0, to=1, number_of_steps=20)
        annotate_y_pos_slider.place(relx=0.5, rely=0.85, relwidth=0.4)
        annotate_y_pos_strvar = tk.StringVar()
        annotate_y_pos_strvar.set(str(annotate_y_pos_slider.get()))
        annotate_y_pos_value_label = ctk.CTkLabel(master=annotate_frame, textvariable=annotate_y_pos_strvar)
        annotate_y_pos_value_label.place(relx=0.8, rely=0.7)
        self.vars["fi annotate y pos"] = annotate_y_pos_strvar
        self.sliders["fi annotate y pos"] = annotate_y_pos_slider
        
        
        # --------------- PLOT
        fig, ax = self.create_figure()
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.get_tk_widget().place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.8)
        self.canvas["feature importance"] = canvas

        # --------------- EXEC
        draw_button = ctk.CTkButton(master=exec_frame, text="Draw", fg_color="green")
        draw_button.place(anchor=tk.CENTER, relx=0.75, rely=0.5, relheight=0.5)
        self.buttons["draw"] = draw_button

        # ---------------- CONFIGURE
        load_clf_button.configure(command=self.load_clf)
        draw_button.configure(command=partial(self.redraw_figure, ax))
        alpha_slider.configure(command=partial(self.update_slider_value, var=alpha_strvar))
        alpha_fill_slider.configure(command=partial(self.update_slider_value, var=alpha_fill_strvar))
        color_button.configure(command=partial(self.select_color, 'fi color'))
        y_label_slider.configure(command=partial(self.update_slider_value, var=y_label_strvar))
        x_label_slider.configure(command=partial(self.update_slider_value, var=x_label_strvar))
        x_ticks_slider.configure(command=partial(self.update_slider_value, var=x_ticks_strvar))
        y_ticks_slider.configure(command=partial(self.update_slider_value, var=y_ticks_strvar))
        x_ticks_rotation_slider.configure(command=partial(self.update_slider_value, var=x_ticks_rotation_strvar))
        y_ticks_rotation_slider.configure(command=partial(self.update_slider_value, var=y_ticks_rotation_strvar))
        legend_x_pos_slider.configure(command=partial(self.update_slider_value, var=legend_x_pos_strvar))
        legend_y_pos_slider.configure(command=partial(self.update_slider_value, var=legend_y_pos_strvar))
        legend_size_slider.configure(command=partial(self.update_slider_value, var=legend_size_strvar))
        annotate_x_pos_slider.configure(command=partial(self.update_slider_value, var=annotate_x_pos_strvar))
        annotate_y_pos_slider.configure(command=partial(self.update_slider_value, var=annotate_y_pos_strvar))
        figsize_x_slider.configure(command=partial(self.update_slider_value, var=figsize_x_strvar))
        figsize_y_slider.configure(command=partial(self.update_slider_value, var=figsize_y_strvar))

    def load_clf(self):
        if self.controller:
            self.controller.load_clf()

    def select_color(self, selection_button_name):
        color_window = ctk.CTkToplevel()
        color_window.title("Color Selection")
        max_col = 8
        col = 0
        row = 0
        for c in p.COLORS:
            color_button = ctk.CTkButton(master=color_window, text=c, text_color="black", 
                                         height=30, width=130, fg_color=c,
                                         )
            color_button.grid(row=row, column=col, padx=3, pady=3)
            color_button.configure(command=partial(self.chose_color, color_button, selection_button_name))

            if col >= max_col:
                col = 0
                row += 1
            else:
                col += 1

    def chose_color(self, color_button, selection_button_name):
        self.buttons[selection_button_name].configure(fg_color=color_button.cget('fg_color'))
        self.vars[selection_button_name].set(color_button.cget('text'))
        
    @staticmethod
    def update_slider_value(value, var):
        var.set(str(round(value, 2)))

    def create_figure(self):
        if self.controller:
            return self.controller.create_figure()

    def redraw_figure(self, ax):
        if self.controller:
            self.controller.redraw_figure(ax)
