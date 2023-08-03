import pickle
from tkinter import messagebox

import params as p


class PlotModel:

    def __init__(self,):
        self.version = p.version

        self.plot = None

        self.dataset_path = ""

        self.dataset = None

        self.vars = {}
        self.canvas = {}
        self.figures = {}
        self.targets = []
        self.n_ydata = -1
        self.plot_legend = {'show legend': p.SHOW_LEGEND, 'legend anchor': p.LEGEND_ANCHOR,
                            'legend alpha': p.LEGEND_ALPHA, 'legend x pos': 0.0, 'legend y pos': 0.0,
                            'legend draggable': p.LEGEND_DRAGGABLE, 'legend ncols': p.LEGEND_NCOLS,
                            'legend fontsize': p.LEGEND_FONTSIZE, }

        self.plot_axes = {'x label': '', 'y label': '', 'x label size': p.DEFAULT_FONTSIZE,
                          'y label size': p.DEFAULT_FONTSIZE, 'n x ticks': p.DEFAULT_NTICKS,
                          'n y ticks': p.DEFAULT_NTICKS, 'x ticks rotation': p.DEFAULT_FONTROTATION,
                          'y ticks rotation': p.DEFAULT_FONTROTATION, 'x ticks size': p.DEFAULT_FONTSIZE,
                          'y ticks size': p.DEFAULT_FONTSIZE, 'round x ticks': p.DEFAULT_ROUND,
                          'round y ticks': p.DEFAULT_ROUND, 'axes font': p.DEFAULT_FONT,
                          '3D x rotation': 0, '3D y rotation': 0, '3D z rotation': 0,
                          }

        self.plot_general_settings = {'title': '', 'title font': p.DEFAULT_FONT,
                                      'title size': p.DEFAULT_FONTSIZE, 'dpi': p.DEFAULT_DPI}

        self.plot_data = {'xdata': 'None', 'ellipsis': False, 'ellipsis alpha': p.DEFAULT_ALPHA,
                          'label column': 'None',}
    def load_model(self, path):
        try:
            attr_dict = pickle.load(open(path, "rb"))
            if attr_dict["version"] == self.version:
                self.__dict__.update(attr_dict)
                messagebox.showinfo("Info", f"Analysis configuration correctly loaded.\nVersion {self.version}")
                return True
            else:
                messagebox.showerror("Error", f"You can not load a configuration version ({attr_dict['version']})"
                                              f" other than the current one in use ({self.version})")
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