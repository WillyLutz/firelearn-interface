import os
import pickle
import random
from string import ascii_letters

import fiiireflyyy.firelearn
import numpy as np
import pandas as pd
import sklearn.preprocessing
from matplotlib import pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from VIEW.AnalysisView import AnalysisView
from MODEL.AnalysisModel import AnalysisModel
import customtkinter as ctk
from CONTROLLER import input_validation as ival
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from CONTROLLER.ProgressBar import ProgressBar
from MODEL.ClfTester import ClfTester
from data import params as p

from typing import Callable

import seaborn as sns
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class AnalysisController:
    def __init__(self, main_controller, model: AnalysisModel, view: AnalysisView, ):
        self.model = model
        self.view = view
        self.main_controller = main_controller
        self.progress = None

    def load_clf(self, ):
        filename = self.main_controller.open_filedialog(mode="aimodel")
        if filename:
            clf = pickle.load(open(filename, "rb"))
            self.model.clf = clf

            self.view.vars["load clf"].set(filename)
            extension = os.path.basename(filename).split(".")[1]
            self.view.vars["clf type"].set(f"Type: {p.MODEL_EXTENSIONS[extension]}")

    def dummy_figure(self):  # todo create plot
        fig, ax = plt.subplots(figsize=(p.DEFAULT_FIGUREWIDTH, p.DEFAULT_FIGUREHEIGHT))
        t = np.arange(0, 3, .01)
        ax.plot(t, random.randint(1, 4) *
                np.sin(random.randint(1, 4) * np.pi * t))
        ax.set_xlabel("time [s]")
        ax.set_ylabel("f(t)")

        return fig, ax

    def draw_figure(self, ):
        if self.input_validation_feature_importances():
            fig, ax = self.view.figures["feature importance"]

            y_data = np.mean([tree.feature_importances_ for tree in self.model.clf.estimators_], axis=0)
            x_data = [i for i in range(len(y_data))]

            n_xticks = int(self.view.entries["fi n x ticks"].get())
            n_yticks = int(self.view.entries["fi n y ticks"].get())

            if n_yticks > len(y_data):
                messagebox.showerror("Value error", "Can not have more y ticks than y values")
                return False
            if n_xticks > len(x_data):
                messagebox.showerror("Value error", "Can not have more x ticks than x values")
                return False

            ax.clear()
            ax.plot(x_data, y_data,
                    linewidth=self.view.entries["fi linewidth"].get(),
                    linestyle=p.LINESTYLES[self.view.cbboxes["fi linestyle"].get()],
                    color=self.view.vars["fi color"].get(),
                    alpha=self.view.sliders["fi alpha"].get(),
                    )

            fill = self.view.cbboxes["fi fill"].get()
            if fill != 'None':
                ylim = plt.gca().get_ylim()
                if fill == 'Below':
                    ax.fill_between(x_data, y_data, ylim[0],
                                    color=self.view.vars["fi color"].get(),
                                    alpha=self.view.sliders["fi alpha fill"].get()
                                    )
                if fill == 'Above':
                    ax.fill_between(x_data, y_data, ylim[1],
                                    color=self.view.vars["fi color"].get(),
                                    alpha=self.view.sliders["fi alpha fill"].get()
                                    )

            ax.set_xlabel(self.view.entries["fi x label"].get(),
                          fontdict={"font": self.view.cbboxes["fi axes font"].get(),
                                    "fontsize": self.view.sliders["fi x label size"].get()})
            ax.set_ylabel(self.view.entries["fi y label"].get(),
                          fontdict={"font": self.view.cbboxes["fi axes font"].get(),
                                    "fontsize": self.view.sliders["fi y label size"].get()})
            ax.set_title(self.view.entries["fi title"].get(),
                         fontdict={"font": self.view.cbboxes["fi title font"].get(),
                                   "fontsize": self.view.sliders["fi title size"].get(), })


            xmin = min(x_data)
            xmax = max(x_data)
            xstep = (xmax - xmin) / (n_xticks - 1)
            xtick = xmin
            xticks = []
            for i in range(n_xticks - 1):
                xticks.append(xtick)
                xtick += xstep
            xticks.append(xmax)
            rounded_xticks = list(np.around(np.array(xticks), int(self.view.entries["fi round x ticks"].get())))
            ax.set_xticks(rounded_xticks)
            ax.tick_params(axis='x',
                           labelsize=self.view.sliders["fi x ticks size"].get(),
                           labelrotation=float(self.view.sliders["fi x ticks rotation"].get()))

            ymin = min(y_data)
            ymay = max(y_data)
            ystep = (ymay - ymin) / (n_yticks - 1)
            ytick = ymin
            yticks = []
            for i in range(n_yticks - 1):
                yticks.append(ytick)
                ytick += ystep
            yticks.append(ymay)
            rounded_yticks = list(np.around(np.array(yticks), int(self.view.entries["fi round y ticks"].get())))
            ax.set_yticks(rounded_yticks)
            ax.tick_params(axis='y',
                           labelsize=self.view.sliders["fi y ticks size"].get(),
                           labelrotation=float(self.view.sliders["fi y ticks rotation"].get()))

            # figure = self.create_figure()
            # self.view.canvas["feature importance"].figure = figure
            plt.tight_layout()
            self.view.figures["feature importance"] = (fig, ax)
            self.view.canvas["feature importance"].draw()

    def input_validation_feature_importances(self):
        fi_entries = {key: value for (key, value) in self.view.entries.items() if "fi" in key}

        if self.model.clf is None:
            messagebox.showerror("Value error", "No classifier loaded.")
            return False
        if float(fi_entries["fi linewidth"].get()) < 0:
            messagebox.showerror("Value error", "Line width must be positive.")

        for key, value in {"fi linewidth": "Line width", "fi n x ticks": "Number of x ticks",
                           "fi n y ticks": "Number of y ticks",}.items():
            if not ival.is_number(fi_entries["fi linewidth"].get()):
                messagebox.showerror("Value error", f"{value} must be a number.")
                return False

        for key, value in {"fi round x ticks": "Round x ticks", "fi round y ticks": "Round y ticks"}.items():
            if not ival.isint(fi_entries[key].get()):
                messagebox.showerror("Value error", f"{value} must be a positive integer.")
                return False

        for key, value in {"fi linewidth": "Line width", }.items():
            if ival.value_is_empty_or_none(fi_entries[key].get()):
                messagebox.showerror("Value error", f"{value} can not be empty or None")
                return False

        if int(self.view.entries["fi n x ticks"].get()) < 2:
            messagebox.showerror("Value error", "Can not have les than 2 ticks.")

        return True

# todo: clean imports in processing and learning
