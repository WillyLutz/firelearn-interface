import pickle
from tkinter import messagebox

from scripts import params, params as p
from packaging import version


class ConfusionModel:
    def __init__(self, ):
        self.version = p.version

        self.plot = None

        self.dataset_path = ""

        self.dataset = None
        self.training_classes = []
        self.testing_classes = []

        self.rename_targets = {}

        self.vars = {}
        self.canvas = {}
        self.figures = {}
        self.confusion_data = {"overall matrix": None, "mixed labels matrix": None, "correspondence": None}

        self.clf_path = ''
        self.clf = None

        self.plot_legend = {'show legend': p.SHOW_LEGEND, 'legend anchor': p.LEGEND_ANCHOR,
                            'legend alpha': p.LEGEND_ALPHA, 'legend x pos': 0.0, 'legend y pos': 0.0,
                            'legend draggable': p.LEGEND_DRAGGABLE, 'legend ncols': p.LEGEND_NCOLS,
                            'legend fontsize': p.LEGEND_FONTSIZE, }

        self.plot_axes = {'x label': 'The input is', 'y label': 'The input is classified as',
                          'x label size': p.DEFAULT_FONTSIZE,
                          'y label size': p.DEFAULT_FONTSIZE,  'x ticks rotation': p.DEFAULT_FONTROTATION,
                          'y ticks rotation': p.DEFAULT_FONTROTATION, 'x ticks size': p.DEFAULT_FONTSIZE,
                          'y ticks size': p.DEFAULT_FONTSIZE,'axes font': p.DEFAULT_FONT,
                          }

        self.plot_general_settings = {'title': '', 'title font': p.DEFAULT_FONT,
                                      'title size': p.DEFAULT_FONTSIZE, 'dpi': p.DEFAULT_DPI}

        self.plot_specific_settings = {"annot size": 12, "annot mode": 'percent', "annot font": p.DEFAULT_FONT,
                                       "annot only cup": 0}
        self.plot_data = { }

    def load_model(self, path):
        try:
            attr_dict = pickle.load(open(path, "rb"))
            if version.parse(attr_dict["version"]) >= version.parse(params.last_version_compatible):
                # Preserve missing keys in nested dictionaries
                for key, value in self.__dict__.items():
                    if isinstance(value, dict) and key in attr_dict:
                        for sub_key, sub_value in value.items():
                            attr_dict[key].setdefault(sub_key, sub_value)
                self.__dict__.update(attr_dict)
                messagebox.showinfo("Info", f"Analysis configuration correctly loaded.\nVersion {self.version}")
                return True
            else:
                messagebox.showerror("Error", f"You can not load a configuration version ({attr_dict['version']})"
                                              f" which is incompatible with the one in use ({self.version})")
                return False
        except Exception as e:
            messagebox.showerror("Error", "Error while loading analysis configuration.\n\n"
                                          f"{e}")
            return False

    def save_model(self, path):
        try:
            attr_dict = self.__dict__
            pickle.dump(attr_dict, open(path, "wb"))
            messagebox.showinfo("Info", f"Analysis configuration correctly saved.\nVersion {self.version}")
        except Exception as e:
            messagebox.showerror("Error", "Error while saving analysis configuration.\n\n"
                                          f"{e}")
