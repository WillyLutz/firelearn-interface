import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QFrame, QApplication, QVBoxLayout, QGridLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, \
    QComboBox, QSizePolicy, QTabWidget
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar
)
from matplotlib.figure import Figure

from QtScripts import params
from QtScripts.WIDGETS.SelectedSpikesTableEditor import SelectedSpikesTableEditor
from QtScripts.WIDGETS.SpikeFilterCheckTable import SpikeFilterCheckTable
from QtScripts.WIDGETS.TitleLabel import TitleLabel


class SpikeAnalysisView(QFrame):
    def __init__(self, app: QApplication, parent: QFrame = None, controller=None):
        super().__init__(parent=parent)
        self.app = app
        self.controller = controller
        self.parent = parent
        self.viewlayout = QVBoxLayout()
        self.parent.setLayout(self.viewlayout)
        
        self.main_layout = QGridLayout()
        
        self.widgets = {}
        self.raster_figure = Figure()
        self.raster_canvas = FigureCanvas(self.raster_figure)
        self.raster_canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.raster_ax = self.raster_figure.add_subplot(111)
        # Add the toolbar
        self.raster_toolbar = NavigationToolbar(self.raster_canvas, self)
        
        self.spike_figure = Figure()
        self.spike_canvas = FigureCanvas(self.spike_figure)
        self.spike_canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.spike_ax = self.spike_figure.add_subplot(111)
        # Add the toolbar
        self.spike_toolbar = NavigationToolbar(self.spike_canvas, self)
        
        self.viewlayout.addLayout(self.main_layout, )
        
        
        # self.general_params_layout = QVBoxLayout()
        # self.general_params_layout.addWidget(PlotGeneralParamsLayout(self, self.controller, self.general_params_layout))
        
        self.specific_params_layout = QGridLayout()
        self.raster_layout = QVBoxLayout()
        self.spike_layout = QGridLayout()
        self.tabs_layout = QVBoxLayout()
        
        self.plot_tabs = QTabWidget()
        self.raster_frame = QFrame()
        self.raster_frame.setLayout(self.raster_layout)
        
        self.spike_frame = QFrame()
        self.spike_frame.setLayout(self.spike_layout)
        
        self.plot_tabs.addTab(self.raster_frame, "Raster plot")
        self.plot_tabs.addTab(self.spike_frame, "Spikes plot")
        self.tabs_layout.addWidget(self.plot_tabs)
        
        # self.main_layout.addLayout(self.general_params_layout, 0, 0, 2, 1, )
        self.main_layout.addLayout(self.specific_params_layout, 0, 0,)
        self.main_layout.addLayout(self.tabs_layout, 0, 1, 3, 1)

        self.main_layout.setColumnStretch(0, 1)
        self.main_layout.setColumnStretch(1, 1)
        self.main_layout.setRowStretch(0, 1)
        self.main_layout.setRowStretch(1, 10)
        
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._manage_specific_layout()
        self._manage_raster_tab()
        self._manage_spike_tab()
        
    def manage_plot_tabs(self):
        pass
    
    def _manage_specific_layout(self):
        specific_title_label = TitleLabel(self, text="Spike selection", section="title1")
        specific_load_btn = QPushButton(parent=self, text="Load dataset")
        specific_load_edit = QLineEdit(parent=self)
        specific_load_edit.setEnabled(False)
        
        specific_filter_column_label = QLabel(parent=self, text="Sub sample dataset if column: ")
        specific_subsample_cbbox = QComboBox(parent=self)
        specific_subsample_cbbox.addItems(["None", "File", "Target"])
        specific_filter_value_label = QLabel(parent=self, text="has value(s): ")
        specific_subsample_table = SpikeFilterCheckTable(parent=self, items=[])
        
        raster_title_label = TitleLabel(self, text="Raster plot", section="title1")
        
        raster_as_colormap_label = QLabel(parent=self, text="Show as colormap:")
        raster_as_colormap_cbbox = QComboBox(parent=self)
        raster_as_colormap_cbbox.addItems(["None", "Filtered values", "Peak value",
                                           "Minimum value", "Maximum value", "Slope", "Extrema ratio (min/max)",
                                           ])
        
        raster_colormap_label = QLabel("Colormap:", parent=self)
        raster_colormap_cbbox = QComboBox(parent=self)
        raster_colormap_pixmap_label = QLabel(parent=self)
        
        # configure colorbar widgets
        raster_colormap_cbbox.addItems(params.COLORMAPS)
        raster_colormap_cbbox.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        # raster_colormap_pixmap_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        raster_colormap_pixmap_label.setPixmap(self.colormap_to_pixmap())
        raster_colormap_pixmap_label.show()
        
        spike_title_label = TitleLabel(self, text="Spike plot", section="title1")

        spike_plot_table = SelectedSpikesTableEditor(self, )

        
        
        # store
        self.widgets["raster_as_colormap_cbbox"] = raster_as_colormap_cbbox
        self.widgets["raster_colormap_cbbox"] = raster_colormap_cbbox
        self.widgets["raster_colormap_pixmap_label"] = raster_colormap_pixmap_label
        
        self.widgets["specific_load_edit"] = specific_load_edit
        self.widgets["specific_subsample_cbbox"] = specific_subsample_cbbox
        self.widgets["specific_subsample_table"] = specific_subsample_table
        self.widgets["spike_plot_table"] = spike_plot_table

        
        # layout
        self.specific_params_layout.addWidget(specific_title_label, 0, 0, 1, 3)
        self.specific_params_layout.addWidget(specific_load_btn, 1, 0)
        self.specific_params_layout.addWidget(specific_load_edit, 1, 1, 1, 2)
        self.specific_params_layout.addWidget(specific_filter_column_label, 2, 0)
        self.specific_params_layout.addWidget(specific_subsample_cbbox, 2, 1)
        self.specific_params_layout.addWidget(specific_filter_value_label, 2, 2)
        self.specific_params_layout.addWidget(specific_subsample_table, 3, 0, 1, 3)
        
        
        raster_layout = QVBoxLayout()
        raster_layout.addWidget(raster_title_label,)
        
        colormap_layout = QHBoxLayout()
        colormap_layout.addWidget(raster_as_colormap_label)
        colormap_layout.addWidget(raster_as_colormap_cbbox)
        colormap_layout.addWidget(raster_colormap_label)
        colormap_layout.addWidget(raster_colormap_cbbox)
        colormap_layout.addWidget(raster_colormap_pixmap_label)
        raster_layout.addLayout(colormap_layout)
        self.specific_params_layout.addLayout(raster_layout, 4, 0, 1, 3)
        
        spike_layout = QVBoxLayout()
        spike_layout.addWidget(spike_title_label)
        spike_layout.addWidget(spike_plot_table)
        self.specific_params_layout.addLayout(spike_layout, 5, 0, 1, 3)

        self.specific_params_layout.setRowStretch(0, 1)
        self.specific_params_layout.setRowStretch(1, 1)
        self.specific_params_layout.setRowStretch(2, 1)

        self.specific_params_layout.setColumnStretch(0, 1)
        self.specific_params_layout.setColumnStretch(1, 1)
        self.specific_params_layout.setColumnStretch(2, 1)
        self.specific_params_layout.setColumnStretch(3, 2)

        # connect
        raster_colormap_cbbox.currentIndexChanged.connect(self.update_colormap)
        raster_colormap_cbbox.setCurrentText(params.DEFAULT_COLORMAP)
        specific_load_btn.clicked.connect(self.controller.load_dataset)
        specific_subsample_cbbox.currentIndexChanged.connect(self.controller.filter_column_changed)
        
        
    def _manage_raster_tab(self):
       
        raster_selected_spike_label = QLabel(parent=self, text="Selected spike: (x=, y=)")
        
        raster_previous_x_btn = QPushButton(parent=self, text="<-- Previous spike")
        raster_next_x_btn = QPushButton(parent=self, text="Next spike -->")
        
        raster_select_all_index_btn = QPushButton(parent=self, text="Select all current index")
        raster_select_all_column_btn = QPushButton(parent=self, text="Select all current column")
        
        raster_add_spike_btn = QPushButton(parent=self, text="Add selected spike")
        raster_params_btn = QPushButton(parent=self, text="Raster parameters")
        raster_draw_btn = QPushButton(parent=self, text="Draw Raster")
        
        # store
        
        self.widgets["raster_selected_spike_label"] = raster_selected_spike_label
        # layout
        
        
        self.raster_layout.addWidget(raster_selected_spike_label,)
        
        raster_top_btn_layout = QHBoxLayout()
        raster_top_btn_layout.addWidget(raster_previous_x_btn)
        raster_top_btn_layout.addWidget(raster_next_x_btn)
        raster_top_btn_layout.addWidget(raster_select_all_index_btn)
        raster_top_btn_layout.addWidget(raster_select_all_column_btn)
        self.raster_layout.addLayout(raster_top_btn_layout)
        
    
        self.raster_layout.addWidget(self.raster_canvas)
        self.raster_layout.addWidget(self.raster_toolbar)
        
        bottom_btn_layout = QHBoxLayout()
        bottom_btn_layout.addWidget(raster_add_spike_btn)
        bottom_btn_layout.addWidget(raster_params_btn)
        bottom_btn_layout.addWidget(raster_draw_btn)
        self.raster_layout.addLayout(bottom_btn_layout)
        
        
        # connect
        raster_add_spike_btn.clicked.connect(self.controller.add_selected_spike)
        
        
        raster_draw_btn.clicked.connect(self.controller.draw_raster)
        
        raster_next_x_btn.clicked.connect(lambda: self.controller.select_next_previous_spike('x', 1))
        raster_previous_x_btn.clicked.connect(lambda: self.controller.select_next_previous_spike('x', -1))
        
        raster_params_btn.setEnabled(False)
        raster_select_all_column_btn.setEnabled(False)
        raster_select_all_index_btn.setEnabled(False)

    def _manage_spike_tab(self):
        
        spike_draw_btn = QPushButton(parent=self, text="Draw spikes")
        # store
        # layout
        self.spike_layout.addWidget(self.spike_canvas, 2, 0)
        self.spike_layout.addWidget(self.spike_toolbar, 3, 0)
        self.spike_layout.addWidget(spike_draw_btn, 4, 0)
        # connect
        spike_draw_btn.clicked.connect(self.controller.draw_spikes)
        self.plot_example()
    
    def plot_example(self):
        self.spike_figure.tight_layout()
        self.spike_canvas.draw()
        self.raster_figure.tight_layout()
        self.raster_canvas.draw()
        
    def update_colormap(self):
        cmap = self.widgets["raster_colormap_cbbox"].currentText()
        self.widgets["raster_colormap_pixmap_label"].setPixmap(self.colormap_to_pixmap(cmap))
        self.widgets["raster_colormap_pixmap_label"].show()
    
    def colormap_to_pixmap(self, cmap_name='seismic', width=256, height=20):
        gradient = np.linspace(0, 1, width).reshape(1, -1)
        gradient = np.vstack([gradient] * height)
        
        cmap = plt.get_cmap(cmap_name)
        rgba_img = (cmap(gradient) * 255).astype(np.uint8)
        qimage = QImage(rgba_img.data, rgba_img.shape[1], rgba_img.shape[0], QImage.Format.Format_RGBA8888)
        return QPixmap.fromImage(qimage)