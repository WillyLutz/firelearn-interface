import pickle
from tkinter import messagebox

from data import params


class ProcessingModel:

    def __init__(self, main_model):
        self.main_model = main_model
        self.version = self.main_model.version

        self.__parent_directory = ""
        self.__single_file = ""
        self.__save_directory = ""
        self.__to_include = []
        self.__to_exclude = []
        self.__targets = {}
        self.__n_filters = 0

        self.__entry_params = {}
        self.__cbox_params = {}
        self.__switch_params = {}
        self.__strvar_params = {}

    @property
    def entry_params(self):
        return self.__entry_params

    @entry_params.setter
    def entry_params(self, value):
        self.__entry_params = value

    @property
    def targets(self):
        return self.__targets

    @targets.setter
    def targets(self, value):
        self.__targets = value

    @property
    def n_filters(self):
        return self.__n_filters

    @n_filters.setter
    def n_filters(self, value):
        self.__n_filters = value

    @property
    def to_include(self):
        return self.__to_include

    @to_include.setter
    def to_include(self, value):
        self.__to_include = value

    @property
    def cbox_params(self):
        return self.__cbox_params

    @cbox_params.setter
    def cbox_params(self, value):
        self.__cbox_params = value

    @property
    def parent_directory(self):
        return self.__parent_directory

    @parent_directory.setter
    def parent_directory(self, value):
        self.__parent_directory = value

    @property
    def to_exclude(self):
        return self.__to_exclude

    @to_exclude.setter
    def to_exclude(self, value):
        self.__to_exclude = value

    @property
    def save_directory(self):
        return self.__save_directory

    @save_directory.setter
    def save_directory(self, value):
        self.__save_directory = value

    @property
    def strvar_params(self):
        return self.__strvar_params

    @strvar_params.setter
    def strvar_params(self, value):
        self.__strvar_params = value

    @property
    def switch_params(self):
        return self.__switch_params

    @switch_params.setter
    def switch_params(self, value):
        self.__switch_params = value

    @property
    def single_file(self):
        return self.__single_file

    @single_file.setter
    def single_file(self, value):
        self.__single_file = value

    def load_model(self, path):
        # todo : load model
        try:
            attr_dict = pickle.load(open(path, "rb"))
            if attr_dict["version"] == self.version:
                self.__dict__.update(attr_dict)
                messagebox.showinfo("Info", f"Processing configuration correctly loaded.\nVersion {self.version}")
                return True
            else:
                messagebox.showerror("Error", f"You can not load a configuration version ({attr_dict['version']})"
                                              f" other than the current one in use ({self.version})")
                return False
        except Exception as e:
            messagebox.showerror("Error", "Error while loading processing configuration.\n\n"
                                          f"{e}")
            return False

    def save_model(self, path):
        # todo : save model
        try:
            attr_dict = self.__dict__
            pickle.dump(attr_dict, open(path, "wb"))
            messagebox.showinfo("Info", f"Processing configuration correctly saved.\nVersion {self.version}")
        except Exception as e:
            messagebox.showerror("Error", "Error while saving processing configuration.\n\n"
                                          f"{e}")




