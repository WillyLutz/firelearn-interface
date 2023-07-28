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
        fig.savefig(filepath, dpi=int(self.model.plot_general_settings["dpi"]))

        # df = pd.DataFrame(columns=["X", "Y"])
        # df["X"] = x_data
        # df["Y"] = y_data
        #
        # df.to_csv(filepath, index=False)

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
                self.update_view_from_model()  # todo : does not work with multiple y :

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
            fig, ax = self.view.figures["plot"]
            ax.clear()
            for n in range(self.model.n_ydata+1):
                self.remove_ydata(str(n))

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

            # fig, ax = self.view.figures["plot"]
            # ax.plot(df[self.view.vars["xdata"].get()],
            #         df[self.view.vars[f"ydata {n_ydata}"].get()],
            #         label=self.view.vars[f"ydata legend {n_ydata}"].get(),
            #         linestyle=self.view.vars[f"linestyle {n_ydata}"].get(),
            #         linewidth=self.view.vars[f"linewidth {n_ydata}"].get(),
            #         color=self.view.vars[f"color {n_ydata}"].get(),
            #         alpha=self.view.vars[f"alpha {n_ydata}"].get(),
            #         )
            # --------------- TRACE
            self.view.trace_ids[f"ydata {n_ydata}"] = ydata_cbbox_var.trace("w", partial(self.view.trace_plot_data, n_ydata))
            self.view.trace_ids[f"ydata legend {n_ydata}"] = ydata_legend_var.trace("w", partial(self.view.trace_update_data,
                                                                                                 n_ydata))
            self.view.trace_ids[f"linestyle {n_ydata}"] = linestyle_var.trace("w",
                                                                              partial(self.view.trace_update_data, n_ydata))
            self.view.trace_ids[f"linewidth {n_ydata}"] = linewidth_var.trace("w",
                                                                              partial(self.view.trace_update_data, n_ydata))
            self.view.trace_ids[f"color {n_ydata}"] = color_var.trace("w", partial(self.view.trace_update_data, n_ydata))
            self.view.trace_ids[f"alpha {n_ydata}"] = alpha_var.trace("w", partial(self.view.trace_update_data, n_ydata))


            self.view.trace_plot_data(n_ydata)
            print("add ydata ", n_ydata, "lines ", self.view.lines)


        else:
            messagebox.showerror("Missing Values", "No dataset loaded")
            return False

    def remove_ydata(self, frame_key):
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
            del self.view.trace_ids[f"linewidth {n_ydata}"]
            del self.view.trace_ids[f"color {n_ydata}"]
            del self.view.trace_ids[f"alpha {n_ydata}"]
            del self.view.trace_ids[f"ydata legend {n_ydata}"]
            del self.view.trace_ids[f"linestyle {n_ydata}"]
            del self.view.trace_ids[f"ydata {n_ydata}"]
            del self.view.sliders[f"alpha {n_ydata}"]

            self.view.lines[n_ydata].pop(0).remove()
            del self.view.lines[n_ydata]

            self.view.canvas["plot"].draw()

            print("remove ydata ", n_ydata, "lines ", self.view.lines)

            self.model.n_ydata -= 1
