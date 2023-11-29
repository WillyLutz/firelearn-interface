from scripts.MODEL.AnalysisModel import AnalysisModel


class AnalysisController:
    def __init__(self, view):
        self.model = AnalysisModel()
        self.view = view
        self.view.controller = self  # set controller

        self.progress = None

