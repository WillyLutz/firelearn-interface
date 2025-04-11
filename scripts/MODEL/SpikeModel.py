import pickle
from tkinter import messagebox

from packaging.version import Version

from scripts import params as p, params
from packaging import version
import toml
import logging

logger = logging.getLogger("__SpikeModel__")
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
        self.plot_legend = {'show_legend': p.SHOW_LEGEND, 'legend_anchor': p.LEGEND_ANCHOR,
                            'legend_alpha': p.LEGEND_ALPHA, 'legend_x_pos': 0.0, 'legend_y_pos': 0.0,
                            'legend_draggable': p.LEGEND_DRAGGABLE, 'legend_ncols': p.LEGEND_NCOLS,
                            'legend_fontsize': p.LEGEND_FONTSIZE, }

        self.plot_axes = {'x_label': '', 'y_label': 'Spike_count/sample', 'x_label_size': p.DEFAULT_FONTSIZE,
                          'y_label_size': p.DEFAULT_FONTSIZE, 'n_x_ticks': p.DEFAULT_NTICKS,
                          'n_y_ticks': p.DEFAULT_NTICKS, 'x_ticks_rotation': p.DEFAULT_FONTROTATION,
                          'y_ticks_rotation': p.DEFAULT_FONTROTATION, 'x_ticks_size': p.DEFAULT_FONTSIZE,
                          'y_ticks_size': p.DEFAULT_FONTSIZE, 'round_x_ticks': p.DEFAULT_ROUND,
                          'round_y_ticks': p.DEFAULT_ROUND, 'axes_font': p.DEFAULT_FONT,
                          }

        self.plot_general_settings = {'title': '', 'title_font': p.DEFAULT_FONT,
                                      'title_size': p.DEFAULT_FONTSIZE, 'dpi': p.DEFAULT_DPI}

        self.plot_data = {'xdata': 'None',
                          'label_column': 'None',
                          'type': ['bar', 'violin']}
        
        self.spike_params = {'dead_window': 0.1, 'std_threshold': 5.5, 'sampling_frequency': 10000, 'all_spikes_count': {},
                             'all_spikes_indices': {},}

    def state_to_dict(self):
        """
        Convert model attributes to a dictionary.
        Modify this method if you need to convert or omit some attributes.
        """
        state = {
            "version": self.version,
            "plot": self.plot,
            "dataset_path": self.dataset_path,
            "parent_directory": self.parent_directory,
            "single_file": self.single_file,
            "to_include": self.to_include,
            "to_exclude": self.to_exclude,
            "dataset": self.dataset,
            "entries": self.entries,
            "buttons": self.buttons,
            "cbboxes": self.cbboxes,
            "vars": self.vars,
            "switches": self.switches,
            "sliders": self.sliders,
            "ckboxes": self.ckboxes,
            "textboxes": self.textboxes,
            "canvas": self.canvas,
            "figures": self.figures,
            "targets": self.targets,
            "n_labels": self.n_labels,
            "max_n_labels": self.max_n_labels,
            "n_labels_offset": self.n_labels_offset,
            "plot_legend": self.plot_legend,
            "plot_axes": self.plot_axes,
            "plot_general_settings": self.plot_general_settings,
            "plot_data": self.plot_data,
            "spike_params": self.spike_params,
        }

        # Convert None values to an acceptable TOML value (e.g., empty string)
        for key, value in state.items():
            if value is None:
                state[key] = ""

        return state

    def save_to_toml(self, file_path=r"C:\Users\wlutz\Documents\config.toml"):
        """
        Save the model state to a TOML file.
        """
        state_dict = self.state_to_dict()
        try:
            with open(file_path, "w") as f:
                toml.dump(state_dict, f)
            print(f"State saved to {file_path}")
        except Exception as e:
            print(f"Error while saving state: {e}")

    def load_model(self, path):
        try:
            attr_dict = pickle.load(open(path, "rb"))
            before_load = self.n_labels
            if Version(attr_dict["version"]) >= Version(params.last_version_compatible_processing):
                # Preserve missing keys in nested dictionaries
                for key, value in self.__dict__.items():
                    if isinstance(value, dict) and key in attr_dict:
                        for sub_key, sub_value in value.items():
                            attr_dict[key].setdefault(sub_key, sub_value)
                self.__dict__.update(attr_dict)
                self.version = params.version

                self.n_labels = before_load

                logger.debug(f"sampling freq {self.vars["sampling_frequency"]}")
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
        # self.save_to_toml()
        try:
            attr_dict = self.__dict__
            pickle.dump(attr_dict, open(path, "wb"))
            messagebox.showinfo("Info", f"Analysis configuration correctly saved.\nVersion {self.version}")
        except Exception as e:
            messagebox.showerror("Error", "Error while saving analysis configuration.\n\n"
                                          f"{e}")