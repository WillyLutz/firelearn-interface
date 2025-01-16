import os
import random
import string
import time
from tkinter import filedialog, messagebox

import numpy as np
import pandas as pd
from markdown.extensions.extra import extensions

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
                self.update_params(self.view.cbboxes)
                self.update_params(self.view.entries)
                self.update_params(self.view.ckboxes)
                self.update_params(self.view.vars)
                
                local_vars = self.model.vars
                local_cbox = self.model.cbboxes
                
                all_files = []
                if local_vars['filesorter multiple']:
                    files = ff.get_all_files(self.model.parent_directory)
                    for file in files:
                        if all(i in file for i in self.model.to_include) and (
                                not any(e in file for e in self.model.to_exclude)):
                            all_files.append(file)
                
                if local_vars['filesorter single']:
                    all_files.append(self.model.single_file)

                """
                section for processing bar
                """
                n_files = int(len(all_files))
                skiprow = 0
                if local_vars['signal ckbox behead']:
                    skiprow = int(local_vars['signal behead'])
                
                example_dataframe = pd.read_csv(all_files[0], index_col=False, skiprows=skiprow)
                if local_vars['signal select columns ckbox']:
                    n_columns = int(local_vars['signal select columns number'])
                else:
                    n_columns = int(len([col for col in example_dataframe.columns if self.model.vars["except column"] not in col]))
                
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
                if local_vars['filename filename']:
                    processing_basename.append(local_vars['filename filename'])
                else:
                    if local_vars['signal select columns ckbox']:
                        processing_basename.append(f"Sel{local_vars['signal select columns mode'].capitalize()}"
                                                   f"{local_vars['signal select columns metric'].capitalize()}"
                                                   f"{local_vars['signal select columns number']}")
                    if local_vars['signal sampling ckbox']:
                        processing_basename.append(f"Ds{local_vars['signal sampling']}")
                    if local_vars['signal filter']:
                        processing_basename.append(
                            f"O{local_vars['signal filter order']}{local_vars['signal filter type']}"
                            f"{local_vars['signal filter first cut']}-{local_vars['signal filter second cut']}"
                            f"H{local_vars['signal harmonics type']}{local_vars['signal filter harmonic frequency']}-"
                            f"{local_vars['signal filter nth harmonic']}")
                    if local_vars['signal fft']:
                        processing_basename.append("signal fft")
                    if local_vars['signal average']:
                        processing_basename.append("avg")
                    if local_vars['signal interpolation']:
                        processing_basename.append(f"Sm{local_vars['signal interpolation']}")
                if local_vars['filename random key']:
                    processing_basename.append(''.join(random.choice(characters) for _ in range(5)))
                if local_vars['filename keyword ckbox']:
                    processing_basename.append(local_vars['filename keyword'])
                if local_vars['filename timestamp']:
                    processing_basename.append(time.strftime("%Y-%m-%d-%H-%M"))
                if not local_vars['filename random key'] and not local_vars['filename keyword ckbox'] and not \
                local_vars['filename timestamp'] \
                        and not local_vars['filename filename']:
                    processing_basename.append("FL_processed")
                
                # generate harmonic frequencies
                harmonics = []
                if local_vars['signal harmonics type'] != "None":
                    harmonics = MainController.generate_harmonics(int(local_vars['signal filter harmonic frequency']),
                                                                  int(local_vars['signal filter nth harmonic']),
                                                                  local_vars['signal harmonics type'])
                # file processing
                
                for file in all_files:
                    samples = []
                    if local_vars['signal ckbox behead']:
                        self.processing_progress.update_task("Beheading raw files")
                        df = pd.read_csv(file, index_col=False, skiprows=skiprow)
                        self.processing_progress.increment_progress(1)
                    else:
                        df = pd.read_csv(file, index_col=False)
                    
                    # signal select columns
                    if local_vars['signal select columns ckbox']:
                        self.processing_progress.update_task("Selecting columns")
                        df = dpr.top_n_electrodes(df, int(local_vars['signal select columns number']),
                                                  except_column=self.model.vars["except column"])
                        self.processing_progress.increment_progress(1)
                    
                    # down sampling recordings
                    
                    if local_vars['signal sampling ckbox']:
                        self.processing_progress.update_task("Down sampling file")
                        samples = fp.equal_samples(df, int(local_vars['signal sampling']))
                        self.processing_progress.increment_progress(1)
                    else:
                        samples.append(df)
                    n_sample = 0
                    for df_s in samples:
                        
                        df_s_fft = pd.DataFrame()
                        # filtering
                        
                        if local_vars['signal filter']:
                            for ch in [col for col in df_s.columns if self.model.vars["except column"] not in col]:
                                self.processing_progress.update_task("Filtering")
                                df_s_ch = df_s[ch]
                                if local_vars['signal filter type'] == 'Highpass' and local_vars[
                                    'signal filter first cut']:
                                    df_s_ch = dpr.butter_filter(df_s_ch, order=int(local_vars['signal filter order']),
                                                                btype='highpass',
                                                                cut=int(local_vars['signal filter first cut']))
                                elif local_vars['signal filter type'] == 'Lowpass' and local_vars[
                                    'signal filter first cut']:
                                    df_s_ch = dpr.butter_filter(df_s_ch, order=int(local_vars['signal filter order']),
                                                                btype='lowpass',
                                                                cut=int(local_vars['signal filter first cut']))
                                elif local_vars['signal filter type'] == 'Bandstop' and local_vars[
                                    'signal filter first cut'] and \
                                        local_vars['signal filter second cut']:
                                    df_s_ch = dpr.butter_filter(df_s_ch, order=int(local_vars['signal filter order']),
                                                                btype='bandstop',
                                                                lowcut=int(
                                                                    local_vars['signal filter first cut']),
                                                                highcut=int(
                                                                    local_vars['signal filter second cut']))
                                elif local_vars['signal filter type'] == 'Bandpass' and local_vars[
                                    'signal filter first cut'] and \
                                        local_vars['signal filter second cut']:
                                    df_s_ch = dpr.butter_filter(df_s_ch, order=int(local_vars['signal filter order']),
                                                                btype='bandpass',
                                                                lowcut=int(
                                                                    local_vars['signal filter first cut']),
                                                                highcut=int(
                                                                    local_vars['signal filter second cut']))
                                if local_vars['signal harmonics ckbox']:
                                    for h in harmonics:
                                        df_s_ch = dpr.butter_filter(df_s_ch,
                                                                    order=int(local_vars['signal filter order']),
                                                                    btype='bandstop', lowcut=h - 2,
                                                                    highcut=h + 2)
                                
                                df_s[ch] = df_s_ch  # updating the dataframe for further processing
                                self.processing_progress.increment_progress(1)
                        
                        if local_vars['signal fft']:
                            for ch in [col for col in df_s.columns if self.model.vars["except column"] not in col]:
                                self.processing_progress.update_task("Fast Fourier Transform")
                                df_s_ch = df_s[ch]
                                # fast fourier
                                
                                clean_fft, clean_freqs = dpr.fast_fourier(df_s_ch, int(local_vars['signal fft sf']))
                                if "Frequency [Hz]" not in df_s_fft.columns:
                                    df_s_fft['Frequency [Hz]'] = clean_freqs
                                df_s_fft[ch] = clean_fft
                                self.processing_progress.increment_progress(1)
                            df_s = df_s_fft
                        
                        # merge signal
                        if local_vars['signal average']:
                            self.processing_progress.update_task("Averaging signal")
                            if local_vars['signal fft']:
                                df_s = dpr.merge_all_columns_to_mean(df_s, "Frequency [Hz]").round(3)
                            else:
                                df_s = dpr.merge_all_columns_to_mean(df_s, self.model.vars["except column"]).round(3)
                            self.processing_progress.increment_progress(1)
                        
                        # interpolation signal
                        df_s_processed = pd.DataFrame()
                        if local_vars['signal interpolation ckbox']:
                            self.processing_progress.update_task("interpolation signal")
                            for ch in df_s.columns:
                                df_s_processed[ch] = fp.smoothing(df_s[ch], int(local_vars['signal interpolation']),
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
                        
                        if local_vars['filename make dataset'] == 0:
                            df_s_processed.to_csv(
                                os.path.join(local_vars['filename save under'], '_'.join(filename_constructor)),
                                index=False)
                        else:
                            processed_files_to_make_dataset.append((df_s_processed, file))
                        n_sample += 1
                if local_vars['filename make dataset'] == 1:
                    first_df = processed_files_to_make_dataset[0][0]
                    dataset = pd.DataFrame(columns=[str(x) for x in range(len(first_df.values))])
                    targets = pd.DataFrame(columns=['label', ])
                    for data in processed_files_to_make_dataset:
                        self.processing_progress.update_task("Making dataset")
                        dataframe = data[0]
                        file = data[1]
                        for col in dataframe.columns:
                            if self.model.vars["except column"] not in col and "Frequency [Hz]" not in col:
                                signal = dataframe[col].values
                                dataset.loc[len(dataset)] = signal
                                for key_target, value_target in self.model.targets.items():
                                    if key_target in file:
                                        targets.loc[len(targets)] = value_target
                        
                        self.processing_progress.increment_progress(1)
                    dataset['label'] = targets['label']
                    
                    # preparation of filename
                    processing_basename = [ ]
                    characters = string.ascii_letters + string.digits
                    if not self.model.vars["filename filename"]:
                        processing_basename.append('DATASET')
                        if local_vars['signal select columns ckbox']:
                            processing_basename.append(f"Sel{local_vars['signal select columns mode'].capitalize()}"
                                                       f"{local_vars['signal select columns metric'].capitalize()}"
                                                       f"{local_vars['signal select columns number']}")
                        if local_vars['signal sampling ckbox']:
                            processing_basename.append(f"Ds{local_vars['signal sampling']}")
                        if local_vars['signal filter']:
                            processing_basename.append(
                                f"O{local_vars['signal filter order']}{local_cbox['signal filter type']}"
                                f"{local_vars['signal filter first cut']}-{local_vars['signal filter second cut']}"
                                f"H{local_vars['signal harmonics type']}{local_vars['signal filter harmonic frequency']}-"
                                f"{local_vars['signal filter nth harmonic']}")
                        if local_vars['signal fft']:
                            processing_basename.append("signal fft")
                        if local_vars['signal average']:
                            processing_basename.append("avg")
                        if local_vars['signal interpolation ckbox']:
                            processing_basename.append(f"Sm{local_vars['signal interpolation']}")
                    else:
                        processing_basename.append(self.model.vars['filename filename'])
                        
                    if local_vars['filename random key']:
                        processing_basename.append(''.join(random.choice(characters) for i in range(5)))
                    if local_vars['filename keyword ckbox']:
                        processing_basename.append(local_vars['filename keyword'])
                    if local_vars['filename timestamp']:
                        processing_basename.append(time.strftime("%Y-%m-%d-%H-%M"))
                    if not local_vars['filename random key'] and not local_vars['filename keyword ckbox'] and not \
                    local_vars['filename timestamp']:
                        processing_basename.append("FL_processed")
                    
                    dataset.to_csv(
                        os.path.join(local_vars['filename save under'], '_'.join(processing_basename) + '.csv'),
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
            if type(list(widgets.values())[0]) == ctk.StringVar or \
                type(list(widgets.values())[0]) == ctk.IntVar or \
                type(list(widgets.values())[0]) == ctk.DoubleVar:
                for key, value in widgets.items():
                    local_dict[key] = value.get()
                self.model.vars.update(local_dict)
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
        local_vars = self.model.vars
        local_entry = self.model.entries
        
        n_sample = int(local_vars['signal sampling'])
        
        mea = int(local_vars['signal ckbox behead'])
        electrodes = int(local_vars['signal select columns ckbox'])
        sampling = int(local_vars['signal sampling ckbox'])
        
        merge = int(local_vars['signal average'])
        interpolation = int(local_vars['signal interpolation ckbox'])
        make_dataset = int(local_vars['filename make dataset'])
        filtering = int(local_vars['signal filter'])
        fft = int(local_vars['signal fft'])
        
        file_level_tasks = mea + electrodes + sampling
        sample_level_tasks = merge + interpolation
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
                widget.delete(0, ctk.END)
                widget.insert(0, self.model.entries[key])
                widget.configure(state='disabled')
        
        for key, widget in self.view.switches.items():
            if widget.cget('state') == 'normal':
                if self.model.switches[key]:
                    widget.select()
                else:
                    widget.deselect()
                    
        for key, widget in self.view.ckboxes.items():
            if widget.cget('state') == 'normal':
                if self.model.checkboxes[key]:
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
        
        if all([self.view.ckboxes['filesorter single'].get(), self.view.ckboxes['filesorter multiple'].get()]):
            filesorter_errors.append("You can only chose one between Single file analysis or Multiple files analysis.")
        
        if not any([self.view.ckboxes['filesorter single'].get(), self.view.ckboxes['filesorter multiple'].get()]):
            filesorter_errors.append("You have to select one between Single file analysis or Multiple files analysis.", )
        
        if self.view.ckboxes['filesorter multiple'].get():
            if not self.view.entries['filesorter multiple'].get():
                filesorter_errors.append("You have to select a parent directory to run multi-file processing.")
        
        if self.view.ckboxes['filesorter single'].get():
            if not self.view.entries['filesorter single'].get():
                filesorter_errors.append("You have to select a file to run single file processing.")
        
        # forbidden characters
        for key, textbox in self.view.textboxes.items():
            elements = textbox.get(1.0, ctk.END)
            for element in elements:
                fcs = ival.value_has_forbidden_character(element)
                if fcs:
                    filesorter_errors.append(f"Forbidden characters in '{element}' : {fcs}")
        
        # -------- PROCESSING
        
        if self.view.vars['signal ckbox behead'].get():
            if not self.view.vars['signal behead'].get():
                signal_errors.append("You have to indicate a number of rows to behead from the raw MEA files.")
        
        if self.view.vars['signal select columns ckbox'].get():
            if not self.view.vars['signal select columns number'].get():
                signal_errors.append("You have to indicate a number of columns to select.")
            if self.view.vars['signal select columns mode'].get() == 'None':
                signal_errors.append("You have to select a mode for column selection.")
            
            if self.view.vars['signal select columns metric'].get() == 'None':
                signal_errors.append("You have to select a metric to use for the electrode selection.")
        
        if self.view.vars['signal sampling ckbox'].get():
            if not self.view.vars['signal sampling'].get():
                signal_errors.append("You have to indicate a number of samples.")
        
        if self.view.vars['signal filter harmonic frequency'].get():
            if self.view.vars['signal filter nth harmonic'].get():
                harmonic = int(self.view.vars['signal filter harmonic frequency'].get())
                nth = int(self.view.vars['signal filter nth harmonic'].get())
                frequency = int(self.view.vars['signal filter sf'].get())
                if harmonic * nth > frequency / 2:
                    signal_errors.append("The chosen nth harmonic is superior to half the sampling frequency."
                                  f" Please use maximum nth harmonic as nth<{int((frequency / 2) / harmonic)}")
            else:
                signal_errors.append("You have to fill both the harmonic frequency and the nth harmonics"
                              " using valid numbers.")
        
        if self.view.vars['signal filter'].get():
            if not gates.AND(
                    [self.view.vars[x].get() for x in
                     ['signal filter order', 'signal filter sf', 'signal filter first cut', ]]):
                signal_errors.append('You have to fill at least the filter order, sampling '
                              'frequency, and first cut to use the filtering function.')
            
            if self.view.vars['signal filter second cut'].get() and (
                    self.view.vars['signal filter type'].get() in ['Highpass", "Lowpass']):
                signal_errors.append(f"The second frequency is not needed when using a "
                              f"{self.view.vars['signal filter type'].get()} filter.")
            if self.view.vars['signal filter type'].get() in ['Bandstop", "Bandpass'] and not gates.AND(
                    [self.view.vars['signal filter second cut'].get(),
                     self.view.vars['signal filter first cut'].get()]):
                signal_errors.append(f"Both low cut and high cut frequencies are needed when"
                              f" using a f{self.view.vars['signal filter type'].get()} filter")
        
       
        
        if self.view.vars['signal fft'].get():
            if not self.view.vars['signal fft sf'].get():
                signal_errors.append("Sampling frequency rate needed to perform Fast Fourier Transform.")
        
        if self.view.vars['signal interpolation ckbox'].get():
            if not self.view.vars['signal interpolation'].get():
                signal_errors.append("Number of final values needed to perform interpolation.")
        
        # -------- FILENAME
        if self.view.vars['filename save under'].get() == '':
            filename_errors.append('You have to select a directory where to save your file.')
        elif os.path.isdir(self.view.vars['filename save under'].get()) is False:
            filename_errors.append(f"The selected path {self.view.vars['filename save under'].get()} does not exist.")
        
        if self.view.vars['filename keyword ckbox'].get():
            if not self.view.vars['filename keyword'].get():
                filename_errors.append("Keyword needed.")
        
        for key, entry in self.view.entries.items():
            if type(entry) == ErrEntry:
                if entry.error_message.get() != '':
                    filename_errors.append(f"{key} : {entry.error_message.get()}")
                    
        if self.view.vars['filename make dataset'].get():
            if not gates.AND(
                    [self.view.vars['signal average'].get(), self.view.vars['filesorter multiple'].get()]):
                filename_errors.append(
                    "The 'make dataset' option is available only if 'Average' and 'Multiple files analysis' are both enabled.")
        
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
        img = ctk.CTkImage(dark_image=Image.open(resource_path(f"data/firelearn_img/{step}_green.png")), size=self.view.image_buttons[step].get_image_size())
        self.view.image_buttons[step].configure(image=img)
        self.view.step_check[step] = 1
    
    def invalidate_step(self, step):

        img = ctk.CTkImage(dark_image=Image.open(resource_path(f"data/firelearn_img/{step}_red.png")), size=self.view.image_buttons[step].get_image_size())
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
        self.view.vars['errors'].set(text)

    def export_summary(self):
        
        def symbol_frame(symbol, text, width=40):
            text_length = len(text)
            whitespaces = (width - text_length - 2) / 2
            before_text = int(np.floor(whitespaces))
            after_text = int(np.ceil(whitespaces))
            frame = f"{symbol * width}\n" \
                    f"{symbol}{' ' * before_text}{text}{' ' * after_text}{symbol}\n" \
                    f"{symbol * width}"
            return frame
        
        text = f"{symbol_frame('*', text='FIRELEARN PROCESSING SUMMARY', width=60)}\n\n"
        
        text += f"{symbol_frame('.', text='File sorting')}\n\n"
        
        to_include_txt = [x for x in self.model.to_include]
        to_exclude_txt = [x for x in self.model.to_exclude]
        targets_txt = [f"{k} - {v}"  for k, v in self.model.targets.items()]
        text += (f"Sorting multiple files : {'disabled' if not self.view.vars['filesorter multiple ckbox'].get() else 'enabled'}\n"
                 f"Parent path: {self.view.vars['filesorter multiple'].get()}\n\n"
                 f""
                 f"To include:\n"
                 f"{to_include_txt}\n"
                 f""
                 f"To exclude:\n"
                 f"{to_exclude_txt}\n"
                 f""
                 f"Targets:\n"
                 f"{targets_txt}\n"
                 f""
                 f"Sorting single file: {'disabled' if not self.view.vars['filesorter single ckbox'].get() else 'enabled'}\n"
                 f"File path: {self.view.vars['filesorter single'].get()}\n\n")
        
        text += f"{symbol_frame('.', text='Signal processing')}\n\n"
        
        select_column = ('number: '+self.view.vars['signal select columns number'].get()+
                         ' - mode: '+self.view.vars['signal select columns mode'].get()+
                         ' - metric: '+ self.view.vars['signal select columns metric'].get())
        text += (f"Beheading top-file metadata : {'disabled' if not self.view.vars['signal ckbox behead'].get() else self.view.vars['signal behead'].get() }\n"
                 f"Select columns: "
                 f"{'disabled' if not self.view.vars['signal select columns ckbox'].get() else select_column}\n"
                 f"Divide file into: {'disabled' if not self.view.vars['signal sampling ckbox'].get() else self.view.vars['signal sampling'].get() }\n"
                 f"Fast Fourier Transform sampling frequency (Hz): {'disabled' if not self.view.vars['signal fft'].get() else self.view.vars['signal fft sf'].get() }\n"
                 f"Average of signal column-wise: {'disabled' if not self.view.vars['signal average'].get() else 'enabled' }\n"
                 f"Linear interpolation of signal into n value: {'disabled' if not self.view.vars['signal interpolation ckbox'].get() else self.view.vars['signal interpolation'].get() }\n"
                 f"\n"
                 f"Filtering: {'disabled' if not self.view.vars['signal filter'].get() else 'enabled' }\n"
                 f"Order: {self.view.vars['signal filter order'].get()}\n"
                 f"Sampling frequency (Hz): {self.view.vars['signal filter sf'].get()}\n"
                 f"Filter type: {self.view.vars['signal filter type'].get()}\n"
                 f"First frequency cut (Hz): {self.view.vars['signal filter first cut'].get()}\n"
                 f"Second frequency cut (Hz): {self.view.vars['signal filter second cut'].get()}\n"
                 f"\n"
                 f"Filtering harmonics: {'disabled' if not self.view.vars['signal harmonics ckbox'].get() else 'enabled' }\n"
                 f"Type: {self.view.vars['signal harmonics type'].get()}\n"
                 f"Frequency (Hz): {self.view.vars['signal filter harmonic frequency'].get()}\n"
                 f"Up to Nth: {self.view.vars['signal filter nth harmonic'].get()}\n\n"
                 f"Exception column from processing: {self.view.vars['except column'].get()}"
                 )
        
        text += f"{symbol_frame('.', text='Output management')}\n\n"
        
        text += (f"Random key: {'disabled' if not self.view.vars['filename random key'].get() else 'enabled'}\n"
                 f"{'Timestamp: disabled' if not self.view.vars['filename timestamp'].get() else 'enabled'}\n"
                 f"{'Keyword: disabled' if not self.view.vars['filename keyword ckbox'].get() else self.view.vars['filename keyword'].get() }\n"
                 f"{'Make files as dataset: disabled' if not self.view.vars['filename make dataset'].get() else 'enabled'}\n"
                 f"{'Specified filename: disabled' if not self.view.vars['filename filename ckbox'].get() else self.view.vars['filename filename'].get() }\n"
                 f" {'Save processed file(s) under: disabled' if not self.view.vars['filename save under'].get() else self.view.vars['filename save under'].get() }\n")
        
        # todo : FIXME
        path = filedialog.asksaveasfilename(defaultextension='.txt',
                                        filetypes=[('Text document', '*.txt'), ],
                                            confirmoverwrite=True)
        if path:
            with open(str(path), 'w', encoding='utf-8',) as file:
                file.write(text)

            