import data.params as params
from MODEL.AnalysisModel import AnalysisModel
from MODEL.LearningModel import LearningModel
from MODEL.ProcessingModel import ProcessingModel


class MainModel:
    def __init__(self):
        self.version = params.version
        self.learning_model = LearningModel(self)
        self.processing_model = ProcessingModel(self)
        self.analysis_model = AnalysisModel(self)
