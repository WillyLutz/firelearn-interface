from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTabWidget, QFrame, QTextEdit, QHBoxLayout

from QtScripts.WIDGETS.TitleLabel import TitleLabel
from QtScripts.params import resource_path


class ChooseModelDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__()
        self.viewlayout = QVBoxLayout()
        self.parent = parent
        self.setLayout(self.viewlayout)
        
        self.title = TitleLabel(self, section='title1', text="What kind of model to choose ?")
        
        self.tabs = QTabWidget()
        self.utilities_tab = QFrame()
        self.rfc_tab = QFrame()
        self.svc_tab = QFrame()
        
        rfc_icon = QIcon(
            QPixmap(resource_path("data/firelearn_img/rfc_icon.png"))
        )
        svc_icon = QIcon(
            QPixmap(resource_path("data/firelearn_img/svc_icon.png"))
        )
        self.tabs.addTab(self.rfc_tab, rfc_icon, "RFC")
        self.tabs.addTab(self.svc_tab, svc_icon, "SVC")
        self.tabs.setIconSize(QSize(40, 40))
        
        self.viewlayout.addWidget(self.title)
        self.viewlayout.addWidget(self.tabs)
        
        self.manage_rfc()
        
    def manage_rfc(self):
        layout = QHBoxLayout()
        textedit = QTextEdit(parent=self.rfc_tab)
        html = []
        html.append('<b><font size="16" style="bold">Random Forest Classifier</font></b>')
        
        textedit.setHtml('\n'.join(html))
        
        layout.addWidget(textedit)
        self.rfc_tab.setLayout(layout)