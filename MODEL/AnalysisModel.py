import pickle
from tkinter import messagebox

from data import params


class AnalysisModel:

    def __init__(self, main_model):
        self.main_model = main_model
        self.version = self.main_model.version
        self.clf = None

        self.plot = None

        self.entries = {}
        self.switches = {}
        self.cbboxes = {}
        self.checkboxes = {}
        self.vars = {}
        self.textboxes = {}
        self.checkvar = {}
        self.canvas = {}
        self.sliders = {}

        self.targets = []

    def load_model(self):
        pass

    def save_model(self):
        pass