import pickle
from tkinter import messagebox

from packaging.version import Version

from scripts import params
from packaging import version

class LearningModel:

    def __init__(self,):
        self.version = params.version
        self.full_dataset_path = ""
        self.train_dataset_path = ""
        self.train_dataset = None
        self.test_dataset_path = ""
        self.test_dataset = None
        self.save_rfc_directory = ""
        self.rfc = None
        self.enable_kfold = True
        self.kfold = 5
        self.hyperparameters_to_tune = {'n_estimators': '100, 200, 500',
                                        'criterion': 'gini, entropy, log_loss',
                                        'max_depth': 'None, 5, 10',
                                        }

        self.rfc_params_stringvar = {}

        self.entries = {}
        self.buttons = {}
        self.cbboxes = {}
        self.vars = {}
        self.switches = {}
        self.sliders = {}
        self.ckboxes = {}
        self.textboxes = {}
        self.canvas = {}
        self.figures = {}
        self.targets = []


    def load_model(self, path):
        try:
            attr_dict = pickle.load(open(path, "rb"))
            if Version(attr_dict["version"]) >= Version(params.last_version_compatible):
                # Preserve missing keys in nested dictionaries
                for key, value in self.__dict__.items():
                    if isinstance(value, dict) and key in attr_dict:
                        for sub_key, sub_value in value.items():
                            attr_dict[key].setdefault(sub_key, sub_value)
                self.__dict__.update(attr_dict)
                self.version = params.version
                messagebox.showinfo("Info", f"Learning configuration correctly loaded.\nVersion {self.version}")
                return True
            else:
                messagebox.showerror("Error", f"You can not load a configuration version ({attr_dict['version']})"
                                              f" which is incompatible with the one in use ({self.version})")
                return False
        except Exception as e:
            messagebox.showerror("Error", "Error while loading learning configuration.\n\n"
                                          f"{e}")
            return False

    def save_model(self, path):
        try:
            attr_dict = self.__dict__
            
            pickle.dump(attr_dict, open(path, "wb"))
            messagebox.showinfo("Info", f"Learning configuration correctly saved.\nVersion {self.version}")
        except Exception as e:
            messagebox.showerror("Error", "Error while saving learning configuration.\n\n"
                                          f"{e}")
