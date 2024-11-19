import os
import pickle
import random

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from scripts.MODEL.FeatureImportanceModel import FeatureImportanceModel
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from scripts import params as p
from scripts.WIDGETS.ErrEntry import ErrEntry


class FeatureImportanceController:
    def __init__(self, view,):
        self.model = FeatureImportanceModel()
        self.view = view
        self.view.controller = self  # set controller
        self.progress = None

    def load_clf(self, ):
        filename = filedialog.askopenfilename(title="Open file",
                                              filetypes=(("AI model", "*.rfc"),))
        if filename:
            clf = pickle.load(open(filename, "rb"))
            self.model.clf = clf

            self.view.vars["load clf"].set(filename)
            extension = os.path.basename(filename).split(".")[1]
            self.view.vars["clf type"].set(f"{p.MODEL_EXTENSIONS[extension]}")


    def draw_figure(self, ):
        if self.input_validation_feature_importance():
            plt.close()
            fig, ax = plt.subplots(figsize=(4, 4))
            new_canvas = FigureCanvasTkAgg(fig, master=self.view.frames["plot frame"])
            new_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
            self.view.canvas["features toolbar"].destroy()
            toolbar = NavigationToolbar2Tk(new_canvas,
                                           self.view.frames["plot frame"], pack_toolbar=False)
            toolbar.update()
            toolbar.grid(row=1, column=0, sticky='we')
            self.view.canvas["features"].get_tk_widget().destroy()
            self.view.canvas["features"] = new_canvas
            self.view.figures["features"] = (fig, ax)
            
            y_data = np.mean([tree.feature_importances_ for tree in self.model.clf.estimators_], axis=0)
            x_data = [i for i in range(len(y_data))]

            n_xticks = int(self.model.plot_axes["n x ticks"])
            n_yticks = int(self.model.plot_axes["n y ticks"])

            if n_yticks > len(y_data):
                messagebox.showerror("Value error", "Can not have more y ticks than y values")
                return False
            if n_xticks > len(x_data):
                messagebox.showerror("Value error", "Can not have more x ticks than x values")
                return False

            ax.clear()
            ax.plot(x_data, y_data,
                    linewidth=self.model.plot_general_settings["linewidth"],
                    linestyle=p.LINESTYLES[self.model.plot_general_settings["linestyle"]],
                    color=self.model.plot_general_settings["color"],
                    alpha=self.model.plot_general_settings["alpha"],
                    label="Feature importance"
                    )

            fill = self.model.plot_general_settings["fill"]
            if fill != 'None':
                ylim = plt.gca().get_ylim()
                if fill == 'Below':
                    ax.fill_between(x_data, y_data, ylim[0],
                                    color=self.model.plot_general_settings["color"],
                                    alpha=self.model.plot_general_settings["alpha fill"]
                                    )
                if fill == 'Above':
                    ax.fill_between(x_data, y_data, ylim[1],
                                    color=self.model.plot_general_settings["color"],
                                    alpha=self.model.plot_general_settings["alpha fill"]
                                    )

            ax.set_xlabel(self.model.plot_axes["x label"],
                          fontdict={"font": self.model.plot_axes["axes font"],
                                    "fontsize": self.model.plot_axes["x label size"]})
            ax.set_ylabel(self.model.plot_axes["y label"],
                          fontdict={"font": self.model.plot_axes["axes font"],
                                    "fontsize": self.model.plot_axes["y label size"]})
            ax.set_title(self.model.plot_general_settings["title"],
                         fontdict={"font": self.model.plot_general_settings["title font"],
                                   "fontsize": self.model.plot_general_settings["title size"], })
            xmin = min(x_data)
            xmax = max(x_data)
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

            ymin = min(y_data)
            ymax = max(y_data)
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

            # plt.tight_layout()
            self.view.figures["features"] = (fig, ax)
            self.view.canvas["features"].draw()

    def input_validation_feature_importance(self):
        errors = []
        if not self.model.clf:
            errors.append("No classifier loaded.")

        for key, entry in self.view.entries.items():
            if type(entry) == ErrEntry:
                if entry.error_message.get() != '':
                    errors.append(f"{key} : {entry.error_message.get()}")

        if errors:
            messagebox.showerror('Value Error','\n'.join(errors))
            return False
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

        df.to_csv(filepath+'.csv', index=False)

    def save_config(self, ):
        if self.input_validation_feature_importance():
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
        if len(list(widgets.values())) > 0 :
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
        # for key, value in self.model.plot_data.items():
        #     self.view.vars[key].set(value)
        # for key, value in self.model.plot_legend.items():
        #     self.view.vars[key].set(value)
        for key, value in self.model.plot_axes.items():
            self.view.vars[key].set(value)
        for key, value in self.model.plot_general_settings.items():
            self.view.vars[key].set(value)

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


    def trace_vars_to_model(self, key, *args):
        if key in self.model.plot_general_settings.keys():
            self.model.plot_general_settings[key] = self.view.vars[key].get()
        elif key in self.model.plot_axes.keys():
            self.model.plot_axes[key] = self.view.vars[key].get()
        elif key in self.model.plot_legend.keys():
            self.model.plot_legend[key] = self.view.vars[key].get()
