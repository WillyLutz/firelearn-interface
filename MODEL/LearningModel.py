import pickle
from tkinter import messagebox

import params
import params
from packaging import version

class LearningModel:

    def __init__(self,):
        self.version = params.version
        self.dataset_path = ""
        self.save_rfc_directory = ""
        self.rfc = None

        self.rfc_params_stringvar = {}

        self.entries = {}
        self.buttons = {}
        self.cbboxes = {}
        self.vars = {}
        self.switches = {}
        self.sliders = {}
        self.checkboxes = {}
        self.textboxes = {}
        self.canvas = {}
        self.figures = {}
        self.targets = []

        self.targets = []

    def load_model(self, path):
        try:
            attr_dict = pickle.load(open(path, "rb"))
            if version.parse(attr_dict["version"]) > version.parse(params.last_version_compatible):
                self.__dict__.update(attr_dict)
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
