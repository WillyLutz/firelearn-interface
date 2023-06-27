import pickle
from tkinter import messagebox

from data import params


class LearningModel:

    def __init__(self, main_model):
        self.main_model = main_model
        self.version = self.main_model.version
        self.dataset_path = ""
        self.save_rfc_directory = ""
        self.rfc = None  # todo : change it to Clftester ?

        self.entries = {}
        self.switches = {}
        self.cbboxes = {}
        self.checkboxes = {}
        self.strvars = {}
        self.textboxes = {}
        self.checkvar = {}

        self.targets = []

    def load_model(self, path):
        try:
            attr_dict = pickle.load(open(path, "rb"))
            if attr_dict["version"] == self.version:
                self.__dict__.update(attr_dict)
                messagebox.showinfo("Info", f"Learning configuration correctly loaded.\nVersion {self.version}")
                return True
            else:
                messagebox.showerror("Error", f"You can not load a configuration version ({attr_dict['version']})"
                                              f" other than the current one in use ({self.version})")
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
            messagebox.showerror("Error", "Error while saving processing configuration.\n\n"
                                          f"{e}")
