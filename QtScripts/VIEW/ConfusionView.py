import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator, QImage, QPixmap
from PyQt6.QtWidgets import QFrame, QApplication, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QGridLayout, QLabel, \
    QComboBox, QSizePolicy, QCheckBox, QSlider, QWidget, QScrollArea
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
)
from matplotlib.figure import Figure

from QtScripts import params
from QtScripts.WIDGETS.ConfusionTargetTableEditor import ConfusionTargetTableEditor
from QtScripts.WIDGETS.CustomProgressBar import CustomProgressBar
from QtScripts.WIDGETS.TitleLabel import TitleLabel


class ConfusionView(QFrame):
    def __init__(self, app: QApplication, parent: QFrame = None, controller=None):
        super().__init__(parent=parent)
        self.app = app
        self.controller = controller
        self.parent = parent
        self.viewlayout = QVBoxLayout()
        self.parent.setLayout(self.viewlayout)
        
        self.main_layout = QHBoxLayout()
        
        self.widgets = {}
        
        self.progress_bar = CustomProgressBar()
        self.progress_bar.set_task("No task running.")
        # Create figure and canvas
        self.colorbar = None
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.ax = self.figure.add_subplot(111)
        
        # Add the toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        self.general_params_layout = QVBoxLayout()
        self.specific_params_layout = QGridLayout()
        self.drawing_layout = QVBoxLayout()
        
        self.viewlayout.addLayout(self.main_layout, )
        self.viewlayout.addWidget(self.progress_bar)
        self.main_layout.addLayout(self.general_params_layout, stretch=7)
        self.main_layout.addLayout(self.specific_params_layout, stretch=6)
        self.main_layout.addLayout(self.drawing_layout, stretch=10)
        
        self.manage_general_params_layout()
        self.manage_specific_layout()
        self.manage_drawing_layout()
        
    def manage_general_params_layout(self):
        layout = QGridLayout()
        scroll_area = QScrollArea()
        wrapper_widget = QWidget()
        wrapper_widget.setLayout(layout)
        scroll_area.setWidget(wrapper_widget)
        scroll_area.setWidgetResizable(True)
        
        self.general_params_layout.addWidget(scroll_area)
        # --- GENERAL PARAMS ---
        general_params_title = TitleLabel(parent=self, section='title1', text='General parameters')
        plot_title_label = QLabel("Figure title:", parent=self)
        plot_title_edit = QLineEdit(parent=self)
        plot_title_font_label = QLabel("Title font:", parent=self)
        plot_title_font_cbbox = QComboBox(parent=self)
        plot_title_size_label = QLabel(f"Title font size: ", parent=self)
        plot_title_size_slider = QSlider(parent=self)
        plot_dpi_label = QLabel("DPI:", parent=self)
        plot_dpi_edit = QLineEdit(parent=self)
        plot_dpi_edit.setEnabled(False)
        plot_axes_font = QLabel("Axes font:", parent=self)
        plot_axes_font_cbbox = QComboBox(parent=self)
        
        # configure general widgets
        plot_title_font_cbbox.addItems(params.FONTS)
        plot_title_font_cbbox.setCurrentIndex(params.FONTS.index(params.DEFAULT_FONT))
        plot_title_size_slider.setMinimum(params.MIN_FONTSIZE)
        plot_title_size_slider.setMaximum(params.MAX_FONTSIZE)
        plot_title_size_slider.setOrientation(Qt.Orientation.Horizontal)
        plot_title_size_slider.setTickInterval(1)
        plot_dpi_edit.setValidator(QIntValidator())
        plot_dpi_edit.setText(str(params.DEFAULT_DPI))
        plot_axes_font_cbbox.addItems(params.FONTS)
        plot_axes_font_cbbox.setCurrentIndex(params.FONTS.index(params.DEFAULT_FONT))
        plot_axes_font_cbbox.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        plot_title_font_cbbox.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # store general widgets
        self.widgets["plot_title_edit"] = plot_title_edit
        self.widgets["plot_title_font_cbbox"] = plot_title_font_cbbox
        self.widgets["plot_title_size_slider"] = plot_title_size_slider
        self.widgets["plot_dpi_edit"] = plot_dpi_edit
        self.widgets["plot_axes_font_cbbox"] = plot_axes_font_cbbox
        
        # --- X PARAMS ---
        plot_x_axis_title = TitleLabel(parent=self, section='title1', text='X axis parameters')
        plot_x_label_label = QLabel("X label:", parent=self)
        plot_x_label_edit = QLineEdit(parent=self)
        plot_x_label_edit.setText("The input is")
        plot_x_label_size_label = QLabel("Label size: ", parent=self)
        plot_x_label_size_slider = QSlider(parent=self)
        plot_x_tick_rotation_label = QLabel("Tick rotation: 0", parent=self)
        plot_x_tick_rotation_slider = QSlider(parent=self)
        plot_x_tick_size_label = QLabel("Tick size : ", parent=self)
        plot_x_tick_size_slider = QSlider(parent=self)
        
        # configure X widgets
        plot_x_label_size_slider.setMinimum(params.MIN_FONTSIZE)
        plot_x_label_size_slider.setMaximum(params.MAX_FONTSIZE)
        plot_x_label_size_slider.setOrientation(Qt.Orientation.Horizontal)
        plot_x_label_size_slider.setTickInterval(1)
        plot_x_tick_rotation_slider.setMinimum(-180)
        plot_x_tick_rotation_slider.setMaximum(180)
        plot_x_tick_rotation_slider.setOrientation(Qt.Orientation.Horizontal)
        plot_x_tick_rotation_slider.setTickInterval(5)
        plot_x_tick_size_slider.setMinimum(params.MIN_FONTSIZE)
        plot_x_tick_size_slider.setMaximum(params.MAX_FONTSIZE)
        plot_x_tick_size_slider.setOrientation(Qt.Orientation.Horizontal)
        plot_x_tick_size_slider.setTickInterval(1)
        
        # store X widgets
        self.widgets["plot_x_label_edit"] = plot_x_label_edit
        self.widgets["plot_x_label_size_slider"] = plot_x_label_size_slider
        self.widgets["plot_x_tick_rotation_slider"] = plot_x_tick_rotation_slider
        self.widgets["plot_x_tick_size_slider"] = plot_x_tick_size_slider
        
        # --- Y PARAMS ---
        plot_y_axis_title = TitleLabel(parent=self, section='title1', text='Y axis parameters')
        plot_y_label_label = QLabel("Y label:", parent=self)
        plot_y_label_edit = QLineEdit(parent=self)
        plot_y_label_edit.setText("The input is classified as")
        plot_y_label_size_label = QLabel("Label size: ", parent=self)
        plot_y_label_size_slider = QSlider(parent=self)
        plot_y_tick_rotation_label = QLabel("Tick rotation: 0", parent=self)
        plot_y_tick_rotation_slider = QSlider(parent=self)
        plot_y_tick_size_label = QLabel("Tick size : ", parent=self)
        plot_y_tick_size_slider = QSlider(parent=self)
        
        # configure Y widgets
        plot_y_label_size_slider.setMinimum(params.MIN_FONTSIZE)
        plot_y_label_size_slider.setMaximum(params.MAX_FONTSIZE)
        plot_y_label_size_slider.setOrientation(Qt.Orientation.Horizontal)
        plot_y_label_size_slider.setTickInterval(1)
        plot_y_tick_rotation_slider.setMinimum(-180)
        plot_y_tick_rotation_slider.setMaximum(180)
        plot_y_tick_rotation_slider.setOrientation(Qt.Orientation.Horizontal)
        plot_y_tick_rotation_slider.setTickInterval(5)
        plot_y_tick_size_slider.setMinimum(params.MIN_FONTSIZE)
        plot_y_tick_size_slider.setMaximum(params.MAX_FONTSIZE)
        plot_y_tick_size_slider.setOrientation(Qt.Orientation.Horizontal)
        plot_y_tick_size_slider.setTickInterval(1)
        
        # store Y widgets
        self.widgets["plot_y_label_edit"] = plot_y_label_edit
        self.widgets["plot_y_label_size_slider"] = plot_y_label_size_slider
        self.widgets["plot_y_tick_rotation_slider"] = plot_y_tick_rotation_slider
        self.widgets["plot_y_tick_size_slider"] = plot_y_tick_size_slider
        
        # --- LEGEND ---
        plot_colorbar_title = TitleLabel(text="Colorbar parameters", parent=self, section="title1")
        plot_colorbar_label = QLabel("Colormap:", parent=self)
        plot_colorbar_cbbox = QComboBox(parent=self)
        plot_colorbar_pixmap_label = QLabel(parent=self)
        
        # configure colorbar widgets
        plot_colorbar_cbbox.addItems(params.COLORMAPS)
        plot_colorbar_cbbox.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        plot_colorbar_pixmap_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        plot_colorbar_pixmap_label.setPixmap(self.colormap_to_pixmap())
        plot_colorbar_pixmap_label.show()

        # store colorbar widgets
        self.widgets["plot_colorbar_title"] = plot_colorbar_title
        self.widgets["plot_colorbar_label"] = plot_colorbar_label
        self.widgets["plot_colorbar_cbbox"] = plot_colorbar_cbbox
        self.widgets["plot_colorbar_pixmap_label"] = plot_colorbar_pixmap_label
        
        # layout widgets
        layout.addWidget(general_params_title, 0, 0, 1, 2)
        layout.addWidget(plot_title_label, 1, 0)
        layout.addWidget(plot_title_edit, 1, 1)
        layout.addWidget(plot_title_font_label, 2, 0)
        layout.addWidget(plot_title_font_cbbox, 2, 1)
        layout.addWidget(plot_title_size_label, 3, 0)
        layout.addWidget(plot_title_size_slider, 3, 1)
        layout.addWidget(plot_dpi_label, 4, 0)
        layout.addWidget(plot_dpi_edit, 4, 1)
        layout.addWidget(plot_axes_font, 5, 0)
        layout.addWidget(plot_axes_font_cbbox, 5, 1)
        
        layout.addWidget(plot_x_axis_title, 6, 0, 1, 2)
        layout.addWidget(plot_x_label_label, 7, 0)
        layout.addWidget(plot_x_label_edit, 7, 1)
        layout.addWidget(plot_x_label_size_label, 8, 0)
        layout.addWidget(plot_x_label_size_slider, 8, 1)
        layout.addWidget(plot_x_tick_rotation_label, 9, 0)
        layout.addWidget(plot_x_tick_rotation_slider, 9, 1)
        layout.addWidget(plot_x_tick_size_label, 10, 0)
        layout.addWidget(plot_x_tick_size_slider, 10, 1)
        
        layout.addWidget(plot_y_axis_title, 13, 0, 1, 2)
        layout.addWidget(plot_y_label_label, 14, 0)
        layout.addWidget(plot_y_label_edit, 14, 1)
        layout.addWidget(plot_y_label_size_label, 15, 0)
        layout.addWidget(plot_y_label_size_slider, 15, 1)
        layout.addWidget(plot_y_tick_rotation_label, 16, 0)
        layout.addWidget(plot_y_tick_rotation_slider, 16, 1)
        layout.addWidget(plot_y_tick_size_label, 17, 0)
        layout.addWidget(plot_y_tick_size_slider, 17, 1)
        
        layout.addWidget(plot_colorbar_title, 20, 0, 1, 2)
        layout.addWidget(plot_colorbar_label, 21, 0)
        layout.addWidget(plot_colorbar_cbbox, 21, 1)
        layout.addWidget(plot_colorbar_pixmap_label, 22, 1, )

        
        # --- SIGNAL CONNECTIONS ---
        plot_title_size_slider.valueChanged.connect(
            lambda: plot_title_size_label.setText("Title font size: " + str(plot_title_size_slider.value()))
        )
        plot_title_size_slider.setValue(params.DEFAULT_FONTSIZE)
        
        plot_x_label_size_slider.valueChanged.connect(
            lambda: plot_x_label_size_label.setText("Label size: " + str(plot_x_label_size_slider.value()))
        )
        plot_x_label_size_slider.setValue(params.DEFAULT_FONTSIZE)
        
        plot_x_tick_rotation_slider.valueChanged.connect(
            lambda: plot_x_tick_rotation_label.setText("Tick rotation: " + str(plot_x_tick_rotation_slider.value()))
        )
        plot_x_tick_rotation_slider.setValue(params.DEFAULT_FONTROTATION)
        
        plot_x_tick_size_slider.valueChanged.connect(
            lambda: plot_x_tick_size_label.setText("Tick size : " + str(plot_x_tick_size_slider.value()))
        )
        plot_x_tick_size_slider.setValue(params.DEFAULT_FONTSIZE)
        
        plot_y_label_size_slider.valueChanged.connect(
            lambda: plot_y_label_size_label.setText("Label size: " + str(plot_y_label_size_slider.value()))
        )
        plot_y_label_size_slider.setValue(params.DEFAULT_FONTSIZE)
        
        plot_y_tick_rotation_slider.valueChanged.connect(
            lambda: plot_y_tick_rotation_label.setText("Tick rotation: " + str(plot_y_tick_rotation_slider.value()))
        )
        plot_y_tick_rotation_slider.setValue(params.DEFAULT_FONTROTATION)
        
        plot_y_tick_size_slider.valueChanged.connect(
            lambda: plot_y_tick_size_label.setText("Tick size : " + str(plot_y_tick_size_slider.value()))
        )
        plot_y_tick_size_slider.setValue(params.DEFAULT_FONTSIZE)
        
        plot_colorbar_cbbox.currentIndexChanged.connect(self.update_colormap)
        plot_colorbar_cbbox.setCurrentText(params.DEFAULT_COLORMAP)
        
    def manage_specific_layout(self):
        specific_title_label = TitleLabel(parent=self, section='title1', text="Specific parameters")
        specific_load_classifier_btn = QPushButton(parent=self, text="Load classifier")
        specific_load_classifier_edit = QLineEdit(parent=self)
        specific_load_classifier_edit.setEnabled(False)
        
        specific_load_dataset_btn = QPushButton(text="Load full_dataset", parent=self)
        specific_load_dataset_edit = QLineEdit(parent=self)
        specific_load_dataset_edit.setEnabled(False)
        
        specific_target_col_label = QLabel(parent=self, text="Target column:")
        specific_target_col_cbbox = QComboBox(parent=self)
        specific_target_col_cbbox.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        specific_train_confusion_table = ConfusionTargetTableEditor(parent=self, targets=[], set_='train')

        specific_test_confusion_table = ConfusionTargetTableEditor(parent=self, targets=[], set_='test')

        specific_select_all_btn = QPushButton(self, text="Select all")
        specific_deselect_all_btn = QPushButton(self, text="Deselect all")
        
        specific_annotation_label = QLabel(parent=self, text="Annotation mode:")
        specific_annotation_cbbox = QComboBox(parent=self)
        specific_annotation_cbbox.addItems(["percent", "numeric", "None"])
        specific_annotation_cbbox.setCurrentText("percent")
        
        specific_annotation_size_label = QLabel(parent=self, text="Annotation size:")
        specific_annotation_size_slider = QSlider(parent=self)
        specific_annotation_size_slider.setMinimum(params.MIN_FONTSIZE)
        specific_annotation_size_slider.setMaximum(params.MAX_FONTSIZE)
        specific_annotation_size_slider.setOrientation(Qt.Orientation.Horizontal)
        specific_annotation_size_slider.setTickInterval(1)
        
        specific_cup_ckbox = QCheckBox(parent=self, text="Show only CUP")
        
        # store widgets
        self.widgets["specific_load_classifier_edit"] = specific_load_classifier_edit
        self.widgets["specific_load_dataset_edit"] = specific_load_dataset_edit
        self.widgets["specific_target_col_cbbox"] = specific_target_col_cbbox
        self.widgets["specific_annotation_cbbox"] = specific_annotation_cbbox
        self.widgets["specific_annotation_size_slider"] = specific_annotation_size_slider
        self.widgets["specific_test_confusion_table"] = specific_test_confusion_table
        self.widgets["specific_train_confusion_table"] = specific_train_confusion_table
        self.widgets["specific_cup_ckbox"] = specific_cup_ckbox

        # layout 
        self.specific_params_layout.addWidget(specific_title_label, 0, 0, 1, 2)
        self.specific_params_layout.addWidget(specific_load_classifier_btn, 1, 0)
        self.specific_params_layout.addWidget(specific_load_classifier_edit, 1, 1)
        self.specific_params_layout.addWidget(specific_load_dataset_btn, 2, 0)
        self.specific_params_layout.addWidget(specific_load_dataset_edit, 2, 1)
        self.specific_params_layout.addWidget(specific_target_col_label, 3, 0)
        self.specific_params_layout.addWidget(specific_target_col_cbbox, 3, 1)
        self.specific_params_layout.addWidget(specific_train_confusion_table, 4, 0, 1, 2)
        self.specific_params_layout.addWidget(specific_test_confusion_table, 5, 0, 1, 2)
        self.specific_params_layout.addWidget(specific_select_all_btn, 6, 0)
        self.specific_params_layout.addWidget(specific_deselect_all_btn, 6, 1)
        self.specific_params_layout.addWidget(specific_annotation_label, 7, 0)
        self.specific_params_layout.addWidget(specific_annotation_cbbox, 7, 1)
        self.specific_params_layout.addWidget(specific_annotation_size_label, 8, 0)
        self.specific_params_layout.addWidget(specific_annotation_size_slider, 8, 1)
        self.specific_params_layout.addWidget(specific_cup_ckbox, 9, 0)

        # connect
        specific_annotation_size_slider.valueChanged.connect(lambda: specific_annotation_size_label.
                                                             setText(f"Annotation size: {specific_annotation_size_slider.value()}"))
        specific_annotation_size_slider.setValue(params.DEFAULT_FONTSIZE)
        
        specific_load_classifier_btn.clicked.connect(self.controller.load_classifier)
        specific_load_dataset_btn.clicked.connect(self.controller.load_dataset)
        specific_select_all_btn.clicked.connect(self.controller.select_all)
        specific_deselect_all_btn.clicked.connect(self.controller.deselect_all)
        specific_target_col_cbbox.currentIndexChanged.connect(self.controller.update_target_col)
    
    def manage_drawing_layout(self):
        specific_title_label = TitleLabel(parent=self, section='title1', text="Drawing")
        
        compute_btn = QPushButton(parent=self, text="Compute")
        draw_btn = QPushButton("Draw", parent=self)
        # ---- Store widgets
        
        # ---- Connect
        compute_btn.clicked.connect(self.controller.compute_confusion)
        draw_btn.clicked.connect(self.controller.draw)
        
        # ---- Layout
        self.drawing_layout.addWidget(specific_title_label)
        self.drawing_layout.addWidget(self.canvas)
        self.drawing_layout.addWidget(self.toolbar)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(compute_btn)
        btn_layout.addWidget(draw_btn)
        self.drawing_layout.addLayout(btn_layout)
        self.plot_example()
    
    def plot_example(self):
        self.figure.tight_layout()
        self.canvas.draw()
    
    def colormap_to_pixmap(self, cmap_name='seismic', width=256, height=20):
        gradient = np.linspace(0, 1, width).reshape(1, -1)
        gradient = np.vstack([gradient] * height)
        
        cmap = plt.get_cmap(cmap_name)
        rgba_img = (cmap(gradient) * 255).astype(np.uint8)
        qimage = QImage(rgba_img.data, rgba_img.shape[1], rgba_img.shape[0], QImage.Format.Format_RGBA8888)
        return QPixmap.fromImage(qimage)
    
    def update_colormap(self):
        cmap = self.widgets["plot_colorbar_cbbox"].currentText()
        self.widgets["plot_colorbar_pixmap_label"].setPixmap(self.colormap_to_pixmap(cmap))
        self.widgets["plot_colorbar_pixmap_label"].show()
        
        