import pickle
from tkinter import messagebox


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

        self.__entries = {}
        self.__cbboxes = {}
        self.__switches = {}
        self.__strvars = {}

    @property
    def targets(self):
        return self.__targets

    @targets.setter
    def targets(self, value):
        self.__targets = value

    @property
    def entries(self):
        return self.__entries

    @entries.setter
    def entries(self, value):
        self.__entries = value

    @property
    def strvars(self):
        return self.__strvars

    @strvars.setter
    def strvars(self, value):
        self.__strvars = value

    @property
    def n_filters(self):
        return self.__n_filters

    @n_filters.setter
    def n_filters(self, value):
        self.__n_filters = value

    @property
    def switches(self):
        return self.__switches

    @switches.setter
    def switches(self, value):
        self.__switches = value

    @property
    def to_include(self):
        return self.__to_include

    @to_include.setter
    def to_include(self, value):
        self.__to_include = value

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
    def single_file(self):
        return self.__single_file

    @single_file.setter
    def single_file(self, value):
        self.__single_file = value

    @property
    def cbboxes(self):
        return self.__cbboxes

    @cbboxes.setter
    def cbboxes(self, value):
        self.__cbboxes = value

    def load_model(self, path):
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
        try:
            attr_dict = self.__dict__
            pickle.dump(attr_dict, open(path, "wb"))
            messagebox.showinfo("Info", f"Processing configuration correctly saved.\nVersion {self.version}")
        except Exception as e:
            messagebox.showerror("Error", "Error while saving processing configuration.\n\n"
                                          f"{e}")




