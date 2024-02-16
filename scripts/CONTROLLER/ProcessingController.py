import os
import random
import string
import time
from tkinter import filedialog, messagebox

import pandas as pd

from scripts.CONTROLLER.ProgressBar import ProgressBar
from scripts.MODEL.ProcessingModel import ProcessingModel
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from fiiireflyyy import files as ff
from fiiireflyyy import process as fp
from fiiireflyyy import logic_gates as gates

from scripts.CONTROLLER import data_processing as dpr, input_validation as ival
from scripts.CONTROLLER.MainController import MainController
from PIL import Image

from scripts.WIDGETS.ErrEntry import ErrEntry

from scripts.params import resource_path

pd.options.mode.chained_assignment = None


class ProcessingController:
    def __init__(self, view):
        self.processing_progress = None
        self.model = ProcessingModel()
        self.view = view
        self.view.controller = self  # set controller
    
    def processing(self, ):
        if self.check_params_validity():
            if all([value for key, value in self.view.step_check.items()]):
                self.update_params(self.view.switches)
                self.update_params(self.view.cbboxes)
                self.update_params(self.view.entries)
                
                local_entry = self.model.entries
                local_switch = self.model.switches
                local_cbox = self.model.cbboxes
                
                all_files = []
                if local_switch["filesorter multiple"]:
                    files = ff.get_all_files(self.model.parent_directory)
                    for file in files:
                        if all(i in file for i in self.model.to_include) and (
                                not any(e in file for e in self.model.to_exclude)):
                            all_files.append(file)
                
                if local_switch["filesorter single"]:
                    all_files.append(self.model.single_file)

                """
                section for processing bar
                """
                n_files = int(len(all_files))
                skiprow = 0
                if local_switch["signal behead"]:
                    skiprow = int(local_entry["signal behead"])
                
                example_dataframe = pd.read_csv(all_files[0], index_col=False, skiprows=skiprow)
                if local_switch["signal select columns"]:
                    n_columns = int(local_entry["signal select columns number"])
                else:
                    n_columns = int(len([col for col in example_dataframe.columns if "time" not in col.lower()]))
                    # todo : allow to specify the excepted column
                
                self.processing_progress = ProgressBar("Processing progression", app=self.view.app)
                self.processing_progress.total_tasks = self.update_number_of_tasks(n_files, n_columns)
                self.processing_progress.start()
                
                processed_files_to_make_dataset = []
                """
                end of section for processing bar
                """
                # preparation of filename
                processing_basename = []
                characters = string.ascii_letters + string.digits
                if local_switch["filename"]:
                    processing_basename.append(local_entry['filename'])
                else:
                    if local_switch["signal select columns"]:
                        processing_basename.append(f"Sel{local_cbox['signal select columns mode'].capitalize()}"
                                                   f"{local_cbox['signal select columns metric'].capitalize()}"
                                                   f"{local_entry['signal select columns number']}")
                    if local_switch["signal sampling"]:
                        processing_basename.append(f"Ds{local_entry['signal sampling']}sample{local_entry['signal sampling']}")
                    if local_switch["signal filter"]:
                        processing_basename.append(
                            f"O{local_entry['signal filter order']}{local_cbox["signal filter type"]}"
                            f"{local_entry["signal filter first frequency"]}-{local_entry["signal filter second frequency"]}"
                            f"H{local_cbox["signal filter harmonic type"]}{local_entry["signal filter harmonic frequency"]}-"
                            f"{local_entry["signal filter nth harmonic"]}")
                    if local_switch["signal fft"]:
                        processing_basename.append("signal fft")
                    if local_switch["signal merge"]:
                        processing_basename.append("avg")
                    if local_switch["signal smoothing"]:
                        processing_basename.append(f"Sm{local_entry['signal smoothing']}")
                if local_switch["filename random key"]:
                    processing_basename.append(''.join(random.choice(characters) for _ in range(5)))
                if local_switch["filename keyword"]:
                    processing_basename.append(local_entry["filename keyword"])
                if local_switch["filename timestamp"]:
                    processing_basename.append(time.strftime("%Y-%m-%d-%H-%M"))
                if not local_switch["filename random key"] and not local_switch["filename keyword"] and not \
                local_switch["filename timestamp"] \
                        and not local_switch['filename']:
                    processing_basename.append("FL_processed")
                
                # generate harmonic frequencies
                if local_cbox["signal filter harmonic type"] != "None":
                    harmonics = MainController.generate_harmonics(int(local_entry["signal filter harmonic frequency"]),
                                                                  int(local_entry["signal filter nth harmonic"]),
                                                                  local_cbox["signal filter harmonic type"])
                # file processing
                
                for file in all_files:
                    samples = []
                    if local_switch["signal behead"]:
                        self.processing_progress.update_task("Beheading raw files")
                        df = pd.read_csv(file, index_col=False, skiprows=skiprow)
                        self.processing_progress.increment_progress(1)
                    else:
                        df = pd.read_csv(file, index_col=False)
                    
                    # signal select columns
                    if local_switch["signal select columns"]:
                        self.processing_progress.update_task("Selecting columns")
                        df = dpr.top_n_electrodes(df, int(local_entry["signal select columns number"]),
                                                  "TimeStamp [µs]")
                        self.processing_progress.increment_progress(1)
                    
                    # down sampling recordings
                    
                    if local_switch["signal sampling"]:
                        self.processing_progress.update_task("Down sampling file")
                        samples = fp.equal_samples(df, int(local_entry["signal sampling"]))
                        self.processing_progress.increment_progress(1)
                    else:
                        samples.append(df)
                    n_sample = 0
                    for df_s in samples:
                        
                        df_s_fft = pd.DataFrame()
                        # filtering
                        
                        if local_switch["signal filter"]:
                            for ch in [col for col in df_s.columns if "time" not in col.lower()]:
                                self.processing_progress.update_task("Filtering")
                                df_s_ch = df_s[ch]
                                if local_cbox["signal filter type"] == 'Highpass' and local_entry[
                                    "signal filter first frequency"]:
                                    df_s_ch = dpr.butter_filter(df_s_ch, order=int(local_entry["signal filter order"]),
                                                                btype='highpass',
                                                                cut=int(local_entry["signal filter first frequency"]))
                                elif local_cbox["signal filter type"] == 'Lowpass' and local_entry[
                                    "signal filter first frequency"]:
                                    df_s_ch = dpr.butter_filter(df_s_ch, order=int(local_entry["signal filter order"]),
                                                                btype='lowpass',
                                                                cut=int(local_entry["signal filter second frequency"]))
                                elif local_cbox["signal filter type"] == 'Bandstop' and local_entry[
                                    "signal filter first frequency"] and \
                                        local_entry["signal filter second frequency"]:
                                    df_s_ch = dpr.butter_filter(df_s_ch, order=int(local_entry["signal filter order"]),
                                                                btype='bandstop',
                                                                lowcut=int(
                                                                    local_entry["signal filter first frequency"]),
                                                                highcut=int(
                                                                    local_entry["signal filter second frequency"]))
                                elif local_cbox["signal filter type"] == 'Bandpass' and local_entry[
                                    "signal filter first frequency"] and \
                                        local_entry["signal filter second frequency"]:
                                    df_s_ch = dpr.butter_filter(df_s_ch, order=int(local_entry["signal filter order"]),
                                                                btype='bandpass',
                                                                lowcut=int(
                                                                    local_entry["signal filter first frequency"]),
                                                                highcut=int(
                                                                    local_entry["signal filter second frequency"]))
                                if local_entry["signal filter harmonic frequency"]:
                                    for h in harmonics:
                                        df_s_ch = dpr.butter_filter(df_s_ch,
                                                                    order=int(local_entry["signal filter order"]),
                                                                    btype='bandstop', lowcut=h - 2,
                                                                    highcut=h + 2)
                                
                                df_s[ch] = df_s_ch  # updating the dataframe for further processing
                                self.processing_progress.increment_progress(1)
                        
                        if local_switch["signal fft"]:
                            for ch in [col for col in df_s.columns if "time" not in col.lower()]:
                                self.processing_progress.update_task("Fast Fourier Transform")
                                df_s_ch = df_s[ch]
                                # fast fourier
                                
                                clean_fft, clean_freqs = dpr.fast_fourier(df_s_ch, int(local_entry["signal fft sf"]))
                                if "Frequency [Hz]" not in df_s_fft.columns:
                                    df_s_fft["Frequency [Hz]"] = clean_freqs
                                df_s_fft[ch] = clean_fft
                                self.processing_progress.increment_progress(1)
                            df_s = df_s_fft
                        
                        # merge signal
                        if local_switch["signal merge"]:
                            self.processing_progress.update_task("Averaging signal")
                            df_s = dpr.merge_all_columns_to_mean(df_s, "Frequency [Hz]").round(3)
                            self.processing_progress.increment_progress(1)
                        
                        # smoothing signal
                        df_s_processed = pd.DataFrame()
                        if local_switch["signal smoothing"]:
                            self.processing_progress.update_task("Smoothing signal")
                            for ch in df_s.columns:
                                df_s_processed[ch] = fp.smoothing(df_s[ch], int(local_entry["signal smoothing"]),
                                                                  'mean')
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
                            df_s_processed.to_csv(
                                os.path.join(local_entry["filename save under"], '_'.join(filename_constructor)),
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
                    if local_switch["signal select columns"]:
                        processing_basename.append(f"Sel{local_cbox['signal select columns mode'].capitalize()}"
                                                   f"{local_cbox['signal select columns metric'].capitalize()}"
                                                   f"{local_entry['signal select columns number']}")
                    if local_switch["signal sampling"]:
                        processing_basename.append(f"Ds{local_entry['signal sampling']}sample{local_entry['signal sampling']}")
                    if local_switch["signal filter"]:
                        processing_basename.append(
                            f"O{local_entry['signal filter order']}{local_cbox["signal filter type"]}"
                            f"{local_entry["signal filter first frequency"]}-{local_entry["signal filter second frequency"]}"
                            f"H{local_cbox["signal filter harmonic type"]}{local_entry["signal filter harmonic frequency"]}-"
                            f"{local_entry["signal filter nth harmonic"]}")
                    if local_switch["signal fft"]:
                        processing_basename.append("signal fft")
                    if local_switch["signal merge"]:
                        processing_basename.append("avg")
                    if local_switch["signal smoothing"]:
                        processing_basename.append(f"Sm{local_entry["signal smoothing"]}")
                    if local_switch["filename random key"]:
                        processing_basename.append(''.join(random.choice(characters) for i in range(5)))
                    if local_switch["filename keyword"]:
                        processing_basename.append(local_entry["filename keyword"])
                    if local_switch["filename timestamp"]:
                        processing_basename.append(time.strftime("%Y-%m-%d-%H-%M"))
                    if not local_switch["filename random key"] and not local_switch["filename keyword"] and not \
                    local_switch["filename timestamp"]:
                        processing_basename.append("FL_processed")
                    
                    dataset.to_csv(
                        os.path.join(local_entry["filename save under"], '_'.join(processing_basename) + '.csv'),
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
            if (type(list(widgets.values())[0]) == ctk.CTkEntry or
                    type(list(widgets.values())[0]) == ErrEntry):
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
        
        n_sample = int(local_entry["signal sampling"])
        
        mea = int(local_switch["signal behead"])
        electrodes = int(local_switch["signal select columns"])
        sampling = int(local_switch["signal sampling"])
        merge = int(local_switch["signal merge"])
        smoothing = int(local_switch["signal smoothing"])
        make_dataset = int(local_switch["make dataset"])
        filtering = int(local_switch["signal filter"])
        fft = int(local_switch["signal fft"])
        
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
        filesorter_errors = []
        signal_errors = []
        filename_errors = []
        
        # -------- FILESORTER
        
        if all([self.view.switches["filesorter single"].get(), self.view.switches["filesorter multiple"].get()]):
            filesorter_errors.append("You can only chose one between Single file analysis or Multiple files analysis.")
        
        if not any([self.view.switches["filesorter single"].get(), self.view.switches["filesorter multiple"].get()]):
            filesorter_errors.append("You have to select one between Single file analysis or Multiple files analysis.", )
        
        if self.view.switches["filesorter multiple"].get():
            if not self.view.entries["filesorter multiple"].get():
                filesorter_errors.append("You have to select a parent directory to run multi-file processing.")
        
        if self.view.switches["filesorter single"].get():
            if not self.view.entries["filesorter single"].get():
                filesorter_errors.append("You have to select a file to run single file processing.")
        
        # forbidden characters
        for key, textbox in self.view.textboxes.items():
            elements = textbox.get(1.0, ctk.END)
            for element in elements:
                fcs = ival.value_has_forbidden_character(element)
                if fcs:
                    filesorter_errors.append(f"Forbidden characters in '{element}' : {fcs}")
        
        # -------- PROCESSING
        
        if self.view.switches["signal behead"].get():
            if not self.view.entries["signal behead"].get():
                signal_errors.append("You have to indicate a number of rows to behead from the raw MEA files.")
        
        if self.view.switches["signal select columns"].get():
            if not self.view.entries["signal select columns number"].get():
                signal_errors.append("You have to indicate a number of electrodes to select.")
            if self.view.cbboxes["signal select columns mode"].get() == 'None':
                signal_errors.append("You have to select a mode for electrode selection.")
            
            if self.view.cbboxes["signal select columns metric"].get() == 'None':
                signal_errors.append("You have to select a metric to use for the electrode selection.")
        
        if self.view.switches["signal sampling"].get():
            if not self.view.entries["signal sampling"].get():
                signal_errors.append("You have to indicate a number of samples.")
        
        if self.view.entries["signal filter harmonic frequency"].get():
            if self.view.entries["signal filter nth harmonic"].get():
                harmonic = int(self.view.entries["signal filter harmonic frequency"].get())
                nth = int(self.view.entries["signal filter nth harmonic"].get())
                frequency = int(self.view.entries["signal filter sf"].get())
                if harmonic * nth > frequency / 2:
                    signal_errors.append("The chosen nth harmonic is superior to half the sampling frequency."
                                  f" Please use maximum nth harmonic as nth<{int((frequency / 2) / harmonic)}")
            else:
                signal_errors.append("You have to fill both the harmonic frequency and the nth harmonics"
                              " using valid numbers.")
        
        if self.view.switches["signal filter"].get():
            if not gates.AND(
                    [self.view.entries[x].get() for x in
                     ["signal filter order", "signal filter sf", "signal filter first frequency", ]]):
                signal_errors.append("You have to fill at least the filter order, sampling "
                              "frequency, and first frequency to use the filtering function.")
            
            if self.view.entries["signal filter second frequency"].get() and (
                    self.view.cbboxes["signal filter type"].get() not in ["Bandstop", "Bandpass"]):
                signal_errors.append(f"The second frequency is not needed when using a "
                              f"{self.view.cbboxes["signal filter type"].get()} filter.")
            if self.view.cbboxes["signal filter type"].get() in ["Bandstop", "Bandpass"] and not gates.AND(
                    [self.view.entries["signal filter second frequency"].get(),
                     self.view.entries["signal filter first frequency"].get()]):
                signal_errors.append(f"Both low cut and high cut frequencies are needed when"
                              f" using a f{self.view.cbboxes["signal filter type"].get()} filter")
        
       
        
        if self.view.switches["signal fft"].get():
            if not self.view.entries["signal fft sf"].get():
                signal_errors.append("Sampling frequency rate needed to perform Fast Fourier Transform.")
        
        if self.view.switches["signal smoothing"].get():
            if not self.view.entries["signal smoothing"].get():
                signal_errors.append("Number of final values needed to perform smoothing.")
        
        # -------- FILENAME
        if self.view.entries["filename save under"].get() == '':
            filename_errors.append('You have to select a directory where to save your file.')
        elif os.path.isdir(self.view.entries["filename save under"].get()) is False:
            filename_errors.append(f'The selected path {self.view.entries["filename save under"].get()} does not exist.')
        
        if self.view.switches["filename keyword"].get():
            if not self.view.entries["filename keyword"].get():
                filename_errors.append("Keyword needed.")
        
        for key, entry in self.view.entries.items():
            if type(entry) == ErrEntry:
                if entry.error_message.get() != '':
                    filename_errors.append(f"{key} : {entry.error_message.get()}")
                    
        if self.view.switches["make dataset"].get():
            if not gates.AND(
                    [self.view.switches["signal merge"].get(), self.view.switches["filesorter multiple"].get()]):
                filename_errors.append(
                    "The 'make dataset' option is available only if 'Merge' and 'Multiple files analysis' are both True.")
        
        self.invalidate_step("filesorter") if filesorter_errors else self.validate_step("filesorter")
        self.invalidate_step("signal") if signal_errors else self.validate_step("signal")
        self.invalidate_step("filename") if filename_errors else self.validate_step("filename")

        if filesorter_errors or signal_errors or filename_errors:
            errors = [error for errors in [filesorter_errors, signal_errors, filename_errors] for error in errors]
            messagebox.showerror('Value Error', '\n'.join(errors))
            return False
        else:
            return True
    
    def validate_step(self, step):
        img = ctk.CTkImage(dark_image=Image.open(resource_path(f"data/firelearn_img/{step}_green.png")), size=(120, 120))
        self.view.image_buttons[step].configure(image=img)
        self.view.step_check[step] = 1
    
    def invalidate_step(self, step):
        img = ctk.CTkImage(dark_image=Image.open(resource_path(f"data/firelearn_img/{step}_red.png")), size=(120, 120))
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
