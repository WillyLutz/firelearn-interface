from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QApplication, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QGridLayout, QLabel, \
    QComboBox, QSizePolicy

from QtScripts.VIEW.PlotGeneralParamsLayout import PlotGeneralParamsLayout
from QtScripts.WIDGETS.DatasetPlotTableEditor import DatasetPlotTableEditor
from QtScripts.WIDGETS.TitleLabel import TitleLabel
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
)
from matplotlib.figure import Figure

class DatasetView(QFrame):
    def __init__(self, app: QApplication, parent: QFrame = None, controller=None):
        super().__init__(parent=parent)
        self.app = app
        self.controller = controller
        self.parent = parent
        self.viewlayout = QVBoxLayout()
        self.parent.setLayout(self.viewlayout)
        
        self.main_layout = QHBoxLayout()
        
        self.widgets = {}
        
        # Create figure and canvas
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.ax = self.figure.add_subplot(111)

        
        # Add the toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        self.general_params_layout = QVBoxLayout()
        self.general_params_layout.addWidget(PlotGeneralParamsLayout(self, self.controller, self.general_params_layout))
        self.specific_params_layout = QGridLayout()
        self.drawing_layout = QVBoxLayout()
        
        self.viewlayout.addLayout(self.main_layout,)
        self.main_layout.addLayout(self.general_params_layout,stretch=7)
        self.main_layout.addLayout(self.specific_params_layout, stretch=6)
        self.main_layout.addLayout(self.drawing_layout, stretch=10)

        self.manage_specific_layout()
        self.manage_drawing_layout()
        
    def manage_specific_layout(self):
        specific_title_label = TitleLabel(parent=self, section='title1', text="Specific parameters")
        specific_load_btn = QPushButton(text="Load full_dataset", parent=self)
        specific_load_edit = QLineEdit(parent=self)
        specific_load_edit.setEnabled(False)
        
        specific_target_col_label = QLabel(parent=self, text="Target column:")
        specific_target_col_cbbox = QComboBox(parent=self)
        specific_target_col_cbbox.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        specific_dataset_tableplot = DatasetPlotTableEditor(parent=self, combo_items=None,)
        
        # ---- Store widgets
        self.widgets["specific_load_btn"] = specific_load_btn
        self.widgets["specific_load_edit"] = specific_load_edit
        self.widgets["specific_target_col_cbbox"] = specific_target_col_cbbox
        self.widgets["specific_dataset_tableplot"] = specific_dataset_tableplot
        
        # ---- Connect
        specific_load_btn.clicked.connect(self.controller.load_dataset)
        (specific_target_col_cbbox.currentIndexChanged.
         connect(lambda: self.controller.update_combotable_items("specific_dataset_tableplot")))
        
        # ---- Layout
        self.specific_params_layout.addWidget(specific_title_label, 0, 0, 1, 2)
        self.specific_params_layout.addWidget(specific_load_btn, 1, 0)
        self.specific_params_layout.addWidget(specific_load_edit, 1, 1)
        self.specific_params_layout.addWidget(specific_target_col_label, 2, 0)
        self.specific_params_layout.addWidget(specific_target_col_cbbox, 2, 1)
        self.specific_params_layout.addWidget(specific_dataset_tableplot, 3, 0, 1, 2)
    
    def manage_drawing_layout(self):
        specific_title_label = TitleLabel(parent=self, section='title1', text="Drawing")
        
        draw_btn = QPushButton("Draw", parent=self)
        # ---- Store widgets
        
        # ---- Connect
        draw_btn.clicked.connect(self.controller.draw)
        
        # ---- Layout
        self.drawing_layout.addWidget(specific_title_label)
        self.drawing_layout.addWidget(self.canvas)
        self.drawing_layout.addWidget(self.toolbar)
        self.drawing_layout.addWidget(draw_btn)
        self.plot_example()
        
    def plot_example(self):
        self.figure.tight_layout()
        self.canvas.draw()
        
    