import os
import random
import string
import time
from tkinter import filedialog, messagebox

import pandas as pd

from CONTROLLER.ProgressBar import ProgressBar
from VIEW.ProcessingView import ProcessingView
from MODEL.ProcessingModel import ProcessingModel
import customtkinter as ctk
from CONTROLLER import input_validation as ival
import tkinter as tk
from tkinter import ttk
from fiiireflyyy import firefiles as ff
from fiiireflyyy import fireprocess as fp
from fiiireflyyy import logic_gates as gates

from CONTROLLER import data_processing as dpr



class ProcessingController:
    def __init__(self, main_controller, model: ProcessingModel, view: ProcessingView, ):
        self.processing_progress = None
        self.model = model
        self.view = view
        self.main_controller = main_controller

    def processing(self, switch_widgets, cbox_widgets, entry_widgets):
        if self.check_params_validity(switch_widgets, entry_widgets):
            self.update_params(switch_widgets)
            self.update_params(cbox_widgets)
            self.update_params(entry_widgets)

            local_entry = self.model.entry_params
            local_switch = self.model.switch_params
            local_cbox = self.model.cbox_params

            all_files = []
            if local_switch["sorting"]:
                files = ff.get_all_files(self.model.parent_directory)
                for file in files:
                    if all(i in file for i in self.model.to_include) and (
                            not any(e in file for e in self.model.to_exclude)):
                        all_files.append(file)

            if local_switch["single file"]:
                all_files.append(self.model.single_file)

            n_files = int(len(all_files))
            skiprow = 0
            if local_switch["raw mea"]:
                skiprow = int(local_entry["info header"])

            example_dataframe = pd.read_csv(all_files[0], index_col=False, skiprows=skiprow)
            if local_switch["select electrodes"]:
                n_columns = int(local_entry["n electrodes"])
            else:
                n_columns = int(len([col for col in example_dataframe.columns if "time" not in col.lower()]))

            self.processing_progress = ProgressBar("Processing progression", app=self.view.app)
            self.processing_progress.daemon = True
            self.processing_progress.total_tasks = self.update_number_of_tasks(n_files, n_columns)
            self.processing_progress.start()

            processed_files_to_make_dataset = []

            # preparation of filename
            processing_basename = []
            characters = string.ascii_letters + string.digits
            if local_switch["select electrodes"]:
                processing_basename.append(f"Sel{local_cbox['mode electrode'].capitalize()}"
                                           f"{local_cbox['metric electrode'].capitalize()}"
                                           f"{local_entry['n electrodes']}")
            if local_switch["sampling"]:
                processing_basename.append(f"Ds{local_entry['sampling']}sample{local_entry['sampling']}")
            if local_switch["filter"]:
                processing_basename.append(
                    f"O{local_entry['filter order']}{local_cbox['filter type']}"
                    f"{local_entry['first frequency']}-{local_entry['second frequency']}"
                    f"H{local_cbox['harmonic type']}{local_entry['harmonic']}-"
                    f"{local_entry['nth harmonic']}")
            if local_switch["fft"]:
                processing_basename.append("FFT")
            if local_switch["average"]:
                processing_basename.append("avg")
            if local_switch["smoothing"]:
                processing_basename.append(f"Sm{local_entry['n smoothing']}")
            if local_switch["random key"]:
                processing_basename.append(''.join(random.choice(characters) for _ in range(5)))
            if local_switch["keyword"]:
                processing_basename.append(local_entry["keyword"])
            if local_switch["timestamp"]:
                processing_basename.append(time.strftime("%Y-%m-%d-%H-%M"))
            if not local_switch["random key"] and not local_switch["keyword"] and not local_switch["timestamp"]:
                processing_basename.append("FL_processed")

            harmonics = self.main_controller.generate_harmonics(int(local_entry["harmonic"]),
                                                                int(local_entry["nth harmonic"]),
                                                                local_cbox["harmonic type"])
            # file processing
            for file in all_files:
                samples = []
                if local_switch["raw mea"]:
                    self.processing_progress.update_progress("Beheading raw files")
                    df = pd.read_csv(file, index_col=False, skiprows=skiprow)
                    self.processing_progress.increment_progress(1)
                else:
                    df = pd.read_csv(file, index_col=False)

                # select electrodes
                if local_switch["select electrodes"]:
                    self.processing_progress.update_progress("Selecting columns")
                    df = dpr.top_n_electrodes(df, int(local_entry["n electrodes"]), "TimeStamp")
                    self.processing_progress.increment_progress(1)

                # down sampling recordings

                if local_switch["sampling"]:
                    self.processing_progress.update_progress("Down sampling file")
                    samples = fp.equal_samples(df, int(local_entry["sampling"]))
                    self.processing_progress.increment_progress(1)
                else:
                    samples.append(df)
                n_sample = 0
                for df_s in samples:

                    df_s_fft = pd.DataFrame()
                    # filtering

                    if local_switch["filter"]:
                        for ch in [col for col in df_s.columns if "time" not in col.lower()]:
                            self.processing_progress.update_progress("Filtering")
                            df_s_ch = df_s[ch]
                            if local_cbox["filter type"] == 'Highpass' and local_entry["first frequency"]:
                                df_s_ch = dpr.butter_filter(df_s_ch, order=int(local_entry["filter order"]),
                                                            btype='highpass',
                                                            cut=int(local_entry["first frequency"]))
                            elif local_cbox["filter type"] == 'Lowpass' and local_entry[
                                "first frequency"]:
                                df_s_ch = dpr.butter_filter(df_s_ch, order=int(local_entry["filter order"]),
                                                            btype='lowpass',
                                                            cut=int(local_entry["second frequency"]))
                            elif local_cbox["filter type"] == 'Bandstop' and local_entry[
                                "first frequency"] and \
                                    local_entry["second frequency"]:
                                df_s_ch = dpr.butter_filter(df_s_ch, order=int(local_entry["filter order"]),
                                                            btype='bandstop',
                                                            lowcut=int(local_entry["first frequency"]),
                                                            highcut=int(local_entry["second frequency"]))
                            elif local_cbox["filter type"] == 'Bandpass' and local_entry[
                                "first frequency"] and \
                                    local_entry["second frequency"]:
                                df_s_ch = dpr.butter_filter(df_s_ch, order=int(local_entry["filter order"]),
                                                            btype='bandpass',
                                                            lowcut=int(local_entry["first frequency"]),
                                                            highcut=int(local_entry["second frequency"]))
                            if local_entry["harmonic"]:
                                for h in harmonics:
                                    df_s_ch = dpr.butter_filter(df_s_ch, order=int(local_entry["filter order"]),
                                                                btype='bandstop', lowcut=h - 2,
                                                                highcut=h + 2)

                            df_s[ch] = df_s_ch  # updating the dataframe for further processing
                            self.processing_progress.increment_progress(1)

                    if local_switch["fft"]:
                        for ch in [col for col in df_s.columns if "time" not in col.lower()]:
                            self.processing_progress.update_progress("Fast Fourier Transform")
                            df_s_ch = df_s[ch]
                            # fast fourier

                            clean_fft, clean_freqs = dpr.fast_fourier(df_s_ch, int(local_entry["sampling fft"]))
                            if "Frequency [Hz]" not in df_s_fft.columns:
                                df_s_fft["Frequency [Hz]"] = clean_freqs
                            df_s_fft[ch] = clean_fft
                            self.processing_progress.increment_progress(1)
                        df_s = df_s_fft

                    # average signal
                    if local_switch["average"]:
                        self.processing_progress.update_progress("Averaging signal")
                        df_s = dpr.merge_all_columns_to_mean(df_s, "Frequency [Hz]").round(3)
                        self.processing_progress.increment_progress(1)

                    # smoothing signal
                    df_s_processed = pd.DataFrame()
                    if local_switch["smoothing"]:
                        self.processing_progress.update_progress("Smoothing signal")
                        for ch in df_s.columns:
                            df_s_processed[ch] = fp.smoothing(df_s[ch], int(local_entry["n smoothing"]), 'mean')
                        self.processing_progress.increment_progress(1)
                    else:
                        df_s_processed = df_s

                    # saving file
                    filename_constructor = []
                    filename = os.path.basename(file).split(".")[0]

                    filename_constructor.append(filename)
                    filename_constructor.append("_".join(processing_basename))
                    filename_constructor.append(".csv")

                    if local_switch["make dataset"] == 0:
                        df_s_processed.to_csv(os.path.join(local_entry["save under"], '_'.join(filename_constructor)),
                                              index=False)
                    else:
                        processed_files_to_make_dataset.append((df_s_processed, file))
                    n_sample += 1
            if local_switch["make dataset"] == 1:
                first_df = processed_files_to_make_dataset[0][0]
                dataset = pd.DataFrame(columns=[str(x) for x in range(len(first_df.values))])
                targets = pd.DataFrame(columns=["label", ])
                for data in processed_files_to_make_dataset:
                    self.processing_progress.update_progress("Making dataset")
                    dataframe = data[0]
                    file = data[1]
                    for col in dataframe.columns:
                        if "time" not in col.lower() and "frequency" not in col.lower():
                            signal = dataframe[col].values
                            dataset.loc[len(dataset)] = signal
                            for key_target, value_target in self.model.targets.items():
                                if key_target in file:
                                    targets.loc[len(targets)] = value_target

                    self.processing_progress.increment_progress(1)
                dataset["label"] = targets["label"]

                # preparation of filename
                processing_basename = ["DATASET", ]
                characters = string.ascii_letters + string.digits
                if local_switch["select electrodes"]:
                    processing_basename.append(f"Sel{local_cbox['mode electrode'].capitalize()}"
                                               f"{local_cbox['metric electrode'].capitalize()}"
                                               f"{local_entry['n electrodes']}")
                if local_switch["sampling"]:
                    processing_basename.append(f"Ds{local_entry['sampling']}sample{local_entry['sampling']}")
                if local_switch["filter"]:
                    processing_basename.append(
                        f"O{local_entry['filter order']}{local_cbox['filter type']}"
                        f"{local_entry['first frequency']}-{local_entry['second frequency']}"
                        f"H{local_cbox['harmonic type']}{local_entry['harmonic']}-"
                        f"{local_entry['nth harmonic']}")
                if local_switch["fft"]:
                    processing_basename.append("FFT")
                if local_switch["average"]:
                    processing_basename.append("avg")
                if local_switch["smoothing"]:
                    processing_basename.append(f"Sm{local_entry['n smoothing']}")
                if local_switch["random key"]:
                    processing_basename.append(''.join(random.choice(characters) for i in range(5)))
                if local_switch["keyword"]:
                    processing_basename.append(local_entry["keyword"])
                if local_switch["timestamp"]:
                    processing_basename.append(time.strftime("%Y-%m-%d-%H-%M"))
                if not local_switch["random key"] and not local_switch["keyword"] and not local_switch["timestamp"]:
                    processing_basename.append("FL_processed")

                dataset.to_csv(os.path.join(local_entry["save under"], '_'.join(processing_basename) + '.csv'),
                               index=False)

    def select_save_directory(self, strvar):
        dirname = self.main_controller.open_filedialog(mode='directory')
        if type(strvar) == ctk.StringVar:
            strvar.set(dirname)
            self.model.save_directory = dirname

    def select_parent_directory(self, strvar):
        dirname = self.main_controller.open_filedialog(mode='directory')
        if type(strvar) == ctk.StringVar:
            strvar.set(dirname)
            self.model.parent_directory = dirname

    def select_single_file(self, display_in):
        filename = self.main_controller.open_filedialog(mode='file')
        if type(display_in) == ctk.StringVar:
            display_in.set(filename)
            self.model.single_file = filename

    def add_subtract_to_include(self, entry, textbox, mode='add'):
        if ival.widget_value_has_forbidden_character(entry) is False:
            entry.delete(0, ctk.END)
            return False

        to_include = entry.get()
        local_include = self.model.to_include
        if mode == 'add':
            local_include.append(to_include)
        elif mode == 'subtract':
            local_include = [x for x in self.model.to_include if x != to_include]
        self.model.to_include = local_include
        self.main_controller.update_textbox(textbox, self.model.to_include)
        entry.delete(0, ctk.END)

    def add_subtract_to_exclude(self, entry, textbox, mode='add'):
        if ival.widget_value_has_forbidden_character(entry) is False:
            entry.delete(0, ctk.END)
            return False
        to_exclude = entry.get()
        local_exclude = self.model.to_exclude
        if mode == 'add':
            local_exclude.append(to_exclude)
        elif mode == 'subtract':
            local_exclude = [x for x in self.model.to_exclude if x != to_exclude]
        self.model.to_exclude = local_exclude
        self.main_controller.update_textbox(textbox, self.model.to_exclude)
        entry.delete(0, ctk.END)

    def add_subtract_target(self, key_entry, value_entry, textbox, mode='add'):  # todo : to processing controller
        if ival.widget_value_has_forbidden_character(key_entry) is False:
            key_entry.delete(0, ctk.END)
            value_entry.delete(0, ctk.END)
            return False
        if ival.widget_value_has_forbidden_character(value_entry) is False:
            key_entry.delete(0, ctk.END)
            value_entry.delete(0, ctk.END)
            return False
        key = key_entry.get()
        value = value_entry.get()
        local_targets = self.model.targets
        if mode == 'add':
            if key and value:
                local_targets[key] = value
        elif mode == 'subtract':
            if key:
                try:
                    del local_targets[key]
                except KeyError:
                    pass
        self.model.targets = local_targets
        self.main_controller.update_textbox(textbox, self.model.targets)
        key_entry.delete(0, ctk.END)
        value_entry.delete(0, ctk.END)

    def update_params(self, widgets: dict, ):
        local_dict = {}
        for key, value in widgets.items():
            local_dict[key] = value.get()
        if type(list(widgets.values())[0]) == ctk.CTkSwitch:
            self.model.switch_params.update(local_dict)
        if type(list(widgets.values())[0]) == ctk.CTkEntry:
            self.model.entry_params.update(local_dict)
        if type(list(widgets.values())[0]) == tk.ttk.Combobox:
            self.model.cbox_params.update(local_dict)

    @staticmethod
    def check_params_validity(switches, entries):

        if switches["make dataset"].get():
            if not ival.AND([switches["merge"].get(), switches["sorting"].get()]):
                messagebox.showerror(title="Params validity", message="The 'make dataset' option is available only if "
                                                                      "'Merge' and 'Multiple files analysis' are both True.", )
            return False

        if all([switches["single file"].get(), switches["sorting"].get()]):
            messagebox.showerror(title="Params validity", message="You can only chose one between Single file "
                                                                  "analysis or Multiple files analysis.", )
            return False
        if not any([switches["single file"].get(), switches["sorting"].get()]):
            messagebox.showerror(title="Params validity", message="You have to select one between Single file "
                                                                  "analysis or Multiple files analysis.", )
            return False

        # valid number format
        for widget in ["raw mea", "n electrodes", "sampling", "filter order", "filter sampling", "first frequency",
                       "second frequency", "harmonic", "nth harmonic", "fft sampling", "smoothing"]:
            if ival.widget_value_is_positive_int_or_empty(entries[widget]) is False:
                return False

        # correct values
        if entries["harmonic"].get():
            if entries["nth harmonic"].get():
                harmonic = int(entries["harmonic"].get())
                nth = int(entries["nth harmonic"].get())
                frequency = int(entries["filter fs"].get())
                if harmonic * nth > frequency / 2:
                    messagebox.showerror("Value Error",
                                         "The chosen nth harmonic is superior to half the sampling frequency."
                                         f" Please use maximum nth harmonic as nth<{int((frequency / 2) / harmonic)}")
                    return False
            else:
                messagebox.showerror("Value Error", "You have to fill both the harmonic frequency and the nth harmonics"
                                                    " using valid numbers.")
                return False

        # forbidden characters
        if ival.widget_value_has_forbidden_character(entries["keyword"]) is False:
            return False

        # invalid paths
        if entries["save under"].get() == '':
            messagebox.showwarning('Path warning', 'You have to select a directory where to save your file(n_sample).')
            return False
        elif os.path.isdir(entries["save under"].get()) is False:
            messagebox.showerror('Path error', f'The selected path {entries["save under"].get()} does not exist.')
            return False

        for switch in switches:
            if switch == "sorting":
                if not entries["sorting"]:
                    messagebox.showerror("Missing Value", "You have to select a parent directory to run multi-file processing.")
                    return False

            if switch == "single file":
                if not entries["single file"]:
                    messagebox.showerror("Missing Value", "You have to select a file to run single file processing.")
                    return False

            if switch == "raw mea":
                if not entries["raw mea"]:
                    messagebox.showerror("Missing Value", "You have to indicate a number of rows to remove from the raw MEA files.")
                    return False

            if switch == "select electrodes":
                if not entries["n electrodes"]:
                    messagebox.showerror("Missing Value", "You have to indicate a number of electrodes to keep.")
                    return False

            if switch == "sampling":
                if not entries["sampling"]:
                    messagebox.showerror("Missing Value", "You have to indicate a number of samples.")
                    return False

            if switch == "filter":
                if not ival.AND([entries[x] for x in ["filter order", "filter sampling", "first frequency",]]):
                    messagebox.showerror("Missing Value", "You have to fill at least the filter order, sampling "
                                                          "frequency, and first frequency to use the filtering function.")
                    return False
                # todo : check f2 depending on the filter type
        # todo : check that all entries are filled if switch is on
        return True

    def update_number_of_tasks(self, n_file, n_col, ):
        local_switch = self.model.switch_params
        local_entry = self.model.entry_params

        n_sample = int(local_entry["sampling"])

        mea = int(local_switch["raw mea"])
        electrodes = int(local_switch["select electrodes"])
        sampling = int(local_switch["sampling"])
        average = int(local_switch["average"])
        smoothing = int(local_switch["smoothing"])
        make_dataset = int(local_switch["make dataset"])
        filtering = int(local_switch["filter"])
        fft = int(local_switch["fft"])

        file_level_tasks = mea + electrodes + sampling
        sample_level_tasks = average + smoothing
        column_level_tasks = filtering * n_col + fft * n_col

        total_tasks = n_file * (file_level_tasks + n_sample * (sample_level_tasks + column_level_tasks))
        if make_dataset:
            total_tasks += n_file * n_sample

        return total_tasks

    def save_model(self, switch_widgets, cbox_widgets, entry_widgets, textbox_widget):
        if self.check_params_validity(switch_widgets, entry_widgets):
            self.update_params(switch_widgets)
            self.update_params(cbox_widgets)
            self.update_params(entry_widgets)

            f = filedialog.asksaveasfilename(defaultextension=".mdl", filetypes=[("Models", "*.mdl"), ])
            self.model.save_model(path=f, )

    def load_model(self, switch_widgets, cbox_widgets, entry_widgets, textbox_widgets):
        f = filedialog.askopenfilename(title="Open file", filetypes=(("Model", "*.mdl"),))
        if f:
            if self.model.load_model(path=f):
                self.update_view_from_model(switch_widgets, cbox_widgets, entry_widgets, textbox_widgets)

    def update_view_from_model(self, switch_widgets, cbox_widgets, entry_widgets,
                               textbox_widgets):
        for key, widget in switch_widgets.items():
            if self.model.switch_params[key] == 1:
                if widget.get() == 1:
                    pass
                else:
                    widget.toggle()
        for key, widget in cbox_widgets.items():
            if widget.cget('state') == "normal":
                widget.set(self.model.cbox_params[key])
            else:
                widget.configure(state='normal')
                widget.set(self.model.cbox_params[key])
                widget.configure(state='disabled')
                pass
        for key, widget in entry_widgets.items():
            if widget.cget('state') == 'normal':
                widget.delete(0, ctk.END)
                widget.insert(0, self.model.entry_params[key])
            else:
                widget.configure(state='normal')
                widget.insert(0, self.model.entry_params[key])
                widget.configure(state='disabled')

        self.main_controller.update_textbox(textbox_widgets["to include"], self.model.to_include)
        self.main_controller.update_textbox(textbox_widgets["to exclude"], self.model.to_exclude)
        self.main_controller.update_textbox(textbox_widgets["targets"], self.model.targets)
