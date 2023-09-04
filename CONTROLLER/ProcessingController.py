import os
import random
import string
import time
from tkinter import filedialog, messagebox

import pandas as pd

from CONTROLLER.ProgressBar import ProgressBar
from MODEL.ProcessingModel import ProcessingModel
import customtkinter as ctk
from CONTROLLER import input_validation as ival
import tkinter as tk
from tkinter import ttk
from fiiireflyyy import files as ff
from fiiireflyyy import process as fp
from fiiireflyyy import logic_gates as gates

from CONTROLLER import data_processing as dpr
from CONTROLLER.MainController import MainController
from PIL import ImageTk, Image

pd.options.mode.chained_assignment = None

class ProcessingController:
    def __init__(self, view):
        self.processing_progress = None
        self.model = ProcessingModel()
        self.view = view
        self.view.controller = self  # set controller

    def processing(self, ):
        self.check_params_validity()
        if all([value for key, value in self.view.step_check.items()]):
            self.update_params(self.view.switches)
            self.update_params(self.view.cbboxes)
            self.update_params(self.view.entries)

            local_entry = self.model.entries
            local_switch = self.model.switches
            local_cbox = self.model.cbboxes

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
                skiprow = int(local_entry["raw mea"])

            example_dataframe = pd.read_csv(all_files[0], index_col=False, skiprows=skiprow)
            if local_switch["select electrodes"]:
                n_columns = int(local_entry["n electrodes"])
            else:
                n_columns = int(len([col for col in example_dataframe.columns if "time" not in col.lower()]))

            self.processing_progress = ProgressBar("Processing progression", app=self.view.app)
            self.processing_progress.total_tasks = self.update_number_of_tasks(n_files, n_columns)
            self.processing_progress.start()

            processed_files_to_make_dataset = []

            # preparation of filename
            processing_basename = []
            characters = string.ascii_letters + string.digits
            if local_switch["select electrodes"]:
                processing_basename.append(f"Sel{local_cbox['select electrode mode'].capitalize()}"
                                           f"{local_cbox['select electrode metric'].capitalize()}"
                                           f"{local_entry['n electrodes']}")
            if local_switch["sampling"]:
                processing_basename.append(f"Ds{local_entry['sampling']}sample{local_entry['sampling']}")
            if local_switch["filter"]:
                processing_basename.append(
                    f"O{local_entry['filter order']}{local_cbox['filter type']}"
                    f"{local_entry['first frequency']}-{local_entry['second frequency']}"
                    f"H{local_cbox['harmonic type']}{local_entry['harmonic frequency']}-"
                    f"{local_entry['nth harmonic']}")
            if local_switch["fft"]:
                processing_basename.append("FFT")
            if local_switch["merge"]:
                processing_basename.append("avg")
            if local_switch["smoothing"]:
                processing_basename.append(f"Sm{local_entry['smoothing']}")
            if local_switch["random key"]:
                processing_basename.append(''.join(random.choice(characters) for _ in range(5)))
            if local_switch["keyword"]:
                processing_basename.append(local_entry["keyword"])
            if local_switch["timestamp"]:
                processing_basename.append(time.strftime("%Y-%m-%d-%H-%M"))
            if not local_switch["random key"] and not local_switch["keyword"] and not local_switch["timestamp"]:
                processing_basename.append("FL_processed")

            harmonics = MainController.generate_harmonics(int(local_entry["harmonic frequency"]),
                                                          int(local_entry["nth harmonic"]),
                                                          local_cbox["harmonic type"])
            # file processing

            for file in all_files:
                samples = []
                if local_switch["raw mea"]:
                    self.processing_progress.update_task("Beheading raw files")
                    df = pd.read_csv(file, index_col=False, skiprows=skiprow)
                    self.processing_progress.increment_progress(1)
                else:
                    df = pd.read_csv(file, index_col=False)

                # select electrodes
                if local_switch["select electrodes"]:
                    self.processing_progress.update_task("Selecting columns")
                    df = dpr.top_n_electrodes(df, int(local_entry["n electrodes"]), "TimeStamp [µs]")
                    self.processing_progress.increment_progress(1)

                # down sampling recordings

                if local_switch["sampling"]:
                    self.processing_progress.update_task("Down sampling file")
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
                            self.processing_progress.update_task("Filtering")
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
                            if local_entry["harmonic frequency"]:
                                for h in harmonics:
                                    df_s_ch = dpr.butter_filter(df_s_ch, order=int(local_entry["filter order"]),
                                                                btype='bandstop', lowcut=h - 2,
                                                                highcut=h + 2)

                            df_s[ch] = df_s_ch  # updating the dataframe for further processing
                            self.processing_progress.increment_progress(1)

                    if local_switch["fft"]:
                        for ch in [col for col in df_s.columns if "time" not in col.lower()]:
                            self.processing_progress.update_task("Fast Fourier Transform")
                            df_s_ch = df_s[ch]
                            # fast fourier

                            clean_fft, clean_freqs = dpr.fast_fourier(df_s_ch, int(local_entry["fft sampling"]))
                            if "Frequency [Hz]" not in df_s_fft.columns:
                                df_s_fft["Frequency [Hz]"] = clean_freqs
                            df_s_fft[ch] = clean_fft
                            self.processing_progress.increment_progress(1)
                        df_s = df_s_fft

                    # merge signal
                    if local_switch["merge"]:
                        self.processing_progress.update_task("Averaging signal")
                        df_s = dpr.merge_all_columns_to_mean(df_s, "Frequency [Hz]").round(3)
                        self.processing_progress.increment_progress(1)

                    # smoothing signal
                    df_s_processed = pd.DataFrame()
                    if local_switch["smoothing"]:
                        self.processing_progress.update_task("Smoothing signal")
                        for ch in df_s.columns:
                            df_s_processed[ch] = fp.smoothing(df_s[ch], int(local_entry["smoothing"]), 'mean')
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
                        df_s_processed.to_csv(os.path.join(local_entry["save files"], '_'.join(filename_constructor)),
                                              index=False)
                    else:
                        processed_files_to_make_dataset.append((df_s_processed, file))
                    n_sample += 1
            if local_switch["make dataset"] == 1:
                first_df = processed_files_to_make_dataset[0][0]
                dataset = pd.DataFrame(columns=[str(x) for x in range(len(first_df.values))])
                targets = pd.DataFrame(columns=["label", ])
                for data in processed_files_to_make_dataset:
                    self.processing_progress.update_task("Making dataset")
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
                    processing_basename.append(f"Sel{local_cbox['select electrode mode'].capitalize()}"
                                               f"{local_cbox['select electrode metric'].capitalize()}"
                                               f"{local_entry['n electrodes']}")
                if local_switch["sampling"]:
                    processing_basename.append(f"Ds{local_entry['sampling']}sample{local_entry['sampling']}")
                if local_switch["filter"]:
                    processing_basename.append(
                        f"O{local_entry['filter order']}{local_cbox['filter type']}"
                        f"{local_entry['first frequency']}-{local_entry['second frequency']}"
                        f"H{local_cbox['harmonic type']}{local_entry['harmonic frequency']}-"
                        f"{local_entry['nth harmonic']}")
                if local_switch["fft"]:
                    processing_basename.append("FFT")
                if local_switch["merge"]:
                    processing_basename.append("avg")
                if local_switch["smoothing"]:
                    processing_basename.append(f"Sm{local_entry['smoothing']}")
                if local_switch["random key"]:
                    processing_basename.append(''.join(random.choice(characters) for i in range(5)))
                if local_switch["keyword"]:
                    processing_basename.append(local_entry["keyword"])
                if local_switch["timestamp"]:
                    processing_basename.append(time.strftime("%Y-%m-%d-%H-%M"))
                if not local_switch["random key"] and not local_switch["keyword"] and not local_switch["timestamp"]:
                    processing_basename.append("FL_processed")

                dataset.to_csv(os.path.join(local_entry["save files"], '_'.join(processing_basename) + '.csv'),
                               index=False)

    def select_save_directory(self, strvar):
        dirname = filedialog.askdirectory(mustexist=True, title="select directory")
        if type(strvar) == ctk.StringVar:
            strvar.set(dirname)
            self.model.save_directory = dirname

    def select_parent_directory(self, strvar):
        dirname = filedialog.askdirectory(mustexist=True, title="select directory")
        if type(strvar) == ctk.StringVar:
            strvar.set(dirname)
            self.model.parent_directory = dirname

    def select_single_file(self, display_in):
        filename = filedialog.askopenfilename(title="Open file",
                                              filetypes=(("Tables", "*.txt *.xls *.xlsx *.csv"),))
        if type(display_in) == ctk.StringVar:
            display_in.set(filename)
            self.model.single_file = filename

    def add_subtract_to_include(self, entry, textbox, mode='add'):
        if ival.value_has_forbidden_character(entry.get()) is False:
            entry.delete(0, ctk.END)
            return False

        to_include = entry.get()
        if to_include:
            local_include = self.model.to_include
            if mode == 'add':
                local_include.append(to_include)
            elif mode == 'subtract':
                local_include = [x for x in self.model.to_include if x != to_include]
            self.model.to_include = local_include
            MainController.update_textbox(textbox, self.model.to_include)
            entry.delete(0, ctk.END)
        else:
            messagebox.showerror("Missing Value", "You need te indicate a value to include.")

    def add_subtract_to_exclude(self, entry, textbox, mode='add'):
        if ival.value_has_forbidden_character(entry.get()) is False:
            entry.delete(0, ctk.END)
            return False
        to_exclude = entry.get()
        if to_exclude:
            local_exclude = self.model.to_exclude
            if mode == 'add':
                local_exclude.append(to_exclude)
            elif mode == 'subtract':
                local_exclude = [x for x in self.model.to_exclude if x != to_exclude]
            self.model.to_exclude = local_exclude
            MainController.update_textbox(textbox, self.model.to_exclude)
            entry.delete(0, ctk.END)
        else:
            messagebox.showerror("Missing Value", "You need te indicate a value to exclude.")

    def add_subtract_target(self, key_entry, value_entry, textbox, mode='add'):
        if ival.value_has_forbidden_character(key_entry.get()) is False:
            key_entry.delete(0, ctk.END)
            value_entry.delete(0, ctk.END)
            return False
        if ival.value_has_forbidden_character(value_entry.get()) is False:
            key_entry.delete(0, ctk.END)
            value_entry.delete(0, ctk.END)
            return False
        key = key_entry.get()
        value = value_entry.get()

        local_targets = self.model.targets
        if mode == 'add':
            if key and value:
                local_targets[key] = value
            elif key and not value:
                local_targets[key] = key
            else:
                messagebox.showerror("Missing Value", "You need to indicate the key and the value to add a target.")
        elif mode == 'subtract':
            if key:
                try:
                    del local_targets[key]
                except KeyError:
                    pass
            else:
                messagebox.showerror("Missing Value", "You need to indicate at least the key to delete a target.")
        self.model.targets = local_targets
        MainController.update_textbox(textbox, self.model.targets)
        key_entry.delete(0, ctk.END)
        value_entry.delete(0, ctk.END)

    def update_params(self, widgets: dict, ):
        local_dict = {}
        if len(widgets.items()) > 0:
            if type(list(widgets.values())[0]) == ctk.CTkSwitch:
                for key, value in widgets.items():
                    local_dict[key] = value.get()
                self.model.switches.update(local_dict)
            if type(list(widgets.values())[0]) == ctk.CTkEntry:
                for key, value in widgets.items():
                    local_dict[key] = value.get()
                self.model.entries.update(local_dict)
            if type(list(widgets.values())[0]) == tk.ttk.Combobox:
                for key, value in widgets.items():
                    local_dict[key] = value.get()
                self.model.cbboxes.update(local_dict)
            if type(list(widgets.values())[0]) == ctk.CTkTextbox:
                local_dict = {}
                for key, value in widgets.items():
                    local_dict[key] = value.get(1.0, tk.END)
                self.model.textboxes.update(local_dict)


    def update_number_of_tasks(self, n_file, n_col, ):
        local_switch = self.model.switches
        local_entry = self.model.entries

        n_sample = int(local_entry["sampling"])

        mea = int(local_switch["raw mea"])
        electrodes = int(local_switch["select electrodes"])
        sampling = int(local_switch["sampling"])
        merge = int(local_switch["merge"])
        smoothing = int(local_switch["smoothing"])
        make_dataset = int(local_switch["make dataset"])
        filtering = int(local_switch["filter"])
        fft = int(local_switch["fft"])

        file_level_tasks = mea + electrodes + sampling
        sample_level_tasks = merge + smoothing
        column_level_tasks = filtering * n_col + fft * n_col

        total_tasks = n_file * (file_level_tasks + n_sample * (sample_level_tasks + column_level_tasks))
        if make_dataset:
            total_tasks += n_file * n_sample

        return total_tasks

    def update_view_from_model(self, ):

        for key, widget in self.view.cbboxes.items():
            if widget.cget('state') == "normal":
                widget.set(self.model.cbboxes[key])
            else:
                widget.configure(state='normal')
                widget.set(self.model.cbboxes[key])
                widget.configure(state='readonly')
                pass
        for key, widget in self.view.entries.items():
            if widget.cget('state') == 'normal':
                widget.delete(0, ctk.END)
                widget.insert(0, self.model.entries[key])
            else:
                widget.configure(state='normal')
                widget.insert(0, self.model.entries[key])
                widget.configure(state='disabled')

        for key, widget in self.view.switches.items():
            if widget.cget('state') == 'normal':
                if self.model.switches[key]:
                    widget.select()
                else:
                    widget.deselect()

        for key, widget in self.view.textboxes.items():
            MainController.update_textbox(widget, self.model.textboxes[key].split("\n"))

    @staticmethod
    def modulate_entry_state_by_switch(switch, entry):
        MainController.modulate_entry_state_by_switch(switch, entry)

    def load_config(self, ):
        f = filedialog.askopenfilename(title="Open file", filetypes=(("Processing config", "*.pcfg"),))
        if f:
            if self.model.load_model(path=f):
                self.update_view_from_model()

    def save_config(self, ):
        if self.check_params_validity():
            self.update_params(self.view.entries)
            self.update_params(self.view.cbboxes)
            self.update_params(self.view.sliders)
            self.update_params(self.view.vars)
            self.update_params(self.view.switches)
            self.update_params(self.view.textboxes)

            f = filedialog.asksaveasfilename(defaultextension=".pcfg",
                                             filetypes=[("Processing", "*.pcfg"), ])
            if f:
                self.model.save_model(path=f, )

    def check_params_validity(self):
        self.view.errors = {key: [] for (key, _) in self.view.errors.items()}
        self.update_errors()
        # -------- CONTENT 1
        self.check_params_content1()
        # -------- CONTENT 2
        self.check_params_content2()
        # -------- CONTENT 3
        self.check_params_content3()
        # -------- CONTENT 4
        self.check_params_content4()
        # -------- CONTENT 5
        self.check_params_content5()

        self.update_errors()

        return True

    def validate_step(self, step):
        img = ctk.CTkImage(dark_image=Image.open(f"data/{step} green.png"), size=(120, 120))
        self.view.image_buttons[step].configure(image=img)
        self.view.step_check[step] = 1

    def invalidate_step(self, step):
        img = ctk.CTkImage(dark_image=Image.open(f"data/{step} red.png"), size=(120, 120))
        self.view.image_buttons[str(step)].configure(image=img)
        self.view.step_check[step] = 0

    def update_errors(self):
        text = ""
        for step, errors in self.view.errors.items():
            for error in errors:
                text = text + f"STEP {step} - {error}\n\n"
            if len(self.view.errors[step]) > 0:
                self.invalidate_step(step)
            else:
                self.validate_step(step)
        self.view.vars["errors"].set(text)

    def check_params_content1(self):
        def add_error(error):
            self.view.errors["1"].append(error)

        if all([self.view.switches["single file"].get(), self.view.switches["sorting"].get()]):
            add_error("You can only chose one between Single file analysis or Multiple files analysis.")

        if not any([self.view.switches["single file"].get(), self.view.switches["sorting"].get()]):
            add_error("You have to select one between Single file analysis or Multiple files analysis.", )

        if self.view.switches["sorting"].get():
            if not self.view.entries["sorting"].get():
                add_error("You have to select a parent directory to run multi-file processing.")

        if self.view.switches["single file"].get():
            if not self.view.entries["single file"].get():
                add_error("You have to select a file to run single file processing.")

        # forbidden characters
        for key, textbox in self.view.textboxes.items():
            elements = textbox.get(1.0, ctk.END)
            for element in elements:
                fcs = ival.value_has_forbidden_character(element)
                if fcs:
                    add_error(f"Forbidden characters in '{element}' : {fcs}")

    def check_params_content2(self):
        def add_error(error):
            self.view.errors["2"].append(error)

        for widget_key in ["raw mea", "n electrodes", "sampling"]:
            if ival.widget_value_is_positive_int_or_empty(self.view.entries[widget_key]) is False:
                add_error(f"entry value \'{self.view.entries[widget_key].get()}\' is not a positive integer.")

        if self.view.switches["raw mea"].get():
            if not self.view.entries["raw mea"].get():
                add_error("You have to indicate a number of rows to remove from the raw MEA files.")

        if self.view.switches["select electrodes"].get():
            if not self.view.entries["n electrodes"].get():
                add_error("You have to indicate a number of electrodes to select.")
            if self.view.cbboxes["select electrode mode"].get() == 'None':
                add_error("You have to select a mode for electrode selection.")

            if self.view.cbboxes["select electrode metric"].get() == 'None':
                add_error("You have to select a metric to use for the electrode selection.")

        if self.view.switches["sampling"].get():
            if not self.view.entries["sampling"].get():
                add_error("You have to indicate a number of samples.")



    def check_params_content3(self):
        def add_error(error):
            self.view.errors["3"].append(error)

        for widget_key in ["filter order", "filter sampling", "first frequency", "second frequency",
                           "harmonic frequency", "nth harmonic"]:
            if ival.widget_value_is_positive_int_or_empty(self.view.entries[widget_key]) is False:
                add_error(f"entry value\'{self.view.entries[widget_key].get()}\' is not a positive integer.")

        if self.view.entries["harmonic frequency"].get():
            if self.view.entries["nth harmonic"].get():
                harmonic = int(self.view.entries["harmonic frequency"].get())
                nth = int(self.view.entries["nth harmonic"].get())
                frequency = int(self.view.entries["filter sampling"].get())
                if harmonic * nth > frequency / 2:
                    add_error("The chosen nth harmonic is superior to half the sampling frequency."
                              f" Please use maximum nth harmonic as nth<{int((frequency / 2) / harmonic)}")
            else:
                add_error("You have to fill both the harmonic frequency and the nth harmonics"
                          " using valid numbers.")

        if self.view.switches["filter"].get():
            if not gates.AND(
                    [self.view.entries[x].get() for x in ["filter order", "filter sampling", "first frequency", ]]):
                add_error("You have to fill at least the filter order, sampling "
                          "frequency, and first frequency to use the filtering function.")

            if self.view.entries["second frequency"].get() and (
                    self.view.cbboxes["filter type"].get() not in ["Bandstop", "Bandpass"]):
                add_error(f"The second frequency is not needed when using a "
                          f"{self.view.cbboxes['filter type'].get()} filter.")
            if self.view.cbboxes["filter type"].get() in ["Bandstop", "Bandpass"] and not gates.AND(
                    [self.view.entries["second frequency"].get(), self.view.entries["first frequency"].get()]):
                add_error(f"Both low cut and high cut frequencies are needed when"
                          f" using a f{self.view.cbboxes['filter type'].get()} filter")

    def check_params_content4(self):
        def add_error(error):
            self.view.errors["4"].append(error)

        for widget, step in {"fft sampling": 4, "smoothing": 4}.items():
            if ival.widget_value_is_positive_int_or_empty(self.view.entries[widget]) is False:
                add_error(f"entry \'{widget}\' is not positive.")

        if self.view.switches["make dataset"].get():
            if not gates.AND([self.view.switches["merge"].get(), self.view.switches["sorting"].get()]):
                add_error(
                    "The 'make dataset' option is available only if 'Merge' and 'Multiple files analysis' are both True.")

        if self.view.switches["fft"].get():
            if not self.view.entries["fft sampling"].get():
                add_error("Sampling frequency rate needed to perform Fast Fourier Transform.")

        if self.view.switches["smoothing"].get():
            if not self.view.entries["smoothing"].get():
                add_error("Number of final values needed to perform smoothing.")

    def check_params_content5(self):
        def add_error(error):
            self.view.errors["5"].append(error)

        if self.view.entries["save files"].get() == '':
            add_error('You have to select a directory where to save your file.')
        elif os.path.isdir(self.view.entries["save files"].get()) is False:
            add_error(f'The selected path {self.view.entries["save files"].get()} does not exist.')

        if self.view.switches["keyword"].get():
            if not self.view.entries["keyword"].get():
                add_error("Keyword needed.")
            else:
                fcs = ival.value_has_forbidden_character(self.view.entries["keyword"].get())
                if fcs:
                    add_error(f"Forbidden characters in '{self.view.entries['keyword'].get()}' : {fcs}")
