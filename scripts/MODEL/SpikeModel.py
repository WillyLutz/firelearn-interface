import pickle
from tkinter import messagebox

from scripts import params as p
from packaging import version

class SpikeModel:

    def __init__(self,):
        self.version = p.version

        self.plot = None

        self.dataset_path = ""
        self.parent_directory = ""
        self.single_file = ""

        self.to_include = []
        self.to_exclude = []
        self.dataset = None
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
        self.vars = {}
        self.canvas = {}
        self.figures = {}
        self.targets = {}
        self.n_labels = -1
        self.max_n_labels = 24
        self.n_labels_offset = 2
        self.plot_legend = {'show legend': p.SHOW_LEGEND, 'legend anchor': p.LEGEND_ANCHOR,
                            'legend alpha': p.LEGEND_ALPHA, 'legend x pos': 0.0, 'legend y pos': 0.0,
                            'legend draggable': p.LEGEND_DRAGGABLE, 'legend ncols': p.LEGEND_NCOLS,
                            'legend fontsize': p.LEGEND_FONTSIZE, }

        self.plot_axes = {'x label': '', 'y label': 'Spike count/sample', 'x label size': p.DEFAULT_FONTSIZE,
                          'y label size': p.DEFAULT_FONTSIZE, 'n x ticks': p.DEFAULT_NTICKS,
                          'n y ticks': p.DEFAULT_NTICKS, 'x ticks rotation': p.DEFAULT_FONTROTATION,
                          'y ticks rotation': p.DEFAULT_FONTROTATION, 'x ticks size': p.DEFAULT_FONTSIZE,
                          'y ticks size': p.DEFAULT_FONTSIZE, 'round x ticks': p.DEFAULT_ROUND,
                          'round y ticks': p.DEFAULT_ROUND, 'axes font': p.DEFAULT_FONT,
                          }

        self.plot_general_settings = {'title': '', 'title font': p.DEFAULT_FONT,
                                      'title size': p.DEFAULT_FONTSIZE, 'dpi': p.DEFAULT_DPI}

        self.plot_data = {'xdata': 'None',
                          'label column': 'None',
                          'type': ['bar', 'violin']}
        
        self.spike_params = {'dead window': 0.1, 'std threshold': 5.5, 'sampling frequency': 10000, 'all_spikes_count': {},
                             'all_spikes_indices': {},}
    def load_model(self, path):
        try:
            attr_dict = pickle.load(open(path, "rb"))
            befor_load = self.n_labels
            if version.parse(attr_dict["version"]) >= version.parse(p.last_version_compatible_spike):
                # Preserve missing keys in nested dictionaries
                for key, value in self.__dict__.items():
                    if isinstance(value, dict) and key in attr_dict:
                        for sub_key, sub_value in value.items():
                            attr_dict[key].setdefault(sub_key, sub_value)
                self.__dict__.update(attr_dict)
                
                self.n_labels = befor_load
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