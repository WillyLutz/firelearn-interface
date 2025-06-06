from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QVBoxLayout, QTabWidget, QFrame, QApplication

from QtScripts.params import resource_path


class ProcessingView(QFrame):
    def __init__(self, app: QApplication, parent: QFrame = None, controller=None):
        super().__init__(parent=parent)
        self.app = app
        self.controller = controller
        self.parent = parent
        self.viewlayout = QVBoxLayout()
        self.parent.setLayout(self.viewlayout)
        
        self.tabs = QTabWidget()
        self.pca_tab = QFrame()
        self.dataset_tab = QFrame()
        self.feature_importances_tab = QFrame()
        self.confusion_tab = QFrame()
        self.spike_detection_tab = QFrame()
        
        dataset_icon = QIcon(
            QPixmap(resource_path("data/firelearn_img/dataset_icon.png"))
        )
        spike_icon = QIcon(
            QPixmap(resource_path("data/firelearn_img/spike_detection_icon.png"))
        )
        self.tabs.addTab(self.dataset_tab, dataset_icon, "Dataset")
        self.tabs.addTab(self.spike_detection_tab, spike_icon, "Spike detection")
        
        
        self.tabs.setIconSize(QSize(40, 40))
        
        self.viewlayout.addWidget(self.tabs)