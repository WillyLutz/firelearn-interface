from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QApplication, QFrame, QVBoxLayout, QTabWidget, QSizePolicy

from QtScripts.params import resource_path


class LearningView(QFrame):
    def __init__(self, app: QApplication, parent:QFrame=None, controller=None):
        super().__init__(parent=parent)
        self.app = app
        self.controller = controller
        self.parent = parent
        self.viewlayout = QVBoxLayout()
        self.parent.setLayout(self.viewlayout)
        
        self.tabs = QTabWidget()
        self.utilities_tab = QFrame()
        self.rfc_tab = QFrame()
        self.svc_tab = QFrame()
        
        
        utilities_icon = QIcon(
            QPixmap(resource_path("data/firelearn_img/utilities_icon.png"))
        )
        rfc_icon = QIcon(
            QPixmap(resource_path("data/firelearn_img/rfc_icon.png"))
        )
        svc_icon = QIcon(
            QPixmap(resource_path("data/firelearn_img/svc_icon.png"))
        )
        self.tabs.addTab(self.rfc_tab, rfc_icon, "RFC")
        self.tabs.addTab(self.svc_tab, svc_icon, "SVC")
        self.tabs.addTab(self.utilities_tab, utilities_icon, "Utilities")
        self.tabs.setIconSize(QSize(40, 40))
        
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.viewlayout.addWidget(self.tabs)