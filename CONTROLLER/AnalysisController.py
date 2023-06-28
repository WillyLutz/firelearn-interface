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
from data import params

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
            self.view.vars["clf type"].set(f"Type: {params.MODEL_EXTENSIONS[extension]}")

    def create_figure(self):  # todo create plot
        fig, ax = plt.subplots()
        t = np.arange(0, 3, .01)
        ax.plot(t, random.randint(1, 4) *
                        np.sin(random.randint(1, 4) * np.pi * t))
        ax.set_xlabel("time [s]")
        ax.set_ylabel("f(t)")

        return fig, ax

    def redraw_figure(self, ax):
        t = np.arange(0, 3, .01)
        ax.clear()
        ax.plot(t, random.randint(1, 4) *
                        np.sin(random.randint(1, 4) * np.pi * t))
        # figure = self.create_figure()
        # self.view.canvas["feature importance"].figure = figure
        self.view.canvas["feature importance"].draw()
        # todo : make it so it redraw the graph everytime




# todo: clean imports in processing and learning
