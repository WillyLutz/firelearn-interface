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

    def dummy_figure(self):  # todo create plot
        fig, ax = plt.subplots(figsize=(p.DEFAULT_FIGUREWIDTH, p.DEFAULT_FIGUREHEIGHT))
        t = np.arange(0, 3, .01)
        ax.plot(t, random.randint(1, 4) *
                np.sin(random.randint(1, 4) * np.pi * t))
        ax.set_xlabel("time [s]")
        ax.set_ylabel("f(t)")

        return fig, ax

    def draw_figure(self, ):
        if self.input_validation_plot():
            fig, ax = self.view.figures["plot"]

            df = pd.read_csv(self.model.dataset_path, index_col=False)

            n_xticks = int(self.view.entries["n x ticks"].get())
            n_yticks = int(self.view.entries["n y ticks"].get())

            all_ymin = []  # for y ticks
            all_ymax = []

            # ---- PLOTTING
            x_data = df[self.view.cbboxes["xdata"].get()]
            ax.clear()
            for yi in range(self.model.n_ydata + 1):
                y_data = df[self.view.cbboxes[f"ydata {str(yi)}"].get()]
                all_ymin.append(min(y_data))
                all_ymax.append(max(y_data))

                ax.plot(x_data, y_data,
                        linewidth=self.view.entries[f"linewidth {str(yi)}"].get(),
                        linestyle=p.LINESTYLES[self.view.cbboxes[f"linestyle {str(yi)}"].get()],
                        color=self.view.vars[f"color {str(yi)}"].get(),
                        alpha=self.view.sliders[f"alpha {str(yi)}"].get(),
                        label=self.view.entries[f"ydata legend {str(yi)}"]
                        )

            y_data0 = df[self.view.cbboxes[f"ydata 0"].get()]  # todo : does not take account fo multiple y data
            if n_yticks > len(y_data0):
                messagebox.showerror("Value error", "Can not have more y ticks than y values")
                return False
            if n_xticks > len(x_data):
                messagebox.showerror("Value error", "Can not have more x ticks than x values")
                return False

            # ---- LABELS
            ax.set_xlabel(self.view.entries["x label"].get(),
                          fontdict={"font": self.view.cbboxes["axes font"].get(),
                                    "fontsize": self.view.sliders["x label size"].get()})
            ax.set_ylabel(self.view.entries["y label"].get(),
                          fontdict={"font": self.view.cbboxes["axes font"].get(),
                                    "fontsize": self.view.sliders["y label size"].get()})
            ax.set_title(self.view.entries["title"].get(),
                         fontdict={"font": self.view.cbboxes["title font"].get(),
                                   "fontsize": self.view.sliders["title size"].get(), })

            # ---- TICKS
            xmin = min(x_data)
            xmax = max(x_data)
            xstep = (xmax - xmin) / (n_xticks - 1)
            xtick = xmin
            xticks = []
            for i in range(n_xticks - 1):
                xticks.append(xtick)
                xtick += xstep
            xticks.append(xmax)
            rounded_xticks = list(np.around(np.array(xticks), int(self.view.entries["round x ticks"].get())))
            ax.set_xticks(rounded_xticks)
            ax.tick_params(axis='x',
                           labelsize=self.view.sliders["x ticks size"].get(),
                           labelrotation=float(self.view.sliders["x ticks rotation"].get()))

            ymin = min(all_ymin)
            ymax = max(all_ymax)
            ystep = (ymax - ymin) / (n_yticks - 1)
            ytick = ymin
            yticks = []
            for i in range(n_yticks - 1):
                yticks.append(ytick)
                ytick += ystep
            yticks.append(ymax)
            rounded_yticks = list(np.around(np.array(yticks), int(self.view.entries["round y ticks"].get())))
            ax.set_yticks(rounded_yticks)
            ax.tick_params(axis='y',
                           labelsize=self.view.sliders["y ticks size"].get(),
                           labelrotation=float(self.view.sliders["y ticks rotation"].get()))

            # ----- LEGEND
            # figure = self.create_figure()
            # self.view.canvas["feature importance"].figure = figure
            plt.tight_layout()

            if self.view.switches["show legend"].get():
                plt.legend()

            self.view.figures["plot"] = (fig, ax)
            self.view.canvas["plot"].draw()

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
        fig.savefig(filepath, dpi=int(self.view.entries["dpi"].get()))

    def export_figure_data(self, ax):
        filepath = filedialog.asksaveasfilename(title="Open file", filetypes=(("Coma Separated Value", "*.csv"),))
        line = ax.lines[0]
        x_data = line.get_xdata()
        y_data = line.get_ydata()

        df = pd.DataFrame(columns=["X", "Y"])
        df["X"] = x_data
        df["Y"] = y_data

        df.to_csv(filepath, index=False)

    def check_params_validity(self):
        if not self.input_validation_plot():
            return False
        return True

    def save_config(self, ):
        if self.check_params_validity():
            self.update_params(self.view.entries)
            self.update_params(self.view.cbboxes)
            self.update_params(self.view.sliders)
            self.update_params(self.view.vars)
            self.update_params(self.view.switches)

            f = filedialog.asksaveasfilename(defaultextension=".pltcfg",
                                             filetypes=[("Analysis - Simple plot", "*.pltcfg"), ])
            if f:
                self.model.save_model(path=f, )

    def update_params(self, widgets: dict, ):
        local_dict = {}
        for key, value in widgets.items():
            if type(value) == ctk.CTkTextbox:
                local_dict[key] = value.get('1.0', tk.END)
            else:
                local_dict[key] = value.get()
        if type(list(widgets.values())[0]) == ctk.CTkSwitch:
            self.model.switches.update(local_dict)
        if type(list(widgets.values())[0]) == ctk.CTkEntry:
            self.model.entries.update(local_dict)
        if type(list(widgets.values())[0]) == tk.ttk.Combobox:
            self.model.cbboxes.update(local_dict)
        if type(list(widgets.values())[0]) == ctk.CTkTextbox:
            local_dict = {}
            for key, value in widgets.items():
                local_dict[key] = value.get('1.0', tk.END)
            self.model.textboxes.update(local_dict)
        if type(list(widgets.values())[0]) == ctk.CTkSlider:
            self.model.sliders.update(local_dict)
        if type(list(widgets.values())[0]) == ctk.CTkCheckBox:
            self.model.checkboxes.update(local_dict)
        if type(list(widgets.values())[0]) == tk.IntVar or \
                type(list(widgets.values())[0]) == tk.StringVar or \
                type(list(widgets.values())[0]) == tk.DoubleVar:
            self.model.vars.update(local_dict)

    def load_config(self, ):
        f = filedialog.askopenfilename(title="Open file", filetypes=(("Analysis - Simple plot", "*.pltcfg"),))
        if f:
            if self.model.load_model(path=f):
                self.update_view_from_model()

    def update_view_from_model(self, ):

        for key, widget in self.view.cbboxes.items():
            if widget.cget('state') == "normal":
                widget.set(self.model.cbboxes[key])
            else:
                widget.configure(state='normal')
                widget.set(self.model.cbboxes[key])
                widget.configure(state='readonly')
                pass
        for key, widget in self.view.entries.items():
            if widget.cget('state') == 'normal':
                widget.delete(0, ctk.END)
                widget.insert(0, self.model.entries[key])
            else:
                widget.configure(state='normal')
                widget.insert(0, self.model.entries[key])
                widget.configure(state='disabled')

        for key, widget in self.view.switches.items():
            if widget.cget('state') == 'normal':
                if self.model.switches[key]:
                    widget.select()
                else:
                    widget.deselect()

        for key, widget in self.view.sliders.items():
            if widget.cget('state') == "normal":
                self.view.vars[key].set(self.model.vars[key])
                self.view.sliders[key].set(self.model.sliders[key])

        for key, widget in self.view.textboxes.items():
            MainController.update_textbox(widget, self.model.textboxes[key].split("\n"))

    def load_plot_dataset(self, ):
        filename = filedialog.askopenfilename(title="Open file",
                                              filetypes=(("Tables", "*.txt *.csv"),))
        if filename:
            df = pd.read_csv(filename)
            self.model.dataset_path = filename
            self.view.vars["load dataset"].set(filename)

            columns = list(df.columns)
            self.view.cbboxes["xdata"].configure(values=columns)
            self.view.cbboxes["xdata"].set(columns[0])
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
            ydata_label.place(relx=0, rely=0)
            ydata_cbbox = tk.ttk.Combobox(master=ydata_subframe, values=columns, state='readonly')
            ydata_cbbox.set(columns[-1])
            ydata_cbbox.place(relx=0, rely=0.15)
            self.view.cbboxes[f"ydata {n_ydata}"] = ydata_cbbox

            add_ydata_button = ctk.CTkButton(master=ydata_subframe, text="+", width=25, height=25, state='normal')
            add_ydata_button.place(anchor=tk.NE, relx=0.25, rely=0)
            subtract_ydata_button = ctk.CTkButton(master=ydata_subframe, text="-", width=25, height=25, state='normal')
            subtract_ydata_button.place(anchor=tk.NE, relx=0.38, rely=0)
            self.view.buttons[f"add ydata {n_ydata}"] = add_ydata_button
            self.view.buttons[f"subtract ydata {n_ydata}"] = subtract_ydata_button

            ydata_legend_label = ctk.CTkLabel(master=ydata_subframe, text="Legend label:")
            ydata_legend_label.place(relx=0.5, rely=0)
            ydata_legend_entry = ctk.CTkEntry(master=ydata_subframe)
            ydata_legend_entry.place(relx=0.5, rely=0.15, relwidth=0.4)
            self.view.entries[f"ydata legend {n_ydata}"] = ydata_legend_entry

            linestyle_label = ctk.CTkLabel(master=ydata_subframe, text="Linestyle:")
            linestyle_label.place(relx=0, rely=0.3)
            linestyle_cbbox = tk.ttk.Combobox(master=ydata_subframe, values=list(p.LINESTYLES.keys()), state='readonly')
            linestyle_cbbox.set("solid")
            linestyle_cbbox.place(relx=0, rely=0.5, relwidth=0.35)
            self.view.cbboxes[f"linestyle {n_ydata}"] = linestyle_cbbox

            linewidth_label = ctk.CTkLabel(master=ydata_subframe, text="Linewidth:")
            linewidth_label.place(relx=0.5, rely=0.3)
            linewidth_strvar = tk.StringVar()
            linewidth_strvar.set("1")
            linewidth_entry = ctk.CTkEntry(master=ydata_subframe, textvariable=linewidth_strvar)
            linewidth_entry.place(relx=0.5, rely=0.45, relwidth=0.2)
            self.view.entries[f"linewidth {n_ydata}"] = linewidth_entry
            self.view.vars[f"linewidth {n_ydata}"] = linewidth_strvar

            color_label = ctk.CTkLabel(master=ydata_subframe, text="Color:")
            color_label.place(relx=0, rely=0.65)
            color_var = tk.StringVar()
            color_var.set("green")
            color_button = ctk.CTkButton(master=ydata_subframe, textvariable=color_var,
                                         fg_color=color_var.get(), text_color='black')
            color_button.place(relx=0, rely=0.75)
            self.view.buttons[f"color {n_ydata}"] = color_button
            self.view.vars[f"color {n_ydata}"] = color_var

            alpha_label = ctk.CTkLabel(master=ydata_subframe, text="Alpha:")
            alpha_label.place(relx=0.5, rely=0.65)
            alpha_slider = ctk.CTkSlider(master=ydata_subframe, from_=0, to=1, number_of_steps=10)
            alpha_slider.set(p.DEFAULT_LINEALPHA)
            alpha_slider.place(relx=0.5, rely=0.8, relwidth=0.4)
            alpha_strvar = tk.StringVar()
            alpha_strvar.set(str(alpha_slider.get()))
            alpha_value_label = ctk.CTkLabel(master=ydata_subframe, textvariable=alpha_strvar)
            alpha_value_label.place(relx=0.7, rely=0.65)
            self.view.vars[f"alpha {n_ydata}"] = alpha_strvar
            self.view.sliders[f"alpha {n_ydata}"] = alpha_slider

            alpha_slider.configure(command=partial(self.view.update_slider_value, var=alpha_strvar))
            color_button.configure(command=partial(self.view.select_color, view=self.view,
                                                   selection_button_name=f'color {n_ydata}'))
            add_ydata_button.configure(command=partial(self.add_ydata, scrollable_frame))
            subtract_ydata_button.configure(command=partial(self.view.remove_ydata, f'{n_ydata}'))
        else:
            messagebox.showerror("Missing Values", "No dataset loaded")
            return False

    def remove_ydata(self, frame_key):
        n_ydata = self.model.n_ydata
        destroyed_number = int(frame_key.split(" ")[-1])

        for y in range(0, n_ydata + 1):
            if 0 <= y < destroyed_number:
                pass
            elif y == destroyed_number:
                # destroying all widgets related
                for child in self.view.ydata_subframes[str(y)].winfo_children():
                    child.destroy()

                # remove the frame from self.view.ydata_subframes
                self.view.ydata_subframes[str(y)].destroy()
                del self.view.ydata_subframes[str(y)]

                # destroying all items related in dicts
                del self.view.entries[f"ydata legend {destroyed_number}"]
                del self.view.entries[f"linewidth {destroyed_number}"]
                del self.view.buttons[f"add ydata {destroyed_number}"]
                del self.view.buttons[f"color {destroyed_number}"]
                del self.view.cbboxes[f"ydata {destroyed_number}"]
                del self.view.cbboxes[f"linestyle {destroyed_number}"]
                del self.view.vars[f"linewidth {destroyed_number}"]
                del self.view.vars[f"color {destroyed_number}"]
                del self.view.vars[f"alpha {destroyed_number}"]
                del self.view.sliders[f"alpha {destroyed_number}"]
                pass
            elif y > destroyed_number:
                self.view.rename_dict_key(self.view.entries, f"ydata legend {y}", f"ydata legend {y - 1}")
                self.view.rename_dict_key(self.view.entries, f"linewidth {y}", f"linewidth {y - 1}")
                self.view.rename_dict_key(self.view.buttons, f"add ydata {y}", f"add ydata {y - 1}")
                self.view.rename_dict_key(self.view.buttons, f"color {y}", f"color {y - 1}")
                self.view.rename_dict_key(self.view.buttons, f"subtract ydata {y}", f"subtract ydata {y-1}")
                self.view.rename_dict_key(self.view.cbboxes, f"ydata {y}", f"ydata {y - 1}")
                self.view.rename_dict_key(self.view.cbboxes, f"linestyle {y}", f"linestyle {y - 1}")
                self.view.rename_dict_key(self.view.vars, f"linewidth {y}", f"linewidth {y - 1}")
                self.view.rename_dict_key(self.view.vars, f"color {y}", f"color {y - 1}")
                self.view.rename_dict_key(self.view.vars, f"alpha {y}", f"alpha {y - 1}")
                self.view.rename_dict_key(self.view.sliders, f"alpha {y}", f"alpha {y - 1}")

                self.view.ydata_subframes[str(y)].grid(row=y-1, column=0, sticky=ctk.NSEW)  # replace the frame in grid
                self.view.rename_dict_key(self.view.ydata_subframes, str(y), str(y-1))

        self.model.n_ydata -= 1


