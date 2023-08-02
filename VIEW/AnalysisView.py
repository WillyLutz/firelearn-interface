import tkinter as tk
from functools import partial
from tkinter import ttk

import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from CONTROLLER.AnalysisController import AnalysisController
from VIEW.PlotView import PlotView
from VIEW.FeatureImportanceView import FeatureImportanceView
from VIEW.PcaView import PcaView

import params as p


class AnalysisView(ctk.CTkFrame):
    def __init__(self, app, master, parent_view):
        super().__init__(master=app)
        self.app = app
        self.master = master
        self.parent_view = parent_view
        self.controller = AnalysisController(self, )

        self.analysis_subtabs = ctk.CTkTabview(master=self.master, corner_radius=10)
        self.analysis_subtabs.place(relwidth=1.0, relheight=1.0)
        self.analysis_subtabs.add("Feature importance")
        self.analysis_subtabs.add("Plot")
        self.analysis_subtabs.add("PCA")

        self.analysis_subtabs.add("Confusion")
        self.analysis_subtabs.add("Spike detection")

        self.plot_view = PlotView(app=self.app, master=self.analysis_subtabs.tab("Plot"),
                                  parent_view=self)
        self.feature_importance_view = FeatureImportanceView(app=self.app, parent_view=self,
                                                             master=self.analysis_subtabs.tab("Feature importance"))
        self.pca_view = PcaView(app=self.app, parent_view=self,
                                master=self.analysis_subtabs.tab("PCA"))

    def update_slider_value(self, value, var):
        self.parent_view.update_slider_value(value, var)

    def select_color(self):
        self.parent_view.select_color()
