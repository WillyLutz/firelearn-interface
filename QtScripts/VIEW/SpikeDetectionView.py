from PyQt6.QtCore import QLocale
from PyQt6.QtGui import QIntValidator, QDoubleValidator
from PyQt6.QtWidgets import QApplication, QFrame, QVBoxLayout, QHBoxLayout, \
    QGridLayout, QCheckBox, QLabel, QPushButton, QLineEdit, QComboBox

from QtScripts import params
from QtScripts.WIDGETS.CustomProgressBar import CustomProgressBar
from QtScripts.WIDGETS.TableEditor import TableEditor
from QtScripts.WIDGETS.TitleLabel import TitleLabel


class SpikeDetectionView(QFrame):
    def __init__(self, app: QApplication, parent: QFrame = None, controller=None):
        super().__init__(parent=parent)
        self.app = app
        self.controller = controller
        self.parent = parent
        self.viewlayout = QVBoxLayout()
        self.parent.setLayout(self.viewlayout)
        
        self.widgets = {}
        
        self.parameters_layout = QHBoxLayout()

        self.sorter_layout = QGridLayout()
        self.detection_layout = QGridLayout()
        # self.summary = QFrame()
        
        # keys : 0 = filesorter, 1 = signal, 2 = filename
        self.tab_states = {0: 2, 1: 2, 2: 2}  # value = 0: good, 1: errors, 2: grey
        
        self.progress_bar = CustomProgressBar()
        self.progress_bar.set_task("No task running.")
        
        self.parameters_layout.addLayout(self.sorter_layout, stretch=1)
        self.parameters_layout.addLayout(self.detection_layout, stretch=1)
        self.viewlayout.addLayout(self.parameters_layout,)
        self.viewlayout.addWidget(self.progress_bar, stretch=1)
        
        self.manage_sorting_params()
        self.manage_detection_layout()
        # self.manage_filename_tab()
        # self.manage_summary()
        
    @staticmethod
    def DotDoubleValidator():
        validator = QDoubleValidator()
        validator.setLocale(QLocale("C"))  # "C" locale uses dot as decimal separator
        return validator
    
    def manage_detection_layout(self):
        detection_title = TitleLabel(parent=self, section='title1', text="Spike detection")
        detection_behead_ckbox = QCheckBox("Behead top file:", parent=self)
        detection_behead_ckbox.setChecked(True)
        detection_behead_edit = QLineEdit(parent=self)
        detection_behead_edit.setText("6")
        detection_behead_edit.setValidator(QIntValidator())
        
        detection_column_selection_ckbox = QCheckBox("Select columns:", parent=self, )
        detection_column_selection_ckbox.setChecked(False)
        detection_column_selection_edit = QLineEdit(parent=self)
        detection_column_selection_edit.setValidator(QIntValidator())
        detection_column_selection_mode_label = QLabel("mode: ", parent=self)
        detection_column_selection_metric_label = QLabel("metric: ", parent=self)
        detection_column_selection_mode_cbbox = QComboBox(self)
        detection_column_selection_mode_cbbox.addItems(["Maximum", ])
        detection_column_selection_metric_cbbox = QComboBox(self)
        detection_column_selection_metric_cbbox.addItems(["Standard deviation", ])
        
        detection_threshold_label = QLabel("Standard deviation threshold:", parent=self)
        detection_threshold_edit = QLineEdit(parent=self)
        detection_threshold_edit.setText("5.5")
        detection_threshold_edit.setValidator(self.DotDoubleValidator())
        
        detection_sampling_frequency_label = QLabel("Sampling frequency:", parent=self)
        detection_sampling_frequency_edit = QLineEdit(parent=self)
        detection_sampling_frequency_edit.setText("10000")
        detection_sampling_frequency_edit.setValidator(QIntValidator())
        
        detection_dead_window_label = QLabel("Dead window (s):", parent=self)
        detection_dead_window_edit = QLineEdit(parent=self)
        detection_dead_window_edit.setText("0.1")
        detection_dead_window_edit.setValidator(self.DotDoubleValidator())
        
        detection_exception_column_label = QLabel("Exception column:", parent=self)
        detection_exception_column_edit = QLineEdit(parent=self)
        detection_exception_column_edit.setText("Time")
        
        detection_extraction_ckbox = QCheckBox("Spike extraction:", parent=self)
        detection_extraction_ckbox.setChecked(True)
        detection_extraction_min_margin_label = QLabel("Inferior margin of extraction (s):", parent=self)
        detection_extraction_max_margin_label = QLabel("Superior margin of extraction (s):", parent=self)
        detection_extraction_min_margin_edit = QLineEdit(parent=self)
        detection_extraction_min_margin_edit.setText("0.05")
        detection_extraction_min_margin_edit.setValidator(self.DotDoubleValidator())
        detection_extraction_max_margin_edit = QLineEdit(parent=self)
        detection_extraction_max_margin_edit.setText("0.05")
        detection_extraction_max_margin_edit.setValidator(self.DotDoubleValidator())
        detection_on_edge_label = QLabel("On edge spike extraction", parent=self)
        detection_on_edge_cbbox = QComboBox(parent=self)
        detection_on_edge_cbbox.addItems(["Ignore", "Include trimmed", ])
        
        detection_unit_label = QLabel("Unit:", parent=self)
        detection_unit_edit = QLineEdit(parent=self)
        
        detection_unit_edit.setText(params.DEFAULT_DETECTION_UNITS)
        
        detection_save_label = QLabel(parent=self, text="Save processed files under:")
        detection_save_btn = QPushButton(parent=self, text="Open", )
        save_layout = QHBoxLayout()
        save_layout.addWidget(detection_save_label)
        save_layout.addWidget(detection_save_btn)
        detection_save_edit = QLineEdit(parent=self, )
        detection_save_edit.setEnabled(False)
        detection_save_edit.setEnabled(False)
        
        detection_check_btn = QPushButton("Check params", parent=self)
        detection_start_btn = QPushButton("Start detection", parent=self)
        detection_start_btn.setObjectName("StartProcessButton")

        # store
        self.widgets["detection_behead_ckbox"] = detection_behead_ckbox
        self.widgets["detection_behead_edit"] = detection_behead_edit
        self.widgets["detection_column_selection_ckbox"] = detection_column_selection_ckbox
        self.widgets["detection_column_selection_edit"] = detection_column_selection_edit
        self.widgets["detection_column_selection_mode_cbbox"] = detection_column_selection_mode_cbbox
        self.widgets["detection_column_selection_metric_cbbox"] = detection_column_selection_metric_cbbox
        self.widgets["detection_threshold_edit"] = detection_threshold_edit
        self.widgets["detection_sampling_frequency_edit"] = detection_sampling_frequency_edit
        self.widgets["detection_dead_window_edit"] = detection_dead_window_edit
        self.widgets["detection_exception_column_edit"] = detection_exception_column_edit
        self.widgets["detection_extraction_ckbox"] = detection_extraction_ckbox
        self.widgets["detection_extraction_min_margin_edit"] =  detection_extraction_min_margin_edit
        self.widgets["detection_extraction_max_margin_edit"] = detection_extraction_max_margin_edit
        self.widgets["detection_on_edge_cbbox"] = detection_on_edge_cbbox
        self.widgets["detection_save_edit"] = detection_save_edit
        self.widgets["detection_unit_edit"] = detection_unit_edit
        
        
        # layout
        self.detection_layout.addWidget(detection_title, 0, 0, 1, 3)
        self.detection_layout.addWidget(detection_behead_ckbox, 1, 0)
        self.detection_layout.addWidget(detection_behead_edit, 1, 1)
        self.detection_layout.addWidget(detection_column_selection_ckbox, 2, 0)
        self.detection_layout.addWidget(detection_column_selection_edit, 2, 1)
        self.detection_layout.addWidget(detection_column_selection_mode_label, 3, 0)
        self.detection_layout.addWidget(detection_column_selection_mode_cbbox, 3, 1)
        self.detection_layout.addWidget(detection_column_selection_metric_label, 4, 0)
        self.detection_layout.addWidget(detection_column_selection_metric_cbbox, 4, 1)
        self.detection_layout.addWidget(detection_threshold_label, 5, 0)
        self.detection_layout.addWidget(detection_threshold_edit, 5, 1)
        self.detection_layout.addWidget(detection_sampling_frequency_label, 6, 0)
        self.detection_layout.addWidget(detection_sampling_frequency_edit, 6, 1)
        self.detection_layout.addWidget(detection_dead_window_label, 7, 0)
        self.detection_layout.addWidget(detection_dead_window_edit, 7, 1)
        self.detection_layout.addWidget(detection_exception_column_label, 8, 0)
        self.detection_layout.addWidget(detection_exception_column_edit, 8, 1)
        self.detection_layout.addWidget(detection_extraction_ckbox, 9, 0)
        self.detection_layout.addWidget(detection_extraction_min_margin_label, 10, 0)
        self.detection_layout.addWidget(detection_extraction_min_margin_edit, 10, 1)
        self.detection_layout.addWidget(detection_extraction_max_margin_label, 11, 0)
        self.detection_layout.addWidget(detection_extraction_max_margin_edit, 11, 1)
        self.detection_layout.addWidget(detection_on_edge_label, 13, 0)
        self.detection_layout.addWidget(detection_on_edge_cbbox, 13, 1)
        self.detection_layout.addWidget(detection_unit_label, 14, 0)
        self.detection_layout.addWidget(detection_unit_edit, 14, 1)
        self.detection_layout.addLayout(save_layout, 15, 0)
        self.detection_layout.addWidget(detection_save_edit, 15, 1)

        self.detection_layout.addWidget(detection_check_btn, 16, 0)
        self.detection_layout.addWidget(detection_start_btn, 16, 1)
        
        # connect 
        detection_check_btn.clicked.connect(self.controller.check_parameters)
        detection_save_btn.clicked.connect(lambda: self.controller.parent_controller.parent_controller.load_path_and_update_edit(detection_save_edit, mode='getSaveFileName', extension='.csv'))
        detection_start_btn.clicked.connect(self.controller.start_detection)
        
    def manage_sorting_params(self):
        n_rows = 10
        for i in range(n_rows):
            self.sorter_layout.setRowStretch(i, 1)
        
        self.sorter_layout.setColumnStretch(0, 1)
        self.sorter_layout.setColumnStretch(1, 1)
        self.sorter_layout.setColumnStretch(2, 1)
        self.sorter_layout.setColumnStretch(3, 20)
        # ------------- WIDGETS
        sorter_title = TitleLabel(parent=self, section='title1', text='File sorter')
        
        multiple_files_ckbox = QCheckBox(parent=self, text="Sorting multiple files")
        path_to_parent_label = QLabel(parent=self, text="Path to parent directory:")
        path_to_parent_btn = QPushButton(parent=self, text="Open")
        path_to_parent_edit = QLineEdit(parent=self, )
        path_to_parent_edit.setEnabled(False)
        
        to_include_label = QLabel(parent=self, text="To include:")
        to_include_tableedit = TableEditor(parent=self, headers=["Key", ])
        
        to_exclude_label = QLabel(parent=self, text="To exclude:")
        to_exclude_tableedit = TableEditor(parent=self, headers=["Key", ])
        
        target_key_label = QLabel(parent=self, text="Targets :")
        target_tableedit = TableEditor(parent=self, headers=["Target key", "Target value"])
        
        single_file_ckbox = QCheckBox(parent=self, text="Single file processing")
        path_to_file_label = QLabel(parent=self, text="Path to file:")
        path_to_file_btn = QPushButton(parent=self, text="Open")
        path_to_file_edit = QLineEdit(parent=self, )
        path_to_file_edit.setEnabled(False)
        
        # ------------ LAYOUT
        self.sorter_layout.addWidget(sorter_title, 0, 0)
        self.sorter_layout.addWidget(multiple_files_ckbox, 1, 0)
        self.sorter_layout.addWidget(path_to_parent_label, 2, 0)
        self.sorter_layout.addWidget(path_to_parent_btn, 2, 1, 1, 2)
        self.sorter_layout.addWidget(path_to_parent_edit, 2, 3)
        
        self.sorter_layout.addWidget(to_include_label, 3, 0, )
        self.sorter_layout.addWidget(to_include_tableedit, 4, 1, 1, 4)
        self.sorter_layout.addWidget(to_exclude_label, 5, 0, )
        self.sorter_layout.addWidget(to_exclude_tableedit, 6, 1, 1, 4)
        self.sorter_layout.addWidget(target_key_label, 7, 0, )
        
        self.sorter_layout.addWidget(target_tableedit, 8, 1, 1, 4)
        
        self.sorter_layout.addWidget(single_file_ckbox, 9, 0)
        self.sorter_layout.addWidget(path_to_file_label, 10, 0)
        self.sorter_layout.addWidget(path_to_file_btn, 10, 1, 1, 2)
        self.sorter_layout.addWidget(path_to_file_edit, 10, 3)
        
        
        # ------ SAVE WIDGETS
        names = [(multiple_files_ckbox, "multiple_files_ckbox"), (path_to_parent_edit, "path_to_parent_edit"),
                 (to_include_tableedit, "to_include_tableedit"), (to_exclude_tableedit, "to_exclude_tableedit"),
                 (target_tableedit, "target_tableedit"), (single_file_ckbox, "single_file_ckbox"),
                 (path_to_file_edit, "path_to_file_edit")]
        for widget, name in names:
            self.widgets[name] = widget
        
        # ------ SIGNALS
        path_to_parent_btn.clicked.connect(self.controller.select_parent_directory)
        path_to_file_btn.clicked.connect(self.controller.select_single_file_processing)
        
    