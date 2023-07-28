import tkinter as tk
from functools import partial
from tkinter import ttk

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import params as p
from CONTROLLER.PcaController import PcaController


class PcaView(ctk.CTkFrame):
    def __init__(self, app, master, parent_view):
        super().__init__(master=app)
        self.master = master
        self.parent_view = parent_view
        self.controller = PcaController(self, )

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
        self.scrollable_frames = {}

        self.labels_subframes = {}
        self.manage_pca_tab()



    def manage_pca_tab(self):
        # ---------------- FRAMES
        load_frame = ctk.CTkFrame(master=self.master)
        load_frame.place(relx=0, rely=0, relheight=0.1, relwidth=0.31)

        curves_frame = ctk.CTkFrame(master=self.master)
        curves_frame.place(relx=0, rely=0.13, relheight=0.87, relwidth=0.31)
        general_settings_frame = ctk.CTkFrame(master=curves_frame)
        general_settings_frame.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.32)
        pca_frame = ctk.CTkScrollableFrame(master=curves_frame)
        pca_frame.place(relx=0.01, rely=0.35, relwidth=0.98, relheight=0.64)
        pca_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frames["ydata"] = pca_frame

        params_frame = ctk.CTkFrame(master=self.master)
        params_frame.place(relx=0.32, rely=0, relheight=1, relwidth=0.30)
        axes_frame = ctk.CTkFrame(master=params_frame)
        axes_frame.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.38)
        ticks_frame = ctk.CTkFrame(master=params_frame)
        ticks_frame.place(relx=0.01, rely=0.4, relwidth=0.98, relheight=0.39)
        legend_frame = ctk.CTkFrame(master=params_frame)
        legend_frame.place(relx=0.01, rely=0.8, relwidth=0.98, relheight=0.19)

        plot_frame = ctk.CTkFrame(master=self.master)
        plot_frame.place(relx=0.63, rely=0, relheight=0.8, relwidth=0.37)

        exec_frame = ctk.CTkFrame(master=self.master)
        exec_frame.place(relx=0.63, rely=0.85, relheight=0.15, relwidth=0.37)

        # --------------- INIT FRAME
        load_dataset_button = ctk.CTkButton(master=load_frame, text="Load dataset:")
        load_dataset_button.place(relx=0.0, rely=0)
        self.buttons["load dataset"] = load_dataset_button

        load_dataset_strvar = tk.StringVar()
        load_dataset_entry = ctk.CTkEntry(master=load_frame, state='disabled', textvariable=load_dataset_strvar)
        load_dataset_entry.place(relx=0, rely=0.5, relwidth=0.5)
        self.vars["load dataset"] = load_dataset_strvar
        self.entries["load dataset"] = load_dataset_entry

        # ------ GENERAL SETTINGS
        general_settings_label = ctk.CTkLabel(master=general_settings_frame, text='GENERAL SETTINGS')
        general_settings_label.place(relx=0, rely=0)

        label_column_label = ctk.CTkLabel(master=general_settings_label, text="Labels column:")
        label_column_label.place(relx=0, rely=0.2)
        label_column_cbbox = tk.ttk.Combobox(master=general_settings_frame, values=['None', ], state='readonly')
        label_column_cbbox.place(relx=0, rely=0.3, relwidth=0.4)
        self.cbboxes["label column"] = label_column_cbbox

        n_components_label = ctk.CTkLabel(master=general_settings_frame, text="Number of components:")
        n_components_label.place(relx=0.5, rely=0.15)
        n_components_var = tk.StringVar()
        n_components_var.set("2")
        n_components_entry = ctk.CTkEntry(master=general_settings_frame, state='normal', textvariable=n_components_var)
        n_components_entry.place(relx=0.5, rely=0.3, relwidth=0.2)
        self.entries["n components"] = n_components_entry
        self.entries["n components"] = n_components_var

        label_2D = ctk.CTkLabel(master=general_settings_frame, text="2D settings:")
        label_2D.place(relx=0, rely=0.5)
        ellipsis_var = tk.IntVar()
        ellipsis_var.set(1)
        ellipsis_ckbox = ctk.CTkCheckBox(master=general_settings_frame, variable=ellipsis_var, text='Confidence ellipsis')
        ellipsis_ckbox.place(relx=0, rely=0.65)
        self.vars["ellipsis"] = ellipsis_var
        self.checkboxes["ellipsis"] = ellipsis_ckbox

        ellipsis_alpha_label = ctk.CTkLabel(master=general_settings_frame, text="Alpha:")
        ellipsis_alpha_label.place(relx=0, rely=0.75)
        ellipsis_alpha_slider = ctk.CTkSlider(master=general_settings_frame, from_=0, to=1, number_of_steps=10)
        ellipsis_alpha_slider.set(p.DEFAULT_FONTSIZE)
        ellipsis_alpha_slider.place(relx=0, rely=0.9, relwidth=0.4)
        ellipsis_alpha_strvar = tk.StringVar()
        ellipsis_alpha_strvar.set(str(ellipsis_alpha_slider.get()))
        ellipsis_alpha_value_label = ctk.CTkLabel(master=general_settings_frame, textvariable=ellipsis_alpha_strvar)
        ellipsis_alpha_value_label.place(relx=0.3, rely=0.75)
        self.vars["ellipsis alpha"] = ellipsis_alpha_strvar
        self.sliders["ellipsis alpha"] = ellipsis_alpha_slider

        label_3D = ctk.CTkLabel(master=general_settings_frame, text="3D rotation settings:")
        label_3D.place(relx=0.5, rely=0.5)
        x_rotation_label = ctk.CTkLabel(master=general_settings_frame, text="x:")
        x_rotation_label.place(relx=0.5, rely=0.65)
        y_rotation_label = ctk.CTkLabel(master=general_settings_frame, text="y:")
        y_rotation_label.place(relx=0.5, rely=0.77)
        z_rotation_label = ctk.CTkLabel(master=general_settings_frame, text="z:")
        z_rotation_label.place(relx=0.5, rely=0.89)

        x_rot_slider = ctk.CTkSlider(master=general_settings_frame, from_=-180, to=180, number_of_steps=36)
        x_rot_slider.set(0)
        x_rot_slider.place(relx=0.55, rely=0.65, relwidth=0.35)
        x_rot_strvar = tk.StringVar()
        x_rot_strvar.set(str(x_rot_slider.get()))
        x_rot_value_label = ctk.CTkLabel(master=general_settings_frame, textvariable=x_rot_strvar)
        x_rot_value_label.place(relx=0.95, rely=0.65)
        self.sliders["3D x rotation"] = x_rot_slider
        self.vars["3D x rotation"] = x_rot_strvar

        y_rot_slider = ctk.CTkSlider(master=general_settings_frame, from_=-180, to=180, number_of_steps=36)
        y_rot_slider.set(0)
        y_rot_slider.place(relx=0.55, rely=0.77, relwidth=0.35)
        y_rot_strvar = tk.StringVar()
        y_rot_strvar.set(str(y_rot_slider.get()))
        y_rot_value_label = ctk.CTkLabel(master=general_settings_frame, textvariable=y_rot_strvar)
        y_rot_value_label.place(relx=0.95, rely=0.77)
        self.sliders["3D y rotation"] = y_rot_slider
        self.vars["3D y rotation"] = y_rot_strvar

        z_rot_slider = ctk.CTkSlider(master=general_settings_frame, from_=-180, to=180, number_of_steps=36)
        z_rot_slider.set(0)
        z_rot_slider.place(relx=0.55, rely=0.89, relwidth=0.35)
        z_rot_strvar = tk.StringVar()
        z_rot_strvar.set(str(z_rot_slider.get()))
        z_rot_value_label = ctk.CTkLabel(master=general_settings_frame, textvariable=z_rot_strvar)
        z_rot_value_label.place(relx=0.95, rely=0.89)
        self.sliders["3D z rotation"] = z_rot_slider
        self.vars["3D z rotation"] = z_rot_strvar
        
        
        # ----- Y DATA
        n_labels = self.controller.model.n_labels
        labels_subframe = ctk.CTkFrame(master=pca_frame, height=250)
        labels_subframe.grid(row=0, column=0, sticky=ctk.NSEW)
        self.labels_subframes[f"{n_labels}"] = labels_subframe

        labels_label = ctk.CTkLabel(master=labels_subframe, text="Label:")
        labels_label.place(relx=0, rely=0)
        labels_cbbox = tk.ttk.Combobox(master=labels_subframe, values=[f"None", ], state='readonly')
        labels_cbbox.set("None")
        labels_cbbox.place(relx=0, rely=0.12)
        self.cbboxes[f"label data {n_labels}"] = labels_cbbox

        add_labels_button = ctk.CTkButton(master=labels_subframe, text="+", width=25, height=25, state='normal')
        add_labels_button.place(anchor=tk.NE, relx=0.25, rely=0)
        self.buttons[f"add label data {n_labels}"] = add_labels_button

        fit_var = tk.IntVar()
        fit_var.set(1)
        apply_var = tk.IntVar()
        apply_var.set(1)
        fit_ckbox = ctk.CTkCheckBox(master=labels_subframe, text="Fit", variable=fit_var)
        fit_ckbox.place(relx=0.65, rely=0)
        apply_ckbox = ctk.CTkCheckBox(master=labels_subframe, text="Apply", variable=apply_var)
        apply_ckbox.place(relx=0.75, rely=0)
        self.checkboxes[f"fit {n_labels}"] = fit_ckbox
        self.checkboxes[f"apply {n_labels}"] = apply_ckbox
        self.vars[f"fit {n_labels}"] = fit_var
        self.vars[f"apply {n_labels}"] = apply_var

        labels_legend_label = ctk.CTkLabel(master=labels_subframe, text="Legend label:")
        labels_legend_label.place(relx=0, rely=0.25)
        labels_legend_entry = ctk.CTkEntry(master=labels_subframe)
        labels_legend_entry.place(relx=0, rely=0.37, relwidth=0.4)
        self.entries[f"label data legend {n_labels}"] = labels_legend_entry

        markerstyle_label = ctk.CTkLabel(master=labels_subframe, text="Markers:")
        markerstyle_label.place(relx=0, rely=0.5)
        markerstyle_cbbox = tk.ttk.Combobox(master=labels_subframe, values=list(sorted(p.MARKERS.keys())), state='readonly')
        markerstyle_cbbox.set("point")
        markerstyle_cbbox.place(relx=0, rely=0.62, relwidth=0.25)
        self.cbboxes[f"marker {n_labels}"] = markerstyle_cbbox

        markersize_label = ctk.CTkLabel(master=labels_subframe, text="Marker size:")
        markersize_label.place(relx=0.3, rely=0.5)
        markersize_strvar = tk.StringVar()
        markersize_strvar.set("1")
        markersize_entry = ctk.CTkEntry(master=labels_subframe, textvariable=markersize_strvar)
        markersize_entry.place(relx=0.3, rely=0.62, relwidth=0.2)
        self.entries[f"marker size {n_labels}"] = markersize_entry
        self.vars[f"marker size {n_labels}"] = markersize_strvar

        color_label = ctk.CTkLabel(master=labels_subframe, text="Color:")
        color_label.place(relx=0.6, rely=0.5)
        color_var = tk.StringVar()
        color_var.set("green")
        color_button = ctk.CTkButton(master=labels_subframe, textvariable=color_var,
                                     fg_color=color_var.get(), text_color='black')
        color_button.place(relx=0.6, rely=0.62)
        self.buttons[f"color {n_labels}"] = color_button
        self.vars[f"color {n_labels}"] = color_var

        alpha_label = ctk.CTkLabel(master=labels_subframe, text="Alpha:")
        alpha_label.place(relx=0.5, rely=0.25)
        alpha_slider = ctk.CTkSlider(master=labels_subframe, from_=0, to=1, number_of_steps=10)
        alpha_slider.set(p.DEFAULT_LINEALPHA)
        alpha_slider.place(relx=0.5, rely=0.37, relwidth=0.4)
        alpha_strvar = tk.StringVar()
        alpha_strvar.set(str(alpha_slider.get()))
        alpha_value_label = ctk.CTkLabel(master=labels_subframe, textvariable=alpha_strvar)
        alpha_value_label.place(relx=0.7, rely=0.25)
        self.vars[f"alpha {n_labels}"] = alpha_strvar
        self.sliders[f"alpha {n_labels}"] = alpha_slider

        # ----- AXES
        axes_label = ctk.CTkLabel(master=axes_frame, text="AXES")
        axes_label.place(relx=0, rely=0)

        x_label = ctk.CTkLabel(master=axes_frame, text="x-axis label:")
        x_label.place(relx=0, rely=0.1)
        x_label_entry = ctk.CTkEntry(master=axes_frame, )
        x_label_entry.place(relx=0, rely=0.2, relwidth=0.4)
        self.entries["x label"] = x_label_entry

        y_label = ctk.CTkLabel(master=axes_frame, text="y-axis label:")
        y_label.place(relx=0.5, rely=0.1)
        y_label_entry = ctk.CTkEntry(master=axes_frame, )
        y_label_entry.place(relx=0.5, rely=0.2, relwidth=0.4)
        self.entries["y label"] = y_label_entry

        axes_font_label = ctk.CTkLabel(master=axes_frame, text="Axes / Title font:")
        axes_font_label.place(relx=0, rely=0.4)
        axes_font_cbbox = tk.ttk.Combobox(master=axes_frame, values=p.FONTS, state='readonly')
        axes_font_cbbox.set(p.DEFAULT_FONT)
        axes_font_cbbox.place(relx=0, rely=0.5, relwidth=0.4)
        self.cbboxes["axes font"] = axes_font_cbbox

        title_label = ctk.CTkLabel(master=axes_frame, text="Title:")
        title_label.place(relx=0.5, rely=0.4)
        title_entry = ctk.CTkEntry(master=axes_frame)
        title_entry.place(relx=0.5, rely=0.5, relwidth=0.4)
        self.entries["title"] = title_entry

        x_size_label = ctk.CTkLabel(master=axes_frame, text="x-axis label size:")
        x_size_label.place(relx=0, rely=0.7)
        x_label_slider = ctk.CTkSlider(master=axes_frame, from_=8, to=32, number_of_steps=24)
        x_label_slider.set(p.DEFAULT_FONTSIZE)
        x_label_slider.place(relx=0, rely=0.85, relwidth=0.4)
        x_label_strvar = tk.StringVar()
        x_label_strvar.set(str(x_label_slider.get()))
        x_label_value_label = ctk.CTkLabel(master=axes_frame, textvariable=x_label_strvar)
        x_label_value_label.place(relx=0.3, rely=0.7)
        self.vars["x label size"] = x_label_strvar
        self.sliders["x label size"] = x_label_slider

        y_size_label = ctk.CTkLabel(master=axes_frame, text="y-axis label size:")
        y_size_label.place(relx=0.5, rely=0.7)
        y_label_slider = ctk.CTkSlider(master=axes_frame, from_=8, to=32, number_of_steps=24)
        y_label_slider.set(p.DEFAULT_FONTSIZE)
        y_label_slider.place(relx=0.5, rely=0.85, relwidth=0.4)
        y_label_strvar = tk.StringVar()
        y_label_strvar.set(str(y_label_slider.get()))
        y_label_value_label = ctk.CTkLabel(master=axes_frame, textvariable=y_label_strvar)
        y_label_value_label.place(relx=0.8, rely=0.7)
        self.vars["y label size"] = y_label_strvar
        self.sliders["y label size"] = y_label_slider

        # -----TICKS
        ticks_label = ctk.CTkLabel(master=ticks_frame, text="TICKS")
        ticks_label.place(relx=0, rely=0)

        n_xticks_label = ctk.CTkLabel(master=ticks_frame, text="Number of x ticks:")
        n_xticks_label.place(relx=0, rely=0.1)
        n_xticks_strvar = tk.StringVar()
        n_xticks_strvar.set(p.DEFAULT_NTICKS)
        n_xticks_entry = ctk.CTkEntry(master=ticks_frame, textvariable=n_xticks_strvar)
        n_xticks_entry.place(relx=0, rely=0.2, relwidth=0.2)
        self.entries["n x ticks"] = n_xticks_entry
        self.vars["n x ticks"] = n_xticks_strvar

        n_yticks_label = ctk.CTkLabel(master=ticks_frame, text="Number of y ticks:")
        n_yticks_label.place(relx=0.5, rely=0.1)
        n_yticks_strvar = tk.StringVar()
        n_yticks_strvar.set(p.DEFAULT_NTICKS)
        n_yticks_entry = ctk.CTkEntry(master=ticks_frame, textvariable=n_yticks_strvar)
        n_yticks_entry.place(relx=0.5, rely=0.2, relwidth=0.2)
        self.entries["n y ticks"] = n_yticks_entry
        self.vars["n y ticks"] = n_yticks_strvar

        x_ticks_rotation_label = ctk.CTkLabel(master=ticks_frame, text="x-axis tick rotation:")
        x_ticks_rotation_label.place(relx=0, rely=0.3)
        x_ticks_rotation_slider = ctk.CTkSlider(master=ticks_frame, from_=-180, to=180, number_of_steps=36)
        x_ticks_rotation_slider.set(p.DEFAULT_FONTROTATION)
        x_ticks_rotation_slider.place(relx=0, rely=0.4, relwidth=0.4)
        x_ticks_rotation_strvar = tk.StringVar()
        x_ticks_rotation_strvar.set(str(x_ticks_rotation_slider.get()))
        x_ticks_rotation_value_label = ctk.CTkLabel(master=ticks_frame, textvariable=x_ticks_rotation_strvar)
        x_ticks_rotation_value_label.place(relx=0.3, rely=0.3)
        self.vars["x ticks rotation"] = x_ticks_rotation_strvar
        self.sliders["x ticks rotation"] = x_ticks_rotation_slider

        y_ticks_rotation_label = ctk.CTkLabel(master=ticks_frame, text="y-axis tick rotation:")
        y_ticks_rotation_label.place(relx=0.5, rely=0.3)
        y_ticks_rotation_slider = ctk.CTkSlider(master=ticks_frame, from_=-180, to=180, number_of_steps=36)
        y_ticks_rotation_slider.set(p.DEFAULT_FONTROTATION)
        y_ticks_rotation_slider.place(relx=0.5, rely=0.4, relwidth=0.4)
        y_ticks_rotation_strvar = tk.StringVar()
        y_ticks_rotation_strvar.set(str(y_ticks_rotation_slider.get()))
        y_ticks_rotation_value_label = ctk.CTkLabel(master=ticks_frame, textvariable=y_ticks_rotation_strvar)
        y_ticks_rotation_value_label.place(relx=0.8, rely=0.3)
        self.vars["y ticks rotation"] = y_ticks_rotation_strvar
        self.sliders["y ticks rotation"] = y_ticks_rotation_slider

        x_ticks_label = ctk.CTkLabel(master=ticks_frame, text="x-axis tick size:")
        x_ticks_label.place(relx=0, rely=0.6)
        x_ticks_slider = ctk.CTkSlider(master=ticks_frame, from_=8, to=32, number_of_steps=24)
        x_ticks_slider.set(p.DEFAULT_FONTSIZE)
        x_ticks_slider.place(relx=0, rely=0.7, relwidth=0.4)
        x_ticks_strvar = tk.StringVar()
        x_ticks_strvar.set(str(x_ticks_slider.get()))
        x_ticks_value_label = ctk.CTkLabel(master=ticks_frame, textvariable=x_ticks_strvar)
        x_ticks_value_label.place(relx=0.3, rely=0.6)
        self.vars["x ticks size"] = x_ticks_strvar
        self.sliders["x ticks size"] = x_ticks_slider

        y_ticks_label = ctk.CTkLabel(master=ticks_frame, text="y-axis tick size:")
        y_ticks_label.place(relx=0.5, rely=0.6)
        y_ticks_slider = ctk.CTkSlider(master=ticks_frame, from_=8, to=32, number_of_steps=24)
        y_ticks_slider.set(p.DEFAULT_FONTSIZE)
        y_ticks_slider.place(relx=0.5, rely=0.7, relwidth=0.4)
        y_ticks_strvar = tk.StringVar()
        y_ticks_strvar.set(str(y_ticks_slider.get()))
        y_ticks_value_label = ctk.CTkLabel(master=ticks_frame, textvariable=y_ticks_strvar)
        y_ticks_value_label.place(relx=0.8, rely=0.6)
        self.vars["y ticks size"] = y_ticks_strvar
        self.sliders["y ticks size"] = y_ticks_slider

        round_xticks_label = ctk.CTkLabel(master=ticks_frame, text="Round x ticks:")
        round_xticks_label.place(relx=0, rely=0.8)
        round_xticks_strvar = tk.StringVar()
        round_xticks_strvar.set(p.DEFAULT_ROUND)
        round_xticks_entry = ctk.CTkEntry(master=ticks_frame, textvariable=round_xticks_strvar)
        round_xticks_entry.place(relx=0, rely=0.9, relwidth=0.2)
        self.entries["round x ticks"] = round_xticks_entry
        self.vars["round x ticks"] = round_xticks_strvar

        round_yticks_label = ctk.CTkLabel(master=ticks_frame, text="Round y ticks:")
        round_yticks_label.place(relx=0.5, rely=0.8)
        round_yticks_strvar = tk.StringVar()
        round_yticks_strvar.set(p.DEFAULT_ROUND)
        round_yticks_entry = ctk.CTkEntry(master=ticks_frame, textvariable=round_yticks_strvar)
        round_yticks_entry.place(relx=0.5, rely=0.9, relwidth=0.2)
        self.entries["round y ticks"] = round_yticks_entry
        self.vars["round y ticks"] = round_yticks_strvar

        # ---- LEGEND
        legend_label = ctk.CTkLabel(master=legend_frame, text="LEGEND")
        legend_label.place(relx=0, rely=0)

        show_legend_switch = ctk.CTkSwitch(master=legend_frame, text="Show legend")
        show_legend_switch.place(relx=0, rely=0.2)
        self.switches["show legend"] = show_legend_switch

        legend_anchor_label = ctk.CTkLabel(master=legend_frame, text="Anchor:")
        legend_anchor_label.place(relx=0, rely=0.35)
        legend_anchor_cbbox = tk.ttk.Combobox(master=legend_frame, values=p.LEGEND_POS, state='readonly')
        legend_anchor_cbbox.set("best")
        legend_anchor_cbbox.place(relx=0, rely=0.5)
        self.cbboxes["legend anchor"] = legend_anchor_cbbox

        legend_alpha_label = ctk.CTkLabel(master=legend_frame, text="Alpha:")
        legend_alpha_label.place(relx=0.5, rely=0.35)
        legend_alpha_slider = ctk.CTkSlider(master=legend_frame, from_=0, to=1, number_of_steps=10)
        legend_alpha_slider.set(p.DEFAULT_LINEALPHA)
        legend_alpha_slider.place(relx=0.5, rely=0.5, relwidth=0.4)
        legend_alpha_strvar = tk.StringVar()
        legend_alpha_strvar.set(str(legend_alpha_slider.get()))
        legend_alpha_value_label = ctk.CTkLabel(master=legend_frame, textvariable=legend_alpha_strvar)
        legend_alpha_value_label.place(relx=0.7, rely=0.35)
        self.vars["legend alpha"] = legend_alpha_strvar
        self.sliders["legend alpha"] = legend_alpha_slider

        legend_xpos_label = ctk.CTkLabel(master=legend_frame, text="X position:")
        legend_xpos_label.place(relx=0, rely=0.7)
        legend_xpos_slider = ctk.CTkSlider(master=legend_frame, from_=0, to=1, number_of_steps=10)
        legend_xpos_slider.set(0)
        legend_xpos_slider.place(relx=0, rely=0.9, relwidth=0.4)
        legend_xpos_strvar = tk.StringVar()
        legend_xpos_strvar.set(str(legend_xpos_slider.get()))
        legend_xpos_value_label = ctk.CTkLabel(master=legend_frame, textvariable=legend_xpos_strvar)
        legend_xpos_value_label.place(relx=0.3, rely=0.7)
        self.vars["legend x pos"] = legend_xpos_strvar
        self.sliders["legend x pos"] = legend_xpos_slider

        legend_ypos_label = ctk.CTkLabel(master=legend_frame, text="Y position:")
        legend_ypos_label.place(relx=0.5, rely=0.7)
        legend_ypos_slider = ctk.CTkSlider(master=legend_frame, from_=0, to=1, number_of_steps=10)
        legend_ypos_slider.set(0)
        legend_ypos_slider.place(relx=0.5, rely=0.9, relwidth=0.4)
        legend_ypos_strvar = tk.StringVar()
        legend_ypos_strvar.set(str(legend_ypos_slider.get()))
        legend_ypos_value_label = ctk.CTkLabel(master=legend_frame, textvariable=legend_ypos_strvar)
        legend_ypos_value_label.place(relx=0.8, rely=0.7)
        self.vars["legend y pos"] = legend_ypos_strvar
        self.sliders["legend y pos"] = legend_ypos_slider

        # --------------- PLOT
        fig, ax = self.dummy_figure()
        self.figures["pca"] = (fig, ax)
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.get_tk_widget().place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.96)
        self.canvas["pca"] = canvas

        # --------------- EXEC

        save_figure_button = ctk.CTkButton(master=exec_frame, text="Save figure", fg_color="green")
        save_figure_button.place(anchor=tk.CENTER, relx=0.5, rely=0.66)
        self.buttons["save fig"] = save_figure_button
        load_config_button = ctk.CTkButton(master=exec_frame, text="Load config", fg_color="lightslategray")
        load_config_button.place(anchor=tk.CENTER, relx=0.25, rely=0.33)
        self.buttons["load config"] = load_config_button
        save_config_button = ctk.CTkButton(master=exec_frame, text="Save config", fg_color="lightslategray")
        save_config_button.place(anchor=tk.CENTER, relx=0.25, rely=0.66)
        self.buttons["save config"] = save_config_button
        draw_button = ctk.CTkButton(master=exec_frame, text="Draw", fg_color="green")
        draw_button.place(anchor=tk.CENTER, relx=0.75, rely=0.5, relheight=0.5)
        self.buttons["draw"] = draw_button

        # ---------------- CONFIGURE
        add_labels_button.configure(command=partial(self.add_label_data, pca_frame))
        load_dataset_button.configure(command=self.load_plot_dataset)
        color_button.configure(command=partial(self.select_color, view=self, selection_button_name=f'color {n_labels}'))
        save_config_button.configure(command=self.save_config)
        load_config_button.configure(command=self.load_config)

        for key, slider in self.sliders.items():
            slider.configure(command=partial(self.update_slider_value, var=self.vars[key]))

        save_figure_button.configure(command=partial(self.save_figure, self.figures["pca"][0]))

        draw_button.configure(command=self.draw_figure)

    def set_label_data_columns(self):
        pass
    def add_label_data(self, scrollable_frame):
        if self.controller:
            self.controller.add_label_data(scrollable_frame)

    def remove_label_data(self, frame_key):
        if self.controller:
            self.controller.remove_label_data(frame_key)

    def update_slider_value(self, value, var):
        self.parent_view.parent_view.update_slider_value(value, var)

    def select_color(self, view, selection_button_name):
        self.parent_view.parent_view.select_color(view=view, selection_button_name=selection_button_name)

    def load_plot_dataset(self):
        if self.controller:
            self.controller.load_plot_dataset()

    def dummy_figure(self):
        if self.controller:
            return self.controller.dummy_figure()

    def draw_figure(self, ):
        if self.controller:
            self.controller.draw_figure()

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
