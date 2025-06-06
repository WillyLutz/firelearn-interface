from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import QFrame, QApplication, QVBoxLayout, QGridLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, \
    QComboBox, QCheckBox, QScrollArea, QWidget, QTextEdit

from QtScripts.WIDGETS.ComboTableEditor import ComboTableEditor
from QtScripts.WIDGETS.CustomProgressBar import CustomProgressBar
from QtScripts.WIDGETS.TitleLabel import TitleLabel


class RfcView(QFrame):
    def __init__(self, app: QApplication, parent:QFrame=None, controller=None):
        super().__init__(parent=parent)
        self.app = app
        self.controller = controller
        self.parent = parent
        self.viewlayout = QVBoxLayout()
        self.parent.setLayout(self.viewlayout)
        
        self.main_layout = QHBoxLayout()
        
        self.widgets = {}
        self.rfc_params = {}
        
        self.progress_bar = CustomProgressBar()
        self.progress_bar.set_task("No task running.")
        
        self.viewlayout.addLayout(self.main_layout, stretch=20)
        self.viewlayout.addWidget(self.progress_bar, stretch=1)
        
        self.rfc_params_layout = QVBoxLayout()
        self.train_test_layout = QGridLayout()
        self.metrics_layout = QVBoxLayout()
        
        self.main_layout.addLayout(self.rfc_params_layout, stretch=1)
        self.main_layout.addLayout(self.train_test_layout, stretch=1)
        self.main_layout.addLayout(self.metrics_layout, stretch=1)
        
        self._manage_classifier_params_layout()
        self._manage_train_test_layout()
        self._manage_metrics_layout()
        
    def _fill_hyperparams(self,):
        params_tuning_title = TitleLabel(parent=self, text="Hyperparameter auto-tuning", section="title1")
        params_tuning_label = TitleLabel(parent=self, text="Hyperparameter", section="title2")
        params_value_label = TitleLabel(parent=self, text="Hyperparameter values", section="title2")
        
        params_scrollable_layout = QGridLayout()
        n_param = 0
        for param, values in self.controller.model.hyperparameters_to_tune.items():
            param_ckbox = QCheckBox(parent=self, text=param)
            param_edit = QLineEdit(parent=self)
            param_edit.setText(values)
            
            params_scrollable_layout.addWidget(param_ckbox, n_param, 0)
            params_scrollable_layout.addWidget(param_edit, n_param, 1)
            
            self.widgets[f"hyperparam_{param}_ckbox"] = param_ckbox
            self.widgets[f"hyperparam_{param}_edit"] = param_edit
            n_param += 1
            
        # --- Setup scroll area
        scroll_area = QScrollArea()
        wrapper_widget = QWidget()
        wrapper_widget.setLayout(params_scrollable_layout)
        scroll_area.setWidget(wrapper_widget)
        scroll_area.setWidgetResizable(True)
        
        title_layout = QHBoxLayout()
        title_layout.addWidget(params_tuning_label)
        title_layout.addWidget(params_value_label)
        self.rfc_params_layout.addWidget(params_tuning_title)
        self.rfc_params_layout.addLayout(title_layout)
        self.rfc_params_layout.addWidget(scroll_area)
        

    def _manage_classifier_params_layout(self):
        params_title = TitleLabel(parent=self, text="Classifier parameters", section="title1")
        params_reload_btn = QPushButton(text="Reload default parameters", parent=self)
        
        params_scrollable_layout = QGridLayout()
        
        
        # ---- REGULAR PARAMS
        n_param=0
        for name, value in self.controller.get_fixed_default_rfc_params().items():
            params_label = QLabel(parent=self, text=name, )
            params_edit = QLineEdit(parent=self)
            params_edit.setText(str(value))
            # --- LAYOUT
            params_scrollable_layout.addWidget(params_label, n_param, 0)
            params_scrollable_layout.addWidget(params_edit, n_param, 1)
            # ----- STORE WIDGETS
            self.widgets[f"params_{name}_edit"] = params_edit
            self.rfc_params[name] = params_edit.text()
            
            n_param += 1
            
        # --- Setup scroll area
        scroll_area = QScrollArea()
        wrapper_widget = QWidget()
        wrapper_widget.setLayout(params_scrollable_layout)
        scroll_area.setWidget(wrapper_widget)
        scroll_area.setWidgetResizable(True)
        
        title_layout = QHBoxLayout()
        title_layout.addWidget(params_title)
        title_layout.addWidget(params_reload_btn)
        self.rfc_params_layout.addLayout(title_layout)
        self.rfc_params_layout.addWidget(scroll_area)
        
        self._fill_hyperparams()
        
        
        # ---- CONNECT
        params_reload_btn.clicked.connect(self.controller.reload_rfc_params)
    
    def _manage_train_test_layout(self):
        learn_title = TitleLabel(parent=self, text="Training and validation", section="title1")
        learn_load_train_btn = QPushButton(text="Load train full_dataset", parent=self)
        learn_load_train_edit = QLineEdit(parent=self)
        learn_load_train_edit.setEnabled(False)
        learn_load_test_btn = QPushButton(text="Load test full_dataset", parent=self)
        learn_load_test_edit = QLineEdit(parent=self)
        learn_load_test_edit.setEnabled(False)
        
        learn_target_column_label = QLabel(parent=self, text="Select targets column:",)
        learn_target_column_cbbox = QComboBox(parent=self)
        learn_target_column_cbbox.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        learn_combotable = ComboTableEditor(parent=self, headers=["target", ])
        
        learn_scoring_label = QLabel(parent=self, text="Scoring function:",)
        learn_scoring_cbbox = QComboBox(parent=self)
        learn_scoring_cbbox.addItems(self.controller.model.scoring_functions)
        
        learn_kfold_ckbox = QCheckBox(parent=self, text="K-fold cross validation")
        learn_kfold_ckbox.setChecked(True)
        learn_kfold_edit = QLineEdit(parent=self)
        learn_save_btn = QPushButton(text="Save classifier as", parent=self)
        learn_save_edit = QLineEdit(parent=self)
        learn_save_edit.setEnabled(False)
        
        #----LAYOUT
        self.train_test_layout.addWidget(learn_title, 0, 0, 1, 2)
        self.train_test_layout.addWidget(learn_load_train_btn, 1, 0)
        self.train_test_layout.addWidget(learn_load_train_edit, 1, 1)
        self.train_test_layout.addWidget(learn_load_test_btn, 2, 0)
        self.train_test_layout.addWidget(learn_load_test_edit, 2, 1)
        
        self.train_test_layout.addWidget(learn_target_column_label, 3, 0)
        self.train_test_layout.addWidget(learn_target_column_cbbox, 3, 1)
        self.train_test_layout.addWidget(learn_combotable, 4, 0, 1, 2)
        
        self.train_test_layout.addWidget(learn_scoring_label, 5, 0)
        self.train_test_layout.addWidget(learn_scoring_cbbox, 5, 1)
        self.train_test_layout.addWidget(learn_kfold_ckbox, 6, 0)
        self.train_test_layout.addWidget(learn_kfold_edit, 6, 1)
        self.train_test_layout.addWidget(learn_save_btn, 7, 0)
        self.train_test_layout.addWidget(learn_save_edit, 7, 1)
        
        
        
        #----STORE WIDGETS
        names = [(learn_load_train_edit, "learn_load_train_edit"),
                (learn_load_test_edit, "learn_load_test_edit"),
                 (learn_target_column_cbbox, "learn_target_column_cbbox"),
                 (learn_combotable, "learn_combotable"),
                 (learn_scoring_cbbox, "learn_scoring_cbbox"), (learn_kfold_ckbox, "learn_kfold_ckbox"),
                 (learn_kfold_edit, "learn_kfold_edit"), (learn_save_edit, "learn_save_edit"),]
        
        for widget, name in names:
            self.widgets[name] = widget
        
        #----CONNECT
        learn_load_train_btn.clicked.connect(self.controller.load_train_dataset)
        (learn_target_column_cbbox.currentIndexChanged.
         connect(lambda: self.controller.update_combotable_items("learn_combotable")))
        learn_save_btn.clicked.connect(lambda:
                                       self.controller.parent_controller.
                                       parent_controller.load_path_and_update_edit(learn_save_edit, mode='getSaveFileName',
                                                                                   extension='.rfc'))
        
        # ---- VALIDATOR
        learn_kfold_edit.setValidator(QIntValidator())
        
    
    def _manage_metrics_layout(self):
        metrics_title = TitleLabel(parent=self, text="Learning metrics", section="title1")
        
        metrics_textedit = QTextEdit(parent=self, )
        metrics_textedit.setReadOnly(True)
        
        
        metrics_export_btn = QPushButton(parent=self, text="Export metrics")
        metrics_learning_btn = QPushButton(parent=self, text="Start learning")
        metrics_learning_btn.setObjectName("StartProcessButton")
        # --- LAYOUT
        self.metrics_layout.addWidget(metrics_title,)
        self.metrics_layout.addWidget(metrics_textedit,)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(metrics_export_btn)
        btn_layout.addWidget(metrics_learning_btn)
        
        self.metrics_layout.addLayout(btn_layout)
        
        # ----- STORE WIDGETS
        self.widgets["metrics_textedit"] = metrics_textedit
        # ---- CONNECT
        metrics_export_btn.clicked.connect(self.controller.export_metrics)
        metrics_learning_btn.clicked.connect(self.controller.init_learning)
        
    