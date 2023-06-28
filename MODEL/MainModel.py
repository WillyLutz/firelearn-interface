import os
from tkinter import messagebox

import data.params as params
import pandas as pd
import pickle
from MODEL.LearningModel import LearningModel
from MODEL.ProcessingModel import ProcessingModel
from MODEL.AnalysisModel import AnalysisModel


class MainModel:
    def __init__(self):
        self.version = params.version
        self.learning_model = LearningModel(self)
        self.processing_model = ProcessingModel(self)
        self.analysis_model = AnalysisModel(self)
