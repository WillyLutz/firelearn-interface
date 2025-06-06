import logging

from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QApplication

from QtScripts.CONTROLLER.ConfusionController import ConfusionController
from QtScripts.CONTROLLER.DatasetController import DatasetController
from QtScripts.CONTROLLER.FeatureImportanceController import FeatureImportanceController
from QtScripts.CONTROLLER.PcaController import PcaController
from QtScripts.CONTROLLER.SpikeAnalysisController import SpikeAnalysisController
from QtScripts.MODEL.AnalysisModel import AnalysisModel
from QtScripts.VIEW.AnalysisView import AnalysisView

logger = logging.getLogger("__Analysis__")


class AnalysisController:
    def __init__(self, app: QApplication, parent_controller):
        self.app = app
        self.parent_controller = parent_controller
        self.model = AnalysisModel(self)  # set model
        self.view = AnalysisView(self.app, parent=self.parent_controller.view.analysis_tab, controller=self)
        
        self.dataset_controller = DatasetController(self.app, self)
        self.feature_importances_controller = FeatureImportanceController(self.app, self)
        self.pca_controller = PcaController(self.app, self)
        self.confusion_controller = ConfusionController(self.app, self)
        self.spike_controller = SpikeAnalysisController(self.app, self)
        
    @staticmethod
    def extract_button_color(btn):
        palette = btn.palette()
        bg_color = palette.color(QPalette.ColorRole.Button)
        color = bg_color.name()
        return color
