from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QWidget, QLineEdit, QComboBox, QSlider, QCheckBox, \
    QScrollArea

from QtScripts import params
from QtScripts.WIDGETS.TitleLabel import TitleLabel


class PlotGeneralParamsLayout(QFrame):
    def __init__(self, parent=None, controller=None, container_layout=None):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.container_layout = container_layout
        
        
        self.scrollable_layout = QGridLayout()
        
        # self.setLayout(self.scrollable_layout)
        
        self.manage_layout(self.parent.parent, )
        
        scroll_area = QScrollArea()
        wrapper_widget = QWidget()
        wrapper_widget.setLayout(self.scrollable_layout)
        scroll_area.setWidget(wrapper_widget)
        scroll_area.setWidgetResizable(True)
        
        self.container_layout.addWidget(scroll_area)
    
    def manage_layout(self, p):
        # --- GENERAL PARAMS ---
        general_params_title = TitleLabel(parent=p, section='title1', text='General parameters')
        plot_title_label = QLabel("Figure title:", parent=p)
        plot_title_edit = QLineEdit(parent=p)
        plot_title_font_label = QLabel("Title font:", parent=p)
        plot_title_font_cbbox = QComboBox(parent=p)
        plot_title_size_label = QLabel(f"Title font size: ", parent=p)
        plot_title_size_slider = QSlider(parent=p)
        plot_dpi_label = QLabel("DPI:", parent=p)
        plot_dpi_edit = QLineEdit(parent=p)
        plot_dpi_edit.setEnabled(False)
        plot_axes_font = QLabel("Axes font:", parent=p)
        plot_axes_font_cbbox = QComboBox(parent=p)
        
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
        self.parent.widgets["plot_title_edit"] = plot_title_edit
        self.parent.widgets["plot_title_font_cbbox"] = plot_title_font_cbbox
        self.parent.widgets["plot_title_size_slider"] = plot_title_size_slider
        self.parent.widgets["plot_dpi_edit"] = plot_dpi_edit
        self.parent.widgets["plot_axes_font_cbbox"] = plot_axes_font_cbbox
        
        # --- X PARAMS ---
        plot_x_axis_title = TitleLabel(parent=p, section='title1', text='X axis parameters')
        plot_x_label_label = QLabel("X label:", parent=p)
        plot_x_label_edit = QLineEdit(parent=p)
        plot_x_label_size_label = QLabel("Label size: ", parent=p)
        plot_x_label_size_slider = QSlider(parent=p)
        plot_x_tick_rotation_label = QLabel("Tick rotation: 0", parent=p)
        plot_x_tick_rotation_slider = QSlider(parent=p)
        plot_x_tick_size_label = QLabel("Tick size : ", parent=p)
        plot_x_tick_size_slider = QSlider(parent=p)
        plot_x_n_tick_label = QLabel("N ticks:", parent=p)
        plot_x_n_tick_edit = QLineEdit(parent=p)
        plot_x_round_label = QLabel("Round:", parent=p)
        plot_x_round_edit = QLineEdit(parent=p)
        
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
        plot_x_n_tick_edit.setValidator(QIntValidator())
        plot_x_n_tick_edit.setText(str(params.DEFAULT_FONTSIZE))
        plot_x_round_edit.setValidator(QIntValidator())
        plot_x_round_edit.setText(str(params.DEFAULT_ROUND))
        
        # store X widgets
        self.parent.widgets["plot_x_label_edit"] = plot_x_label_edit
        self.parent.widgets["plot_x_label_size_slider"] = plot_x_label_size_slider
        self.parent.widgets["plot_x_tick_rotation_slider"] = plot_x_tick_rotation_slider
        self.parent.widgets["plot_x_tick_size_slider"] = plot_x_tick_size_slider
        self.parent.widgets["plot_x_n_tick_edit"] = plot_x_n_tick_edit
        self.parent.widgets["plot_x_round_edit"] = plot_x_round_edit
        
        # --- Y PARAMS ---
        plot_y_axis_title = TitleLabel(parent=p, section='title1', text='Y axis parameters')
        plot_y_label_label = QLabel("Y label:", parent=p)
        plot_y_label_edit = QLineEdit(parent=p)
        plot_y_label_size_label = QLabel("Label size: ", parent=p)
        plot_y_label_size_slider = QSlider(parent=p)
        plot_y_tick_rotation_label = QLabel("Tick rotation: 0", parent=p)
        plot_y_tick_rotation_slider = QSlider(parent=p)
        plot_y_tick_size_label = QLabel("Tick size : ", parent=p)
        plot_y_tick_size_slider = QSlider(parent=p)
        plot_y_n_tick_label = QLabel("N ticks:", parent=p)
        plot_y_n_tick_edit = QLineEdit(parent=p)
        # plot_y_round_label = QLabel("Round:", parent=p)
        # plot_y_round_edit = QLineEdit(parent=p)
        
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
        plot_y_n_tick_edit.setValidator(QIntValidator())
        plot_y_n_tick_edit.setText(str(params.DEFAULT_FONTSIZE))
        # plot_y_round_edit.setValidator(QIntValidator())
        # plot_y_round_edit.setText(str(params.DEFAULT_ROUND))
        
        # store Y widgets
        self.parent.widgets["plot_y_label_edit"] = plot_y_label_edit
        self.parent.widgets["plot_y_label_size_slider"] = plot_y_label_size_slider
        self.parent.widgets["plot_y_tick_rotation_slider"] = plot_y_tick_rotation_slider
        self.parent.widgets["plot_y_tick_size_slider"] = plot_y_tick_size_slider
        self.parent.widgets["plot_y_n_tick_edit"] = plot_y_n_tick_edit
        # self.parent.widgets["plot_y_round_edit"] = plot_y_round_edit
        
        # --- LEGEND ---
        plot_legend_title = TitleLabel(text="Legend parameters", parent=p, section="title1")
        plot_legend_ckbox = QCheckBox(parent=p, text="Show legend")
        plot_draggable_ckbox = QCheckBox(parent=p, text="Legend draggable")
        plot_anchor_label = QLabel(parent=p, text="Anchor:")
        plot_anchor_cbbox = QComboBox(parent=p)
        plot_alpha_label = QLabel(parent=p, text="Alpha: 100")
        plot_alpha_slider = QSlider(parent=p)
        plot_legend_x_pos_label = QLabel(parent=p, text="X position:")
        plot_legend_x_pos_slider = QSlider(parent=p)
        plot_legend_y_pos_label = QLabel(parent=p, text="Y position:")
        plot_legend_y_pos_slider = QSlider(parent=p)
        plot_legend_col_label = QLabel(parent=p, text="Number of columns:")
        plot_legend_col_edit = QLineEdit(parent=p)
        plot_legend_size_label = QLabel(parent=p, text="Font size: ")
        plot_legend_size_slider = QSlider(parent=p)
        
        # configure legend widgets
        plot_anchor_cbbox.addItems(params.LEGEND_POS)
        plot_anchor_cbbox.setCurrentIndex(params.LEGEND_POS.index(params.LEGEND_ANCHOR))
        plot_alpha_slider.setRange(0, 100)
        plot_alpha_slider.setOrientation(Qt.Orientation.Horizontal)
        plot_alpha_slider.setTickInterval(5)
        plot_legend_x_pos_slider.setRange(0, 100)
        plot_legend_x_pos_slider.setOrientation(Qt.Orientation.Horizontal)
        plot_legend_x_pos_slider.setTickInterval(5)
        plot_legend_y_pos_slider.setRange(0, 100)
        plot_legend_y_pos_slider.setOrientation(Qt.Orientation.Horizontal)
        plot_legend_y_pos_slider.setTickInterval(5)
        plot_legend_size_slider.setMinimum(params.MIN_FONTSIZE)
        plot_legend_size_slider.setMaximum(params.MAX_FONTSIZE)
        plot_legend_size_slider.setOrientation(Qt.Orientation.Horizontal)
        plot_legend_size_slider.setTickInterval(1)
        
        plot_alpha_slider.setValue(params.LEGEND_ALPHA)
        plot_legend_x_pos_slider.setValue(params.LEGEND_ALPHA)
        plot_legend_y_pos_slider.setValue(params.LEGEND_ALPHA)
        plot_legend_size_slider.setValue(params.DEFAULT_FONTSIZE)
        
        # store legend widgets
        self.parent.widgets["plot_legend_ckbox"] = plot_legend_ckbox
        self.parent.widgets["plot_draggable_ckbox"] = plot_draggable_ckbox
        self.parent.widgets["plot_anchor_cbbox"] = plot_anchor_cbbox
        self.parent.widgets["plot_alpha_slider"] = plot_alpha_slider
        self.parent.widgets["plot_legend_x_pos_slider"] = plot_legend_x_pos_slider
        self.parent.widgets["plot_legend_y_pos_slider"] = plot_legend_y_pos_slider
        self.parent.widgets["plot_legend_col_edit"] = plot_legend_col_edit
        self.parent.widgets["plot_legend_size_slider"] = plot_legend_size_slider
        
        # layout widgets
        layout = self.scrollable_layout
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
        layout.addWidget(plot_x_n_tick_label, 11, 0)
        layout.addWidget(plot_x_n_tick_edit, 11, 1)
        layout.addWidget(plot_x_round_label, 12, 0)
        layout.addWidget(plot_x_round_edit, 12, 1)
        
        layout.addWidget(plot_y_axis_title, 13, 0, 1, 2)
        layout.addWidget(plot_y_label_label, 14, 0)
        layout.addWidget(plot_y_label_edit, 14, 1)
        layout.addWidget(plot_y_label_size_label, 15, 0)
        layout.addWidget(plot_y_label_size_slider, 15, 1)
        layout.addWidget(plot_y_tick_rotation_label, 16, 0)
        layout.addWidget(plot_y_tick_rotation_slider, 16, 1)
        layout.addWidget(plot_y_tick_size_label, 17, 0)
        layout.addWidget(plot_y_tick_size_slider, 17, 1)
        layout.addWidget(plot_y_n_tick_label, 18, 0)
        layout.addWidget(plot_y_n_tick_edit, 18, 1)
        # layout.addWidget(plot_y_round_label, 19, 0)
        # layout.addWidget(plot_y_round_edit, 19, 1)
        
        layout.addWidget(plot_legend_title, 20, 0, 1, 2)
        layout.addWidget(plot_legend_ckbox, 21, 0)
        layout.addWidget(plot_draggable_ckbox, 22, 0)
        layout.addWidget(plot_anchor_label, 23, 0)
        layout.addWidget(plot_anchor_cbbox, 23, 1)
        layout.addWidget(plot_alpha_label, 24, 0)
        layout.addWidget(plot_alpha_slider, 24, 1)
        layout.addWidget(plot_legend_x_pos_label, 25, 0)
        layout.addWidget(plot_legend_x_pos_slider, 25, 1)
        layout.addWidget(plot_legend_y_pos_label, 26, 0)
        layout.addWidget(plot_legend_y_pos_slider, 26, 1)
        layout.addWidget(plot_legend_col_label, 27, 0)
        layout.addWidget(plot_legend_col_edit, 27, 1)
        layout.addWidget(plot_legend_size_label, 28, 0)
        layout.addWidget(plot_legend_size_slider, 28, 1)
        
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
        
        plot_legend_size_slider.valueChanged.connect(
            lambda: plot_legend_size_label.setText("Font size: " + str(plot_legend_size_slider.value()))
        )
        plot_legend_size_slider.setValue(params.DEFAULT_FONTSIZE)
        
        plot_alpha_slider.valueChanged.connect(
            lambda: plot_alpha_label.setText("Alpha: " + str(plot_alpha_slider.value()))
        )
        plot_alpha_slider.setValue(100)
        
        plot_legend_x_pos_slider.valueChanged.connect(
            lambda: plot_legend_x_pos_label.setText("X position: " + str(plot_legend_x_pos_slider.value()))
        )
        plot_legend_x_pos_slider.setValue(0)
        
        plot_legend_y_pos_slider.valueChanged.connect(
            lambda: plot_legend_y_pos_label.setText("Y position: " + str(plot_legend_y_pos_slider.value()))
        )
        plot_legend_y_pos_slider.setValue(0)
