from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator, QPalette, QColor
from PyQt6.QtWidgets import QFrame, QApplication, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QGridLayout, QLabel, \
    QComboBox, QSlider, QCheckBox, QColorDialog, QSizePolicy
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
)
from matplotlib.figure import Figure

from QtScripts import params
from QtScripts.VIEW.PlotGeneralParamsLayout import PlotGeneralParamsLayout
from QtScripts.WIDGETS.TitleLabel import TitleLabel


class FeatureImportanceView(QFrame):
    def __init__(self, app: QApplication, parent: QFrame = None, controller=None):
        super().__init__(parent=parent)
        self.app = app
        self.controller = controller
        self.parent = parent
        selflayout = QVBoxLayout()
        self.parent.setLayout(selflayout)
        
        self.main_layout = QHBoxLayout()
        
        self.widgets = {}
        
        # Create figure and canvas
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.ax = self.figure.add_subplot(111)
        
        # Add the toolbar
        self.toolbar = NavigationToolbar(self.canvas, self,)
        
        self.general_params_layout = QVBoxLayout()
        self.general_params_layout.addWidget(PlotGeneralParamsLayout(self, self.controller, self.general_params_layout))
        self.specific_params_layout = QGridLayout()
        self.drawing_layout = QVBoxLayout()
        
        selflayout.addLayout(self.main_layout, )
        secondary_layout = QVBoxLayout()
        secondary_layout.addLayout(self.specific_params_layout, stretch=3)
        secondary_layout.addLayout(self.drawing_layout, stretch=50)
        self.main_layout.addLayout(self.general_params_layout, stretch=7)
        self.main_layout.addLayout(secondary_layout, stretch=16)
        
        self.manage_specific_layout()
        self.manage_drawing_layout()
    
    def manage_specific_layout(self):
        specific_title_label = TitleLabel(parent=self, section='title1', text="Specific parameters")
        specific_load_btn = QPushButton(text="Load classifier", parent=self)
        specific_load_edit = QLineEdit(parent=self)
        specific_load_edit.setEnabled(False)
        
        linestyle_label = QLabel("Line style:", parent=self)
        linestyle_cbbox = QComboBox(parent=self)
        linestyle_cbbox.addItems(params.LINESTYLES)
        
        linewidth_label = QLabel("Line width:", parent=self)
        linewidth_edit = QLineEdit(parent=self)
        linewidth_edit.setValidator(QIntValidator())
        linewidth_edit.setText(str(params.DEFAULT_LINEWIDTH))
        
        alpha_label = QLabel("Alpha: 100", parent=self)
        alpha_slider = QSlider(parent=self)
        alpha_slider.setMinimum(0)
        alpha_slider.setMaximum(100)
        alpha_slider.setTickInterval(1)
        alpha_slider.setOrientation(Qt.Orientation.Horizontal)
        alpha_slider.valueChanged.connect(lambda: alpha_label.setText("Alpha: " + str(alpha_slider.value())))
        alpha_slider.setValue(100)
        
        fill_ckbox = QCheckBox(parent=self, text="Fill below importances")
        fill_alpha_label = QLabel("Fill alpha:", parent=self)
        fill_alpha_slider = QSlider(parent=self)
        fill_alpha_slider.setMinimum(0)
        fill_alpha_slider.setMaximum(100)
        fill_alpha_slider.setOrientation(Qt.Orientation.Horizontal)
        fill_alpha_slider.setTickInterval(1)
        
        specific_color_label = QLabel("Color: ", parent=self)
        specific_color_btn = QPushButton(parent=self, text="    ")
        palette = specific_color_btn.palette()
        palette.setColor(QPalette.ColorRole.Button, QColor("#32ab38"))
        specific_color_btn.setPalette(palette)
        specific_color_btn.setAutoFillBackground(True)
        specific_color_btn.show()
        
        draw_btn = QPushButton("Draw", parent=self)
        draw_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # ---- Connect
        fill_alpha_slider.valueChanged.connect(
            lambda value, lbl=fill_alpha_label: lbl.setText(f"Alpha: {value}")
        )
        fill_alpha_slider.setValue(50)
        
        specific_color_btn.clicked.connect(self.select_color)
        specific_load_btn.clicked.connect(self.controller.load_clf)
        
        draw_btn.clicked.connect(self.controller.draw)

        
        # ---- Layout
        self.specific_params_layout.addWidget(specific_title_label, 0, 0, 1, 2)
        self.specific_params_layout.addWidget(specific_load_btn, 2, 0)
        self.specific_params_layout.addWidget(specific_load_edit, 2, 1)
        self.specific_params_layout.addWidget(linestyle_label, 0, 2)
        self.specific_params_layout.addWidget(linestyle_cbbox, 0, 3)
        self.specific_params_layout.addWidget(linewidth_label, 1, 2)
        self.specific_params_layout.addWidget(linewidth_edit, 1, 3)
        self.specific_params_layout.addWidget(alpha_label, 2, 2)
        self.specific_params_layout.addWidget(alpha_slider, 2, 3)
        self.specific_params_layout.addWidget(fill_ckbox, 0, 4, 1, 2)
        self.specific_params_layout.addWidget(fill_alpha_label, 1, 4 )
        self.specific_params_layout.addWidget(fill_alpha_slider, 1, 5)
        self.specific_params_layout.addWidget(specific_color_label, 2, 4)
        self.specific_params_layout.addWidget(specific_color_btn, 2, 5)
        self.specific_params_layout.addWidget(draw_btn, 0, 6, 3, 1)

        
        # ---- Store widgets
        self.widgets["specific_load_btn"] = specific_load_btn
        self.widgets["specific_load_edit"] = specific_load_edit
        self.widgets[f"specific_linestyle_label"] = linestyle_label
        self.widgets[f"specific_linestyle_cbbox"] = linestyle_cbbox
        self.widgets[f"specific_linewidth_label"] = linewidth_label
        self.widgets[f"specific_linewidth_edit"] = linewidth_edit
        self.widgets[f"specific_alpha_label"] = alpha_label
        self.widgets[f"specific_alpha_slider"] = alpha_slider
        self.widgets[f"specific_fill_ckbox"] = fill_ckbox
        self.widgets[f"specific_fill_alpha_slider"] = fill_alpha_slider
        self.widgets[f"specific_color_label"] = specific_color_label
        self.widgets[f"specific_color_btn"] = specific_color_btn
        
        
    def manage_drawing_layout(self):
        specific_title_label = TitleLabel(parent=self, section='title1', text="Drawing")
        
        # ---- Store widgets
        
        # ---- Connect
        
        # ---- Layout
        self.drawing_layout.addWidget(specific_title_label)
        self.drawing_layout.addWidget(self.canvas)
        self.drawing_layout.addWidget(self.toolbar)
        self.plot_example()
    
    def plot_example(self):
        self.figure.tight_layout()
        self.canvas.draw()
    
    def select_color(self, ):
        color_dialog = QColorDialog()
        color = color_dialog.getColor(parent=self)
        if color:
            btn = self.widgets[f"specific_color_btn"]
            # .setStyleSheet("QPushButton{background-color:"+color.name()+";}")
            palette = btn.palette()
            palette.setColor(QPalette.ColorRole.Button, color)
            btn.setPalette(palette)
            btn.setAutoFillBackground(True)
            btn.show()
