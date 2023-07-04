import os
import pickle
import random

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from MODEL.AnalysisModel import AnalysisModel
import customtkinter as ctk
from CONTROLLER import input_validation as ival
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import params as p

from CONTROLLER.PlotController import PlotController
from CONTROLLER.FeatureImportanceController import FeatureImportanceController


class AnalysisController:
    def __init__(self, view):
        self.model = AnalysisModel()
        self.view = view
        self.view.controller = self  # set controller

        self.progress = None

