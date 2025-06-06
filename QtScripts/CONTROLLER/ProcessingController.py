import logging

from PyQt6.QtWidgets import QApplication

from QtScripts.CONTROLLER.DatasetProcessingController import DatasetProcessingController
from QtScripts.CONTROLLER.SpikeDetectionController import SpikeDetectionController
from QtScripts.MODEL.ProcessingModel import ProcessingModel
from QtScripts.VIEW.ProcessingView import ProcessingView

logger = logging.getLogger("__Processing__")


class ProcessingController:
    def __init__(self, app: QApplication, parent_controller):
        self.app = app
        self.parent_controller = parent_controller
        self.model = ProcessingModel(self)  # set model
        self.view = ProcessingView(self.app, parent=self.parent_controller.view.processing_tab, controller=self)
        
        self.dataset_controller = DatasetProcessingController(self.app, self)
        self.spike_controller = SpikeDetectionController(self.app, self)
        # self.spike_controller = SpikeController(self.app, self)