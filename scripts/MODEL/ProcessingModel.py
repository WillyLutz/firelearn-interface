import pickle
from tkinter import messagebox

from scripts import params
from packaging.version import Version

class ProcessingModel:

    def __init__(self):
        self.version = params.version

        self.parent_directory = ""
        self.single_file = ""
        self.save_directory = ""
        self.to_include = []
        self.to_exclude = []
        self.targets = {}
        self.n_filters = 0

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


    def load_model(self, path):
        try:
            attr_dict = pickle.load(open(path, "rb"))
            if Version(attr_dict["version"]) >= Version(params.last_version_compatible_processing):
                # Preserve missing keys in nested dictionaries
                for key, value in self.__dict__.items():
                    if isinstance(value, dict) and key in attr_dict:
                        for sub_key, sub_value in value.items():
                            attr_dict[key].setdefault(sub_key, sub_value)
                self.__dict__.update(attr_dict)
                self.version = params.version

                messagebox.showinfo("Info", f"Processing configuration correctly loaded.\nVersion {self.version}")
                return True
            else:
                messagebox.showerror("Error", f"You can not load a configuration version ({attr_dict['version']})"
                                              f" which is incompatible with the one in use ({self.version})")
                return False
        except Exception as e:
            messagebox.showerror("Error", "Error while loading processing configuration.\n\n"
                                          f"{e}")
            return False

    def save_model(self, path):
        try:
            attr_dict = self.__dict__
            pickle.dump(attr_dict, open(path, "wb"))
            messagebox.showinfo("Info", f"Processing configuration correctly saved.\nVersion {self.version}")
        except Exception as e:
            messagebox.showerror("Error", "Error while saving processing configuration.\n\n"
                                          f"{e}")




