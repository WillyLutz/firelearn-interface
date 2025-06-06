import pickle
import traceback

from PyQt6.QtWidgets import QMessageBox
from packaging.version import Version

from QtScripts import params as params


class SpikeDetectionModel:
    def __init__(self, controller):
        self.version = params.version
        self.controller = controller
        self.extension = '.skcfg'
        
        self.parent_directory = ""
        self.single_file_processing = ""
        self.to_include = []
        self.to_exclude = []
        self.targets = {}
        
        self.widgets_values = {}
        
        self.attr_to_load_save_ignore = ["controller", ""]
    
    def update_tableEditors(self):
        self.to_include = []
        self.to_exclude = []
        self.targets = {}
        for inc in self.widgets_values["to_include_tableedit"]:
            self.to_include.append(inc[0])
        for exc in self.widgets_values["to_exclude_tableedit"]:
            self.to_exclude.append(exc[0])
        for key, value in self.widgets_values["target_tableedit"]:
            self.targets[key] = value
    
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
                QMessageBox.information(self.controller.view, "Spike Detection Model",
                                        "Spike detection configuration correctly loaded."
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
        if not path.endswith(self.extension):
            path += self.extension
        try:
            attr_dict = self.__dict__.copy()
            for a in self.attr_to_load_save_ignore:
                if a in attr_dict.keys():
                    del attr_dict[a]
            pickle.dump(attr_dict, open(path, "wb"))
            QMessageBox.information(self.controller.view, "Info",
                                    f"Spike detection configuration correctly saved.\nVersion {self.version}")
        except Exception as e:
            error_msg = traceback.format_exc()
            QMessageBox.warning(self.controller.view, "Error", "Error while saving configuration.\n\n" + error_msg)


