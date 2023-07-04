import tkinter as tk
from functools import partial
from tkinter import ttk

import customtkinter as ctk
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
        self.switches = {}
        self.sliders = {}
        self.checkboxes = {}
        self.textboxes = {}
        self.canvas = {}
        self.figures = {}

        self.manage_plot_tab()

    def set_controller(self, controller):
        self.controller = controller

    def manage_plot_tab(self):
        # ---------------- FRAMES
        init_frame = ctk.CTkFrame(master=self.master)
        init_frame.place(relx=0, rely=0, relheight=0.1, relwidth=0.31)

        curves_frame = ctk.CTkFrame(master=self.master)
        curves_frame.place(relx=0, rely=0.13, relheight=0.87, relwidth=0.31)
        title_frame = ctk.CTkFrame(master=curves_frame)
        title_frame.place(relx=0.01, rely=0.01, relwidth=0.98, relheight=0.18)
        xdata_frame = ctk.CTkFrame(master=curves_frame)
        xdata_frame.place(relx=0.01, rely=0.2, relwidth=0.98, relheight=0.14)
        ydata_frame = ctk.CTkScrollableFrame(master=curves_frame)
        ydata_frame.place(relx=0.01, rely=0.35, relwidth=0.98, relheight=0.64)
        ydata_frame.grid_columnconfigure(0, weight=1)

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
        load_dataset_button = ctk.CTkButton(master=init_frame, text="Load dataset:")
        load_dataset_button.place(relx=0.0, rely=0)
        self.buttons["plt load dataset"] = load_dataset_button

        load_dataset_strvar = tk.StringVar()
        load_dataset_entry = ctk.CTkEntry(master=init_frame, state='disabled', textvariable=load_dataset_strvar)
        load_dataset_entry.place(relx=0, rely=0.5, relwidth=0.5)
        self.vars["plt load dataset"] = load_dataset_strvar
        self.entries["plt load dataset"] = load_dataset_entry

        # ----- TITLE
        title_label = ctk.CTkLabel(master=title_frame, text="Title:")
        title_label.place(relx=0, rely=0)
        title_entry = ctk.CTkEntry(master=title_frame)
        title_entry.place(relx=0, rely=0.2, relwidth=0.4)
        self.entries["plt title"] = title_entry

        title_font_label = ctk.CTkLabel(master=title_frame, text="Title font:")
        title_font_label.place(relx=0.5, rely=0)
        title_font_cbbox = tk.ttk.Combobox(master=title_frame, values=p.FONTS, state='readonly')
        title_font_cbbox.set(p.DEFAULT_FONT)
        title_font_cbbox.place(relx=0.5, rely=0.2, relwidth=0.4)
        self.cbboxes["plt title font"] = title_font_cbbox

        title_size_label = ctk.CTkLabel(master=title_frame, text="Title size:")
        title_size_label.place(relx=0, rely=0.5)
        title_size_slider = ctk.CTkSlider(master=title_frame, from_=8, to=32, number_of_steps=24)
        title_size_slider.set(p.DEFAULT_FONTSIZE)
        title_size_slider.place(relx=0, rely=0.8, relwidth=0.4)
        title_size_strvar = tk.StringVar()
        title_size_strvar.set(str(title_size_slider.get()))
        title_size_value_label = ctk.CTkLabel(master=title_frame, textvariable=title_size_strvar)
        title_size_value_label.place(relx=0.3, rely=0.5)
        self.vars["plt title size"] = title_size_strvar
        self.sliders["plt title size"] = title_size_slider

        dpi_label = ctk.CTkLabel(master=title_frame, text="Figure dpi:")
        dpi_label.place(relx=0.5, rely=0.5)
        dpi_strvar = tk.StringVar()
        dpi_strvar.set("100")
        dpi_entry = ctk.CTkEntry(master=title_frame, textvariable=dpi_strvar)
        dpi_entry.place(relx=0.5, rely=0.8, relwidth=0.2)
        self.entries["plt dpi"] = dpi_entry
        self.vars["plt dpi"] = dpi_strvar

        # ----- X DATA
        xdata_label = ctk.CTkLabel(master=xdata_frame, text="X-data column:")
        xdata_label.place(relx=0, rely=0)
        xdata_cbbox = tk.ttk.Combobox(master=xdata_frame, values=["None", ], state='readonly')
        xdata_cbbox.set("None")
        xdata_cbbox.place(relx=0.5, rely=0)
        self.cbboxes["plt xdata"] = xdata_cbbox

        # ----- Y DATA
        ydata_subframe = ctk.CTkFrame(master=ydata_frame, height=250)
        ydata_subframe.grid(row=0, column=0, sticky=ctk.NSEW)

        ydata_label = ctk.CTkLabel(master=ydata_subframe, text="Y-data column:")
        ydata_label.place(relx=0, rely=0)
        ydata_cbbox = tk.ttk.Combobox(master=ydata_subframe, values=["None", ], state='readonly')
        ydata_cbbox.set("None")
        ydata_cbbox.place(relx=0, rely=0.15)
        self.cbboxes["plt ydata 0"] = ydata_cbbox

        add_ydata_button = ctk.CTkButton(master=ydata_subframe, text="+", width=25, height=25, state='normal')
        add_ydata_button.place(anchor=tk.NE, relx=0.25, rely=0)
        subtract_ydata_button = ctk.CTkButton(master=ydata_subframe, text="-", width=25, height=25, state='normal')
        subtract_ydata_button.place(anchor=tk.NE, relx=0.38, rely=0)
        self.buttons["plt add ydata 0"] = add_ydata_button
        self.buttons["plt subtract ydata 0"] = subtract_ydata_button

        ydata_legend_label = ctk.CTkLabel(master=ydata_subframe, text="Legend label:")
        ydata_legend_label.place(relx=0.5, rely=0)
        ydata_legend_entry = ctk.CTkEntry(master=ydata_subframe)
        ydata_legend_entry.place(relx=0.5, rely=0.15, relwidth=0.4)
        self.entries["plt ydata legend 0"] = ydata_legend_entry

        linestyle_label = ctk.CTkLabel(master=ydata_subframe, text="Linestyle:")
        linestyle_label.place(relx=0, rely=0.3)
        linestyle_cbbox = tk.ttk.Combobox(master=ydata_subframe, values=list(p.LINESTYLES.keys()), state='readonly')
        linestyle_cbbox.set("solid")
        linestyle_cbbox.place(relx=0, rely=0.5, relwidth=0.35)
        self.cbboxes["plt linestyle 0"] = linestyle_cbbox

        linewidth_label = ctk.CTkLabel(master=ydata_subframe, text="Linewidth:")
        linewidth_label.place(relx=0.5, rely=0.3)
        linewidth_strvar = tk.StringVar()
        linewidth_strvar.set("1")
        linewidth_entry = ctk.CTkEntry(master=ydata_subframe, textvariable=linewidth_strvar)
        linewidth_entry.place(relx=0.5, rely=0.45, relwidth=0.2)
        self.entries["plt linewidth 0"] = linewidth_entry
        self.vars["plt linewidth 0"] = linewidth_strvar

        color_label = ctk.CTkLabel(master=ydata_subframe, text="Color:")
        color_label.place(relx=0, rely=0.65)
        color_var = tk.StringVar()
        color_var.set("green")
        color_button = ctk.CTkButton(master=ydata_subframe, textvariable=color_var,
                                     fg_color=color_var.get(), text_color='black')
        color_button.place(relx=0, rely=0.75)
        self.buttons["plt color 0"] = color_button
        self.vars["plt color 0"] = color_var

        alpha_label = ctk.CTkLabel(master=ydata_subframe, text="Alpha:")
        alpha_label.place(relx=0.5, rely=0.65)
        alpha_slider = ctk.CTkSlider(master=ydata_subframe, from_=0, to=1, number_of_steps=10)
        alpha_slider.set(p.DEFAULT_LINEALPHA)
        alpha_slider.place(relx=0.5, rely=0.8, relwidth=0.4)
        alpha_strvar = tk.StringVar()
        alpha_strvar.set(str(alpha_slider.get()))
        alpha_value_label = ctk.CTkLabel(master=ydata_subframe, textvariable=alpha_strvar)
        alpha_value_label.place(relx=0.7, rely=0.65)
        self.vars["plt alpha 0"] = alpha_strvar
        self.sliders["plt alpha 0"] = alpha_slider

        # ----- AXES
        axes_label = ctk.CTkLabel(master=axes_frame, text="AXES")
        axes_label.place(relx=0, rely=0)

        x_label = ctk.CTkLabel(master=axes_frame, text="x-axis label:")
        x_label.place(relx=0, rely=0.1)
        x_label_entry = ctk.CTkEntry(master=axes_frame, )
        x_label_entry.place(relx=0, rely=0.2, relwidth=0.4)
        self.entries["plt x label"] = x_label_entry

        y_label = ctk.CTkLabel(master=axes_frame, text="y-axis label:")
        y_label.place(relx=0.5, rely=0.1)
        y_label_entry = ctk.CTkEntry(master=axes_frame, )
        y_label_entry.place(relx=0.5, rely=0.2, relwidth=0.4)
        self.entries["plt y label"] = y_label_entry

        axes_font_label = ctk.CTkLabel(master=axes_frame, text="Axes font:")
        axes_font_label.place(relx=0, rely=0.4)
        axes_font_cbbox = tk.ttk.Combobox(master=axes_frame, values=p.FONTS, state='readonly')
        axes_font_cbbox.set(p.DEFAULT_FONT)
        axes_font_cbbox.place(relx=0, rely=0.5, relwidth=0.4)
        self.cbboxes["plt axes font"] = axes_font_cbbox

        x_size_label = ctk.CTkLabel(master=axes_frame, text="x-axis label size:")
        x_size_label.place(relx=0, rely=0.7)
        x_label_slider = ctk.CTkSlider(master=axes_frame, from_=8, to=32, number_of_steps=24)
        x_label_slider.set(p.DEFAULT_FONTSIZE)
        x_label_slider.place(relx=0, rely=0.85, relwidth=0.4)
        x_label_strvar = tk.StringVar()
        x_label_strvar.set(str(x_label_slider.get()))
        x_label_value_label = ctk.CTkLabel(master=axes_frame, textvariable=x_label_strvar)
        x_label_value_label.place(relx=0.3, rely=0.7)
        self.vars["plt x label size"] = x_label_strvar
        self.sliders["plt x label size"] = x_label_slider

        y_size_label = ctk.CTkLabel(master=axes_frame, text="y-axis label size:")
        y_size_label.place(relx=0.5, rely=0.7)
        y_label_slider = ctk.CTkSlider(master=axes_frame, from_=8, to=32, number_of_steps=24)
        y_label_slider.set(p.DEFAULT_FONTSIZE)
        y_label_slider.place(relx=0.5, rely=0.85, relwidth=0.4)
        y_label_strvar = tk.StringVar()
        y_label_strvar.set(str(y_label_slider.get()))
        y_label_value_label = ctk.CTkLabel(master=axes_frame, textvariable=y_label_strvar)
        y_label_value_label.place(relx=0.8, rely=0.7)
        self.vars["plt y label size"] = y_label_strvar
        self.sliders["plt y label size"] = y_label_slider

        # -----TICKS
        ticks_label = ctk.CTkLabel(master=ticks_frame, text="TICKS")
        ticks_label.place(relx=0, rely=0)

        n_xticks_label = ctk.CTkLabel(master=ticks_frame, text="Number of x ticks:")
        n_xticks_label.place(relx=0, rely=0.1)
        n_xticks_strvar = tk.StringVar()
        n_xticks_strvar.set(p.DEFAULT_NTICKS)
        n_xticks_entry = ctk.CTkEntry(master=ticks_frame, textvariable=n_xticks_strvar)
        n_xticks_entry.place(relx=0, rely=0.2, relwidth=0.2)
        self.entries["plt n x ticks"] = n_xticks_entry
        self.vars["plt n x ticks"] = n_xticks_strvar

        n_yticks_label = ctk.CTkLabel(master=ticks_frame, text="Number of y ticks:")
        n_yticks_label.place(relx=0.5, rely=0.1)
        n_yticks_strvar = tk.StringVar()
        n_yticks_strvar.set(p.DEFAULT_NTICKS)
        n_yticks_entry = ctk.CTkEntry(master=ticks_frame, textvariable=n_yticks_strvar)
        n_yticks_entry.place(relx=0.5, rely=0.2, relwidth=0.2)
        self.entries["plt n y ticks"] = n_yticks_entry
        self.vars["plt n y ticks"] = n_yticks_strvar

        x_ticks_rotation_label = ctk.CTkLabel(master=ticks_frame, text="x-axis tick rotation:")
        x_ticks_rotation_label.place(relx=0, rely=0.3)
        x_ticks_rotation_slider = ctk.CTkSlider(master=ticks_frame, from_=-180, to=180, number_of_steps=36)
        x_ticks_rotation_slider.set(p.DEFAULT_FONTROTATION)
        x_ticks_rotation_slider.place(relx=0, rely=0.4, relwidth=0.4)
        x_ticks_rotation_strvar = tk.StringVar()
        x_ticks_rotation_strvar.set(str(x_ticks_rotation_slider.get()))
        x_ticks_rotation_value_label = ctk.CTkLabel(master=ticks_frame, textvariable=x_ticks_rotation_strvar)
        x_ticks_rotation_value_label.place(relx=0.3, rely=0.3)
        self.vars["plt x ticks rotation"] = x_ticks_rotation_strvar
        self.sliders["plt x ticks rotation"] = x_ticks_rotation_slider

        y_ticks_rotation_label = ctk.CTkLabel(master=ticks_frame, text="y-axis tick rotation:")
        y_ticks_rotation_label.place(relx=0.5, rely=0.3)
        y_ticks_rotation_slider = ctk.CTkSlider(master=ticks_frame, from_=-180, to=180, number_of_steps=36)
        y_ticks_rotation_slider.set(p.DEFAULT_FONTROTATION)
        y_ticks_rotation_slider.place(relx=0.5, rely=0.4, relwidth=0.4)
        y_ticks_rotation_strvar = tk.StringVar()
        y_ticks_rotation_strvar.set(str(y_ticks_rotation_slider.get()))
        y_ticks_rotation_value_label = ctk.CTkLabel(master=ticks_frame, textvariable=y_ticks_rotation_strvar)
        y_ticks_rotation_value_label.place(relx=0.8, rely=0.3)
        self.vars["plt y ticks rotation"] = y_ticks_rotation_strvar
        self.sliders["plt y ticks rotation"] = y_ticks_rotation_slider

        x_ticks_label = ctk.CTkLabel(master=ticks_frame, text="x-axis tick size:")
        x_ticks_label.place(relx=0, rely=0.6)
        x_ticks_slider = ctk.CTkSlider(master=ticks_frame, from_=8, to=32, number_of_steps=24)
        x_ticks_slider.set(p.DEFAULT_FONTSIZE)
        x_ticks_slider.place(relx=0, rely=0.7, relwidth=0.4)
        x_ticks_strvar = tk.StringVar()
        x_ticks_strvar.set(str(x_ticks_slider.get()))
        x_ticks_value_label = ctk.CTkLabel(master=ticks_frame, textvariable=x_ticks_strvar)
        x_ticks_value_label.place(relx=0.3, rely=0.6)
        self.vars["plt x ticks size"] = x_ticks_strvar
        self.sliders["plt x ticks size"] = x_ticks_slider

        y_ticks_label = ctk.CTkLabel(master=ticks_frame, text="y-axis tick size:")
        y_ticks_label.place(relx=0.5, rely=0.6)
        y_ticks_slider = ctk.CTkSlider(master=ticks_frame, from_=8, to=32, number_of_steps=24)
        y_ticks_slider.set(p.DEFAULT_FONTSIZE)
        y_ticks_slider.place(relx=0.5, rely=0.7, relwidth=0.4)
        y_ticks_strvar = tk.StringVar()
        y_ticks_strvar.set(str(y_ticks_slider.get()))
        y_ticks_value_label = ctk.CTkLabel(master=ticks_frame, textvariable=y_ticks_strvar)
        y_ticks_value_label.place(relx=0.8, rely=0.6)
        self.vars["plt y ticks size"] = y_ticks_strvar
        self.sliders["plt y ticks size"] = y_ticks_slider

        round_xticks_label = ctk.CTkLabel(master=ticks_frame, text="Round x ticks:")
        round_xticks_label.place(relx=0, rely=0.8)
        round_xticks_strvar = tk.StringVar()
        round_xticks_strvar.set(p.DEFAULT_ROUND)
        round_xticks_entry = ctk.CTkEntry(master=ticks_frame, textvariable=round_xticks_strvar)
        round_xticks_entry.place(relx=0, rely=0.9, relwidth=0.2)
        self.entries["plt round x ticks"] = round_xticks_entry
        self.vars["plt round x ticks"] = round_xticks_strvar

        round_yticks_label = ctk.CTkLabel(master=ticks_frame, text="Round y ticks:")
        round_yticks_label.place(relx=0.5, rely=0.8)
        round_yticks_strvar = tk.StringVar()
        round_yticks_strvar.set(p.DEFAULT_ROUND)
        round_yticks_entry = ctk.CTkEntry(master=ticks_frame, textvariable=round_yticks_strvar)
        round_yticks_entry.place(relx=0.5, rely=0.9, relwidth=0.2)
        self.entries["plt round y ticks"] = round_yticks_entry
        self.vars["plt round y ticks"] = round_yticks_strvar

        # ---- LEGEND
        legend_label = ctk.CTkLabel(master=legend_frame, text="LEGEND")
        legend_label.place(relx=0, rely=0)

        show_legend_switch = ctk.CTkSwitch(master=legend_frame, text="Show legend")
        show_legend_switch.place(relx=0, rely=0.2)
        self.switches["plt show legend"] = show_legend_switch

        legend_anchor_label = ctk.CTkLabel(master=legend_frame, text="Anchor:")
        legend_anchor_label.place(relx=0, rely=0.35)
        legend_anchor_cbbox = tk.ttk.Combobox(master=legend_frame, values=p.LEGEND_POS, state='readonly')
        legend_anchor_cbbox.set("best")
        legend_anchor_cbbox.place(relx=0, rely=0.5)
        self.cbboxes["plt legend anchor"] = legend_anchor_cbbox

        legend_alpha_label = ctk.CTkLabel(master=legend_frame, text="Alpha:")
        legend_alpha_label.place(relx=0.5, rely=0.35)
        legend_alpha_slider = ctk.CTkSlider(master=legend_frame, from_=0, to=1, number_of_steps=10)
        legend_alpha_slider.set(p.DEFAULT_LINEALPHA)
        legend_alpha_slider.place(relx=0.5, rely=0.5, relwidth=0.4)
        legend_alpha_strvar = tk.StringVar()
        legend_alpha_strvar.set(str(legend_alpha_slider.get()))
        legend_alpha_value_label = ctk.CTkLabel(master=legend_frame, textvariable=legend_alpha_strvar)
        legend_alpha_value_label.place(relx=0.7, rely=0.35)
        self.vars["plt legend alpha"] = legend_alpha_strvar
        self.sliders["plt legend alpha"] = legend_alpha_slider

        legend_xpos_label = ctk.CTkLabel(master=legend_frame, text="X position:")
        legend_xpos_label.place(relx=0, rely=0.7)
        legend_xpos_slider = ctk.CTkSlider(master=legend_frame, from_=0, to=1, number_of_steps=10)
        legend_xpos_slider.set(0)
        legend_xpos_slider.place(relx=0, rely=0.9, relwidth=0.4)
        legend_xpos_strvar = tk.StringVar()
        legend_xpos_strvar.set(str(legend_xpos_slider.get()))
        legend_xpos_value_label = ctk.CTkLabel(master=legend_frame, textvariable=legend_xpos_strvar)
        legend_xpos_value_label.place(relx=0.3, rely=0.7)
        self.vars["plt legend x pos 0"] = legend_xpos_strvar
        self.sliders["plt legend x pos 0"] = legend_xpos_slider

        legend_ypos_label = ctk.CTkLabel(master=legend_frame, text="Y position:")
        legend_ypos_label.place(relx=0.5, rely=0.7)
        legend_ypos_slider = ctk.CTkSlider(master=legend_frame, from_=0, to=1, number_of_steps=10)
        legend_ypos_slider.set(0)
        legend_ypos_slider.place(relx=0.5, rely=0.9, relwidth=0.4)
        legend_ypos_strvar = tk.StringVar()
        legend_ypos_strvar.set(str(legend_ypos_slider.get()))
        legend_ypos_value_label = ctk.CTkLabel(master=legend_frame, textvariable=legend_ypos_strvar)
        legend_ypos_value_label.place(relx=0.8, rely=0.7)
        self.vars["plt legend y pos 0"] = legend_ypos_strvar
        self.sliders["plt legend y pos 0"] = legend_ypos_slider

        # --------------- PLOT
        fig, ax = self.dummy_figure()
        self.figures["plot"] = (fig, ax)
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.get_tk_widget().place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.96)
        self.canvas["plot"] = canvas

        # --------------- EXEC
        export_button = ctk.CTkButton(master=exec_frame, text="Export data", fg_color="green")
        export_button.place(anchor=tk.CENTER, relx=0.5, rely=0.33)
        self.buttons["plt export"] = export_button
        save_figure_button = ctk.CTkButton(master=exec_frame, text="Save figure", fg_color="green")
        save_figure_button.place(anchor=tk.CENTER, relx=0.5, rely=0.66)
        self.buttons["plt save fig"] = save_figure_button
        load_config_button = ctk.CTkButton(master=exec_frame, text="Load config", fg_color="lightslategray")
        load_config_button.place(anchor=tk.CENTER, relx=0.25, rely=0.33)
        self.buttons["plt load config"] = load_config_button
        save_config_button = ctk.CTkButton(master=exec_frame, text="Save config", fg_color="lightslategray")
        save_config_button.place(anchor=tk.CENTER, relx=0.25, rely=0.66)
        self.buttons["plt save config"] = save_config_button
        draw_button = ctk.CTkButton(master=exec_frame, text="Draw", fg_color="green")
        draw_button.place(anchor=tk.CENTER, relx=0.75, rely=0.5, relheight=0.5)
        self.buttons["plt draw"] = draw_button

        # ---------------- CONFIGURE
        title_size_slider.configure(command=partial(self.update_slider_value, var=title_size_strvar))
        alpha_slider.configure(command=partial(self.update_slider_value, var=alpha_strvar))
        x_label_slider.configure(command=partial(self.update_slider_value, var=x_label_strvar))
        y_label_slider.configure(command=partial(self.update_slider_value, var=y_label_strvar))
        x_ticks_rotation_slider.configure(command=partial(self.update_slider_value, var=x_ticks_rotation_strvar))
        y_ticks_rotation_slider.configure(command=partial(self.update_slider_value, var=y_ticks_rotation_strvar))
        x_ticks_slider.configure(command=partial(self.update_slider_value, var=x_ticks_strvar))
        y_ticks_slider.configure(command=partial(self.update_slider_value, var=y_ticks_strvar))
        legend_alpha_slider.configure(command=partial(self.update_slider_value, var=legend_alpha_strvar))
        legend_xpos_slider.configure(command=partial(self.update_slider_value, var=legend_xpos_strvar))
        legend_ypos_slider.configure(command=partial(self.update_slider_value, var=legend_ypos_strvar))

        load_dataset_button.configure(command=self.load_plot_dataset)
        color_button.configure(command=partial(self.select_color, 'plt color 0'))
        save_config_button.configure(command=self.save_config)
        load_config_button.configure(command=self.load_config)

    def update_slider_value(self, value, var):
        self.parent_view.parent_view.update_slider_value(value, var)

    def select_color(self):
        self.parent_view.parent_view.select_color()

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

    def export_figure_data(self, ax):
        if self.controller:
            self.controller.export_figure_data(ax)

    def save_figure(self, fig):
        if self.controller:
            self.controller.save_figure(fig)
