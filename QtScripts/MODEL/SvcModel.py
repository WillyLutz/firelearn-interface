import pickle
import traceback

from PyQt6.QtWidgets import QMessageBox
from packaging.version import Version

from QtScripts import params as params


class SvcModel:
    def __init__(self, controller):
        self.version = params.version
        self.controller = controller
        self.extension = ".svcfg"
        
        self.widgets_values = {}
        self.train_dataset = None
        self.test_dataset = None
        self.svc_params = {}
        self.model_path = ""
        self.train_targets = []
        
        self.scoring_functions = ["Trust score", "Relative K-Fold CV accuracy", "K-Fold CV accuracy",
                                  "Training accuracy", "Testing accuracy"]
        
        self.hyperparameters_to_tune = {'C': '1e-3, 1e-2, 1e-1',
                                        'kernel': 'linear, poly, rbf, sigmoid',}
        
        self.attr_to_load_save_ignore = ["controller", ""]
    
    def load_model(self, path):
        try:
            attr_dict = pickle.load(open(path, "rb"))
            if Version(attr_dict["version"]) >= Version(params.last_version_compatible_learning):
                # Preserve missing keys in nested dictionaries
                for key, value in self.__dict__.items():
                    if isinstance(value, dict) and key in attr_dict:
                        for sub_key, sub_value in value.items():
                            attr_dict[key].setdefault(sub_key, sub_value)
                self.__dict__.update(attr_dict)
                self.version = params.version
                QMessageBox.information(self.controller.view, "Learning Model",
                                        "Learning configuration correctly loaded."
                                        " \nVersion {self.version}")
                return True
            else:
                QMessageBox.warning(self.controller.view, "Error",
                                    f"You can not load a configuration version ({attr_dict['version']})"
                                    f" which is incompatible with the one in use ({self.version})")
                return False
        except Exception as e:
            QMessageBox.warning(self.controller.view, "Error", "Error while loading configuration.\n\n"
                                                               f"{e}")
            return False
    
    def save_model(self, path):
        print(self.controller)
        
        if not path.endswith(self.extension):
            path += self.extension
        try:
            attr_dict = self.__dict__.copy()
            for a in self.attr_to_load_save_ignore:
                if a in attr_dict.keys():
                    del attr_dict[a]
            pickle.dump(attr_dict, open(path, "wb"))
            QMessageBox.information(self.controller.view, "Info",
                                    f"Learning configuration correctly saved.\nVersion {self.version}")
        except Exception as e:
            error_msg = traceback.format_exc()
            QMessageBox.warning(self.controller.view, "Error", "Error while saving configuration.\n\n" + error_msg)
    
    def update_comboTableEditors(self, ):
        pass