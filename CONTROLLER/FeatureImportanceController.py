import os
import pickle
import random

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from MODEL.FeatureImportanceModel import FeatureImportanceModel
import customtkinter as ctk
from CONTROLLER import input_validation as ival
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import params as p
from CONTROLLER.MainController import MainController


class FeatureImportanceController:
    def __init__(self, view,):
        self.model = FeatureImportanceModel()
        self.view = view
        self.view.controller = self  # set controller
        self.progress = None

    def load_clf(self, ):
        filename = filedialog.askopenfilename(title="Open file",
                                              filetypes=(("AI model", "*.rfc"),))
        print(filename)
        if filename:
            clf = pickle.load(open(filename, "rb"))
            self.model.clf = clf

            self.view.vars["load clf"].set(filename)
            extension = os.path.basename(filename).split(".")[1]
            self.view.vars["clf type"].set(f"Type: {p.MODEL_EXTENSIONS[extension]}")

    def dummy_figure(self):
        fig, ax = plt.subplots(figsize=(p.DEFAULT_FIGUREWIDTH, p.DEFAULT_FIGUREHEIGHT))
        t = np.arange(0, 3, .01)
        ax.plot(t, random.randint(1, 4) *
                np.sin(random.randint(1, 4) * np.pi * t))
        ax.set_xlabel("time [s]")
        ax.set_ylabel("f(t)")

        return fig, ax

    def draw_figure(self, ):
        if self.input_validation_feature_importance():
            fig, ax = self.view.figures["feature importance"]

            y_data = np.mean([tree.feature_importances_ for tree in self.model.clf.estimators_], axis=0)
            x_data = [i for i in range(len(y_data))]

            n_xticks = int(self.view.entries["n x ticks"].get())
            n_yticks = int(self.view.entries["n y ticks"].get())

            if n_yticks > len(y_data):
                messagebox.showerror("Value error", "Can not have more y ticks than y values")
                return False
            if n_xticks > len(x_data):
                messagebox.showerror("Value error", "Can not have more x ticks than x values")
                return False

            ax.clear()
            ax.plot(x_data, y_data,
                    linewidth=self.view.entries["linewidth"].get(),
                    linestyle=p.LINESTYLES[self.view.cbboxes["linestyle"].get()],
                    color=self.view.vars["color"].get(),
                    alpha=self.view.sliders["alpha"].get(),
                    )

            fill = self.view.cbboxes["fill"].get()
            if fill != 'None':
                ylim = plt.gca().get_ylim()
                if fill == 'Below':
                    ax.fill_between(x_data, y_data, ylim[0],
                                    color=self.view.vars["color"].get(),
                                    alpha=self.view.sliders["alpha fill"].get()
                                    )
                if fill == 'Above':
                    ax.fill_between(x_data, y_data, ylim[1],
                                    color=self.view.vars["color"].get(),
                                    alpha=self.view.sliders["alpha fill"].get()
                                    )

            ax.set_xlabel(self.view.entries["x label"].get(),
                          fontdict={"font": self.view.cbboxes["axes font"].get(),
                                    "fontsize": self.view.sliders["x label size"].get()})
            ax.set_ylabel(self.view.entries["y label"].get(),
                          fontdict={"font": self.view.cbboxes["axes font"].get(),
                                    "fontsize": self.view.sliders["y label size"].get()})
            ax.set_title(self.view.entries["title"].get(),
                         fontdict={"font": self.view.cbboxes["title font"].get(),
                                   "fontsize": self.view.sliders["title size"].get(), })

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

            ymin = min(y_data)
            ymay = max(y_data)
            ystep = (ymay - ymin) / (n_yticks - 1)
            ytick = ymin
            yticks = []
            for i in range(n_yticks - 1):
                yticks.append(ytick)
                ytick += ystep
            yticks.append(ymay)
            rounded_yticks = list(np.around(np.array(yticks), int(self.view.entries["round y ticks"].get())))
            ax.set_yticks(rounded_yticks)
            ax.tick_params(axis='y',
                           labelsize=self.view.sliders["y ticks size"].get(),
                           labelrotation=float(self.view.sliders["y ticks rotation"].get()))

            # figure = self.create_figure()
            # self.view.canvas["feature importance"].figure = figure
            plt.tight_layout()
            self.view.figures["feature importance"] = (fig, ax)
            self.view.canvas["feature importance"].draw()

    def input_validation_feature_importance(self):
        fi_entries = {key: value for (key, value) in self.view.entries.items() if "fi" in key}

        if not self.model.clf:
            messagebox.showerror("Value error", "No classifier loaded.")
            return False

        if float(fi_entries["linewidth"].get()) < 0:
            messagebox.showerror("Value error", "Line width must be positive.")

        for key, value in {"linewidth": "Line width", "n x ticks": "Number of x ticks",
                           "n y ticks": "Number of y ticks", "dpi": "Figure dpi"}.items():
            if not ival.is_number(fi_entries["linewidth"].get()):
                messagebox.showerror("Value error", f"{value} must be a number.")
                return False

        for key, value in {"round x ticks": "Round x ticks", "round y ticks": "Round y ticks",
                           "dpi": "Figure dpi"}.items():
            if not ival.isint(fi_entries[key].get()):
                messagebox.showerror("Value error", f"{value} must be a positive integer.")
                return False

        for key, value in {"linewidth": "Line width", }.items():
            if ival.value_is_empty_or_none(fi_entries[key].get()):
                messagebox.showerror("Value error", f"{value} can not be empty or None")
                return False

        if int(self.view.entries["n x ticks"].get()) < 2:
            messagebox.showerror("Value error", "Can not have les than 2 ticks.")

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
        if not self.input_validation_feature_importance():
            return False
        return True

    def save_config(self, ):
        if self.check_params_validity():
            self.update_params(self.view.entries)
            self.update_params(self.view.cbboxes)
            self.update_params(self.view.sliders)
            self.update_params(self.view.vars)

            f = filedialog.asksaveasfilename(defaultextension=".ficfg",
                                             filetypes=[("Analysis - Feature Importance", "*.ficfg"), ])
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
        f = filedialog.askopenfilename(title="Open file", filetypes=(("Analysis - Feature Importance", "*.ficfg"),))
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
            self.model.dataset_paths["plot"] = filename
            self.view.vars["plt load dataset"].set(filename)

            columns = list(df.columns)
            self.view.cbboxes["plt xdata"].configure(values=columns)
            self.view.cbboxes["plt xdata"].set(columns[0])
            ydata_curves = {key: value for (key, value) in self.view.cbboxes.items() if "plt ydata " in key}
            for key, value in ydata_curves.items():
                value.configure(values=columns)
                value.set(columns[-1])

