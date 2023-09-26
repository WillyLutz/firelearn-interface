import pickle
from tkinter import messagebox

import params
import params as p
from packaging import version

class FeatureImportanceModel:

    def __init__(self,):
        self.version = p.version

        self.clf = None

        self.plot = None

        self.dataset_paths = {}

        self.vars = {}
        self.canvas = {}
        self.figures = {}
        self.targets = []
        #
        self.plot_legend = {'legend anchor': p.LEGEND_ANCHOR,
                            'legend alpha': p.LEGEND_ALPHA, 'legend x pos': 0.0, 'legend y pos': 0.0,
                            'legend draggable': p.LEGEND_DRAGGABLE, 'legend ncols': p.LEGEND_NCOLS,
                            'legend fontsize': p.LEGEND_FONTSIZE, }

        self.plot_axes = {'x label': '', 'y label': '', 'x label size': p.DEFAULT_FONTSIZE,
                          'y label size': p.DEFAULT_FONTSIZE, 'n x ticks': p.DEFAULT_NTICKS,
                          'n y ticks': p.DEFAULT_NTICKS, 'x ticks rotation': p.DEFAULT_FONTROTATION,
                          'y ticks rotation': p.DEFAULT_FONTROTATION, 'x ticks size': p.DEFAULT_FONTSIZE,
                          'y ticks size': p.DEFAULT_FONTSIZE, 'round x ticks': p.DEFAULT_ROUND,
                          'round y ticks': p.DEFAULT_ROUND, 'axes font': p.DEFAULT_FONT,
                          }

        self.plot_general_settings = {'title': '', 'title font': p.DEFAULT_FONT,
                                      'title size': p.DEFAULT_FONTSIZE, 'dpi': p.DEFAULT_DPI,
                                      'alpha': p.DEFAULT_ALPHA, 'alpha fill': p.DEFAULT_FILLALPHA,
                                      'fill': 'None', 'linestyle': p.DEFAULT_LINESTYLE,
                                      'color': 'green', 'clf type': 'Classifier type:',
                                      'linewidth': p.DEFAULT_LINEWIDTH, 'load clf': '',}

    def load_model(self, path):
        try:
            attr_dict = pickle.load(open(path, "rb"))
            if version.parse(attr_dict["version"]) > version.parse(params.last_version_compatible):
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