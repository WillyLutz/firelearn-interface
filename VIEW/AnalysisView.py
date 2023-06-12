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
from VIEW.CustomTable import CustomTable


class AnalysisView(ctk.CTkFrame):
    def __init__(self, app, master, controller):
        super().__init__(master=app)
        self.master = master
        self.controller = controller

        self.analysis_subtabs = ctk.CTkTabview(master=self.master, corner_radius=10)
        self.analysis_subtabs.place(relwidth=1.0, relheight=1.0)
        self.analysis_subtabs.add("Plot")
        self.analysis_subtabs.add("PCA")
        self.analysis_subtabs.add("Confusion")
        self.analysis_subtabs.add("Spike detection")
        self.analysis_subtabs.add("Feature importance")

    def set_controller(self, controller):
        self.controller = controller