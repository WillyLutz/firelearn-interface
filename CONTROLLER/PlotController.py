import os
import pickle
import random
from functools import partial

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from CONTROLLER.MainController import MainController
from MODEL.PlotModel import PlotModel
import customtkinter as ctk
from CONTROLLER import input_validation as ival
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import params as p


class PlotController:
    def __init__(self, view, ):
        self.model = PlotModel()
        self.view = view
        self.view.controller = self  # set controller
        self.progress = None

    def input_validation_plot(self):
        plt_entries = {key: value for (key, value) in self.view.entries.items() if "plt" in key}
        # todo : input validation /!\ multiple y
        # if float(plt_entries["linewidth"].get()) < 0:
        #     messagebox.showerror("Value error", "Line width must be positive.")
        #
        # for key, value in {"linewidth": "Line width", "n x ticks": "Number of x ticks",
        #                    "n y ticks": "Number of y ticks", "dpi": "Figure dpi"}.items():
        #     if not ival.is_number(plt_entries["linewidth"].get()):
        #         messagebox.showerror("Value error", f"{value} must be a number.")
        #         return False
        #
        # for key, value in {"round x ticks": "Round x ticks", "round y ticks": "Round y ticks",
        #                    "dpi": "Figure dpi"}.items():
        #     if not ival.isint(plt_entries[key].get()):
        #         messagebox.showerror("Value error", f"{value} must be a positive integer.")
        #         return False
        #
        # for key, value in {"linewidth": "Line width", }.items():
        #     if ival.value_is_empty_or_none(plt_entries[key].get()):
        #         messagebox.showerror("Value error", f"{value} can not be empty or None")
        #         return False
        #
        # if int(self.view.entries["n x ticks"].get()) < 2:
        #     messagebox.showerror("Value error", "Can not have les than 2 ticks.")

        return True

    def save_figure(self, fig):
        filepath = filedialog.asksaveasfilename(title="Open file", filetypes=(("Image", "*.png"),))
        if filepath:
            fig.savefig(filepath, dpi=int(self.model.plot_general_settings["dpi"]))

    def check_params_validity(self):
        if not self.input_validation_plot():
            return False
        return True

    def save_config(self, ):
        if self.check_params_validity():
            f = filedialog.asksaveasfilename(defaultextension=".pltcfg",
                                             filetypes=[("Analysis - Simple plot", "*.pltcfg"), ])
            if f:
                self.model.save_model(path=f, )

    def load_config(self, ):
        f = filedialog.askopenfilename(title="Open file", filetypes=(("Analysis - Simple plot", "*.pltcfg"),))
        if f:
            if self.model.load_model(path=f):
                self.update_view_from_model()
                # todo : does not work because widgets are not created while the top-levels are not created

    def update_view_from_model(self, ):

        for key, value in self.model.plot_data.items():
            self.view.vars[key].set(value)
        for key, value in self.model.plot_legend.items():
            self.view.vars[key].set(value)
        for key, value in self.model.plot_axes.items():
            self.view.vars[key].set(value)
        for key, value in self.model.plot_general_settings.items():
            self.view.vars[key].set(value)


    def load_plot_dataset(self, ):
        filename = filedialog.askopenfilename(title="Open file",
                                              filetypes=(("Tables", "*.txt *.csv"),))
        if filename:
            fig, ax = self.view.figures["plot"]
            ax.clear()
            for n in range(self.model.n_ydata + 1):
                self.remove_ydata()

            df = pd.read_csv(filename)
            self.model.dataset = df
            self.model.dataset_path = filename
            self.view.vars["load dataset"].set(filename)

            columns = list(df.columns)
            self.view.cbboxes["xdata"].configure(values=columns)
            self.view.vars["xdata"].set(columns[0])

            ydata_curves = {key: value for (key, value) in self.view.cbboxes.items() if "ydata " in key}
            for key, value in ydata_curves.items():
                value.configure(values=columns)
                value.set(columns[-1])

    def add_ydata(self, scrollable_frame):
        if self.model.dataset_path:
            df = pd.read_csv(self.model.dataset_path, index_col=False)
            columns = list(df.columns)

            self.model.n_ydata += 1
            n_ydata = self.model.n_ydata

            ydata_subframe = ctk.CTkFrame(master=scrollable_frame, height=250)
            ydata_subframe.grid(row=n_ydata, column=0, sticky=ctk.NSEW, pady=25)
            self.view.ydata_subframes[str(n_ydata)] = ydata_subframe

            ydata_label = ctk.CTkLabel(master=ydata_subframe, text="Y-data column:")
            ydata_cbbox_var = tk.StringVar(value=columns[-1])
            ydata_cbbox = tk.ttk.Combobox(master=ydata_subframe, values=columns, state='readonly',
                                          textvariable=ydata_cbbox_var)
            ydata_cbbox.set(ydata_cbbox_var.get())

            ydata_label.place(relx=0, rely=0)
            ydata_cbbox.place(relx=0, rely=0.15)
            self.view.cbboxes[f"ydata {n_ydata}"] = ydata_cbbox
            self.view.vars[f"ydata {n_ydata}"] = ydata_cbbox_var

            ydata_legend_label = ctk.CTkLabel(master=ydata_subframe, text="Legend label:")
            ydata_legend_var = tk.StringVar()
            ydata_legend_entry = ctk.CTkEntry(master=ydata_subframe, textvariable=ydata_legend_var)

            ydata_legend_label.place(relx=0.5, rely=0)
            ydata_legend_entry.place(relx=0.5, rely=0.15, relwidth=0.4)
            self.view.entries[f"ydata legend {n_ydata}"] = ydata_legend_entry
            self.view.vars[f"ydata legend {n_ydata}"] = ydata_legend_var

            linestyle_label = ctk.CTkLabel(master=ydata_subframe, text="Linestyle:")
            linestyle_var = tk.StringVar(value=p.DEFAULT_LINESTYLE)
            linestyle_cbbox = tk.ttk.Combobox(master=ydata_subframe, values=list(p.LINESTYLES.keys()), state='readonly',
                                              textvariable=linestyle_var)
            linestyle_cbbox.set(linestyle_var.get())

            linestyle_label.place(relx=0, rely=0.3)
            linestyle_cbbox.place(relx=0, rely=0.5, relwidth=0.35)
            self.view.cbboxes[f"linestyle {n_ydata}"] = linestyle_cbbox
            self.view.vars[f"linestyle {n_ydata}"] = linestyle_var

            linewidth_label = ctk.CTkLabel(master=ydata_subframe, text="Linewidth:")
            linewidth_var = tk.StringVar(value=p.DEFAULT_LINEWIDTH)
            linewidth_entry = ctk.CTkEntry(master=ydata_subframe, textvariable=linewidth_var)

            linewidth_label.place(relx=0.5, rely=0.3)
            linewidth_entry.place(relx=0.5, rely=0.45, relwidth=0.2)
            self.view.entries[f"linewidth {n_ydata}"] = linewidth_entry
            self.view.vars[f"linewidth {n_ydata}"] = linewidth_var

            color_label = ctk.CTkLabel(master=ydata_subframe, text="Color:")
            color_var = tk.StringVar(value=p.DEFAULT_COLOR)
            color_button = ctk.CTkButton(master=ydata_subframe, textvariable=color_var,
                                         fg_color=color_var.get(), text_color='black')

            color_label.place(relx=0, rely=0.65)
            color_button.place(relx=0, rely=0.75)
            self.view.buttons[f"color {n_ydata}"] = color_button
            self.view.vars[f"color {n_ydata}"] = color_var

            alpha_label = ctk.CTkLabel(master=ydata_subframe, text="Alpha:")
            alpha_var = tk.DoubleVar(value=p.DEFAULT_ALPHA)
            alpha_slider = ctk.CTkSlider(master=ydata_subframe, from_=0, to=1, number_of_steps=10, variable=alpha_var)
            alpha_value_label = ctk.CTkLabel(master=ydata_subframe, textvariable=alpha_var)

            alpha_label.place(relx=0.5, rely=0.65)
            alpha_slider.place(relx=0.5, rely=0.8, relwidth=0.4)
            alpha_value_label.place(relx=0.7, rely=0.65)
            self.view.vars[f"alpha {n_ydata}"] = alpha_var
            self.view.sliders[f"alpha {n_ydata}"] = alpha_slider

            color_button.configure(command=partial(self.view.select_color, view=self.view,
                                                   selection_button_name=f'color {n_ydata}'))

        else:
            messagebox.showerror("Missing Values", "No dataset loaded")
            return False

    def remove_ydata(self):
        n_ydata = self.model.n_ydata
        if n_ydata >= 0:
            # destroying all widgets related
            for child in self.view.ydata_subframes[str(n_ydata)].winfo_children():
                child.destroy()

            # remove the frame from self.view.ydata_subframes
            self.view.ydata_subframes[str(n_ydata)].destroy()
            del self.view.ydata_subframes[str(n_ydata)]

            # destroying all items related in dicts
            del self.view.entries[f"ydata legend {n_ydata}"]
            del self.view.entries[f"linewidth {n_ydata}"]
            del self.view.buttons[f"color {n_ydata}"]
            del self.view.cbboxes[f"ydata {n_ydata}"]
            del self.view.cbboxes[f"linestyle {n_ydata}"]
            del self.view.vars[f"linewidth {n_ydata}"]
            del self.view.vars[f"color {n_ydata}"]
            del self.view.vars[f"alpha {n_ydata}"]
            del self.view.vars[f"ydata legend {n_ydata}"]
            del self.view.vars[f"linestyle {n_ydata}"]
            del self.view.vars[f"ydata {n_ydata}"]
            del self.view.sliders[f"alpha {n_ydata}"]

            self.view.lines[n_ydata].pop(0).remove()
            del self.view.lines[n_ydata]

            self.view.canvas["plot"].draw()

            self.model.n_ydata -= 1


    def draw_figure(self):
        # todo: if validation
        fig, ax = self.view.figures["plot"]
        if self.model.n_ydata >= 0:
            ax.clear()
            # ----- PLOT
            df = self.model.dataset
            for n_ydata in range(self.model.n_ydata + 1):
                self.view.lines[n_ydata] = ax.plot(df[self.view.vars["xdata"].get()],
                                                   df[self.view.vars[f"ydata {n_ydata}"].get()],
                                                   label=self.view.vars[f"ydata legend {n_ydata}"].get(),
                                                   linestyle=self.view.vars[f"linestyle {n_ydata}"].get(),
                                                   linewidth=self.view.vars[f"linewidth {n_ydata}"].get(),
                                                   color=self.view.vars[f"color {n_ydata}"].get(),
                                                   alpha=self.view.vars[f"alpha {n_ydata}"].get(),
                                                   )

            # ----- TITLE
            ax.set_title(self.model.plot_general_settings["title"],
                         fontdict={"font": self.model.plot_general_settings["title font"],
                                   "fontsize": self.model.plot_general_settings["title size"], })

            # ---- LABELS

            ax.set_xlabel(self.model.plot_axes["x label"],
                          fontdict={"font": self.model.plot_axes["axes font"],
                                    "fontsize": self.model.plot_axes["x label size"]})
            ax.set_ylabel(self.model.plot_axes["y label"],
                          fontdict={"font": self.model.plot_axes["axes font"],
                                    "fontsize": self.model.plot_axes["y label size"]})

            # ---- TICKS

            first_x = ax.lines[0].get_xdata()
            first_y = ax.lines[0].get_ydata()
            xmin = min(first_x)
            xmax = max(first_x)
            ymin = min(first_y)
            ymax = max(first_y)
            for x in range(self.model.n_ydata + 1):
                # handle = plt.gca()
                line = ax.lines[x]
                x_data = line.get_xdata()
                y_data = line.get_ydata()

                if min(x_data) < xmin:
                    xmin = min(x_data)
                if max(x_data) > xmax:
                    xmax = max(x_data)
                if min(y_data) < ymin:
                    ymin = min(y_data)
                if max(y_data) > ymax:
                    ymax = max(y_data)

            if all([self.model.plot_axes["n x ticks"], self.model.plot_axes["round x ticks"],
                    self.model.plot_axes["n y ticks"], self.model.plot_axes["round y ticks"]]):
                n_xticks = int(self.model.plot_axes["n x ticks"])
                xstep = (xmax - xmin) / (n_xticks - 1)
                xtick = xmin
                xticks = []
                for i in range(n_xticks - 1):
                    xticks.append(xtick)
                    xtick += xstep
                xticks.append(xmax)
                rounded_xticks = list(np.around(np.array(xticks), int(self.model.plot_axes["round x ticks"])))
                ax.set_xticks(rounded_xticks)
                ax.tick_params(axis='x',
                               labelsize=self.model.plot_axes["x ticks size"],
                               labelrotation=float(self.model.plot_axes["x ticks rotation"]))

                n_yticks = int(self.model.plot_axes["n y ticks"])
                ystep = (ymax - ymin) / (n_yticks - 1)
                ytick = ymin
                yticks = []
                for i in range(n_yticks - 1):
                    yticks.append(ytick)
                    ytick += ystep
                yticks.append(ymax)
                rounded_yticks = list(np.around(np.array(yticks), int(self.model.plot_axes["round y ticks"])))
                ax.set_yticks(rounded_yticks)
                ax.tick_params(axis='y',
                               labelsize=self.model.plot_axes["y ticks size"],
                               labelrotation=float(self.model.plot_axes["y ticks rotation"]))

            # ---- LEGEND
            if self.model.plot_legend["show legend"]:
                if not self.model.plot_legend["legend fontsize"] == '':
                    if self.model.plot_legend["legend anchor"] == 'custom':
                        ax.legend(loc='upper left',
                                  bbox_to_anchor=(float(self.model.plot_legend["legend x pos"]),
                                                  float(self.model.plot_legend["legend y pos"])),
                                  draggable=bool(self.model.plot_legend["legend draggable"]),
                                  ncols=int(self.model.plot_legend["legend ncols"]),
                                  fontsize=int(self.model.plot_legend["legend fontsize"]),
                                  framealpha=float(self.model.plot_legend["legend alpha"]),
                                  )
                    else:
                        ax.legend(loc=self.model.plot_legend["legend anchor"],
                                  draggable=bool(self.model.plot_legend["legend draggable"]),
                                  ncols=int(self.model.plot_legend["legend ncols"]),
                                  fontsize=int(self.model.plot_legend["legend fontsize"]),
                                  framealpha=float(self.model.plot_legend["legend alpha"]),
                                  )

                    for t, lh in zip(ax.get_legend().texts, ax.get_legend().legendHandles):
                        t.set_alpha(float(self.model.plot_legend["legend alpha"]))
                        lh.set_alpha(float(self.model.plot_legend["legend alpha"]))

            elif ax.get_legend():
                ax.get_legend().remove()

            plt.tight_layout()

        else:
            ax.clear()
        self.view.figures["plot"] = (fig, ax)
        self.view.canvas["plot"].draw()

    def trace_vars_to_model(self, key, *args):
        if key in self.model.plot_general_settings.keys():
            self.model.plot_general_settings[key] = self.view.vars[key].get()
        elif key in self.model.plot_axes.keys():
            self.model.plot_axes[key] = self.view.vars[key].get()
        elif key in self.model.plot_legend.keys():
            self.model.plot_legend[key] = self.view.vars[key].get()
