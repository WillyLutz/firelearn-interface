import concurrent.futures
import datetime
import multiprocessing
import os
import random
import string
import time
from multiprocessing import Queue
from queue import Empty
from tkinter import filedialog, messagebox
import gc
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

from scripts.PROCESSES.FileProcessor import FileProcess

pd.options.mode.chained_assignment = None


class ProcessingController:
    def __init__(self, view):
        self.processing_progress = None
        self.model = ProcessingModel()
        self.view = view
        self.view.controller = self  # set controller
        self.files_to_process = []
        
        self.files_queue = None
        self.progress_queue = None
        self.result_queue = None
        
        self.workers_alive = False
        self.cancelled = False
    
    
    
    def processing(self, ):
        if self.check_params_validity():
            if self._check_steps():
                processing_time_start = datetime.datetime.now()
                local_vars = self.model.vars
                local_cbox = self.model.cbboxes
                
                self.files_to_process = self._select_files()
                
                if not self.files_to_process:
                    messagebox.showerror("Missing files", "No files have been found using"
                                                          " your inclusion and exclusion parameters.")
                    return

                self._init_progress_bar(self.files_to_process)
                
                processing_basename = self._basename_preparation()
                
                harmonics = MainController.generate_harmonics(int(local_vars['signal filter harmonic frequency']),
                                                                  int(local_vars['signal filter nth harmonic']),
                                                                  local_vars['signal harmonics type'])\
                    if local_vars['signal harmonics type'] != "None" else []
                
                self.processing_progress.update_task("Distributed processing...")
                n_cpu = multiprocessing.cpu_count()
                # n_workers = 1
                if len(self.files_to_process) > int(0.7 * n_cpu):
                    n_workers = 1 if int(0.7 * n_cpu) == 0 else int(0.7 * n_cpu)
                elif len(self.files_to_process) < int(0.7 * n_cpu):
                    
                    n_workers = len(self.files_to_process)

                print("Using n workers for processing: ", n_workers)
                self.processing_progress.update_task("Distributed processing...")
                
                with multiprocessing.Manager() as manager:
                    self.files_queue = multiprocessing.Queue()
                    self.progress_queue = multiprocessing.Queue()
                    self.result_queue = multiprocessing.Queue()
                    
                    # Populate the queue with files
                    for file in self.files_to_process:
                        self.files_queue.put(file)
                    
                    # Add sentinel values (one per worker)
                    for _ in range(n_workers):
                        self.files_queue.put(None)
                        
                    all_processes = [FileProcess(self.files_queue,
                                                 self.result_queue,
                                                 self.progress_queue,
                                                 harmonics,
                                                 processing_basename,
                                                 self.model.vars) for _ in range(n_workers)]
                    # all_processes = [multiprocessing.Process(target=self.process_file_for_worker,
                    #                                          args=(f"worker_{_}",
                    #                                                harmonics, processing_basename,
                    #                                                ))
                    #                  for _ in range(n_workers)]
                    
                    for p in all_processes:
                        print(p)
                        p.start()
                        
                    results = {}
                    finished_workers = 0
                    while finished_workers != len(all_processes) and self.processing_progress.progress_window.winfo_exists():
                        are_alive = []
                        for w in all_processes:
                            if w.is_alive():
                                are_alive.append(w)
                        print("Workers alive: ", [w.name for w in are_alive])
                        
                        try:
                            result = self.result_queue.get()# Use get_nowait() to avoid blocking
                            if type(result) == str: # A Worker finished ! joining it
                                finished_workers += 1
                                print("Worker finishing", result, "finished workers:", finished_workers)

                            else:
                                progress_item = self.progress_queue.get()
                                self.processing_progress.increment_progress(progress_item)
                                filename, processed_files_to_make_dataset = result
                                results[filename] = processed_files_to_make_dataset  # Store results dynamically
                        except Empty:
                            # No progress item was available; just continue looping.
                            pass
                        
                    self.processing_progress.update_task("Finishing distributed processing...")

                    while not self.progress_queue.empty():
                        self.processing_progress.increment_progress(self.progress_queue.get_nowait())
                    
                    while not self.result_queue.empty():
                        processed_files_to_make_dataset, filename  = self.result_queue.get_nowait()  # Use get_nowait() to avoid blocking
                        results[filename] = processed_files_to_make_dataset  # Store results dynamically
                        
                    self.cancelled = True if any(
                        [w.is_alive() for w in all_processes]) and not self.processing_progress.is_alive() else False
                
                    self.processing_progress.update_task("Terminating workers...")
                    for worker in all_processes:
                        print("joining ", worker.name)
                        worker.join(timeout=5)
                        if worker.is_alive():
                            worker.terminate()
                        
                    if self.cancelled:
                        messagebox.showinfo("Cancel Processing", "All workers properly terminated.")
                    else:
                        print("All workers properly terminated.")
                        
                    self.workers_alive = False
                    self.cancelled = False
                    if local_vars['filename make dataset'] == 1:
                        
                        self._make_dataset(processing_basename, results)
                processing_time_end = datetime.datetime.now()
                print("Processing time: ", processing_time_end-processing_time_start)
    

    def _basename_preparation(self):
        """
        Prepare the base name of the final file depending on UI values.
        
        Returns
        -------
        list of str that are element for teh future file name.
        """
        processing_basename = []
        local_vars = self.model.vars
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
            
        return processing_basename
    
    def _check_steps(self):
        """
        Check if there are any steps in the processing UI that contains errors.
        
        Returns
        -------
            True if all steps for processing are True
        """
        if all([value for key, value in self.view.step_check.items()]):
            self.update_params(self.view.cbboxes)
            self.update_params(self.view.entries)
            self.update_params(self.view.ckboxes)
            self.update_params(self.view.vars)
            
            return True
        else:
            return False
    
    @staticmethod
    def iter_large_dict(large_dict):
        """Generator to iterate over a large dictionary containing lists of DataFrames."""
        i = 0
        for key, value in large_dict.items():
            i += 1
            yield key,  value
            del value  # Free memory after yielding the list
            gc.collect()  # Force garbage collection
    
    def _make_dataset(self, processing_basename, results):
        """
        Creates a dataset from the processed files by extracting signal data and
        corresponding labels, then saves the dataset to a CSV file.

        Parameters
        ----------
        results : dict
            A dict of with base names used to construct the processed dataset file's name.

        processed_files_to_make_dataset : list[tuple]
            A list of tuples containing processed dataframes and their corresponding file paths.
            Each tuple represents one processed file and is used to extract signal data and labels.

        Returns
        -------
        None
            This function does not return any value. It saves the created dataset to a CSV file.

        Notes
        -----
        This function iterates over the processed files, extracts the signal data from each
        file's dataframe, and appends it to the `dataset`. It also checks if a corresponding
        label exists in the file name (from `self.model.targets`), and associates the label
        with the corresponding signal data. The resulting dataset and labels are saved to a
        CSV file whose name is constructed using the provided `processing_basename`.

        """
        self.processing_progress.update_task("Making dataset...")
        local_vars = self.model.vars
        # Get a sample dataframe to determine number of columns
        first_df = next(iter(results.values()))[0][0]
        num_cols = len(first_df.values)
        
        # Prepare lists to accumulate dataset rows and target labels
        dataset_rows = []
        target_rows = []
        for k, processed_files in results.items():
            for data in processed_files:
                dataframe, file = data[0], data[1]
                # Filter the columns once for each dataframe iteration
                valid_columns = [
                    col for col in dataframe.columns
                    if self.model.vars["except column"] not in col and "Frequency [Hz]" not in col
                ]
                for col in valid_columns:
                    signal = dataframe[col].values
                    dataset_rows.append(signal)
                    # Iterate through targets and append a label if the key is found in file.
                    # If only one target should be matched, consider breaking after a match.
                    for key_target, value_target in self.model.targets.items():
                        if key_target in file:
                            target_rows.append(value_target)
                            break  # Uncomment this line if only one match is expected per signal
                
            self.processing_progress.increment_progress(1)
        self.processing_progress.update_task("Saving dataset...")
        # Create DataFrames from the accumulated lists
        dataset = pd.DataFrame(dataset_rows, columns=[str(x) for x in range(num_cols)])
        # Assuming each row in dataset has a corresponding target
        targets = pd.DataFrame(target_rows, columns=['label'])
        dataset['label'] = targets['label']
        
        dataset.to_csv(
            os.path.join(local_vars['filename save under'], '_'.join(processing_basename) + '.csv'),
            index=False)
        
        self.processing_progress.increment_progress(1)
        messagebox.showinfo("Processing finished", "Processing finished")
    

    def _select_files(self):
        """
        Select files based on inclusion and exclusion parameters in the UI.
        
        Returns
        -------
            list[str]
                list of paths (str) that correspond to the inclusion and exclusion parameters
        """
        all_files = []
        if self.model.vars['filesorter multiple']:
            files = ff.get_all_files(self.model.parent_directory)
            for file in files:
                if all(i in file for i in self.model.to_include) and (
                        not any(e in file for e in self.model.to_exclude)):
                    all_files.append(file)
        
        if self.model.vars['filesorter single']:
            all_files.append(self.model.single_file)
        return all_files
    
    def _init_progress_bar(self, all_files):
        """
        Initializes and starts a progress bar for processing files.

        Parameters
        ----------
        all_files : list[str]
            A list containing the file paths to be processed.

        Returns
        -------

        Notes
        -----
        This function reads the first file in `all_files` to estimate the number of
        columns for processing. If specific conditions are met (e.g., certain checkboxes
        are selected), it adjusts the number of rows to skip when reading the CSV file.
        The total number of tasks for the progress bar is calculated using the number of
        files and columns, and the progress bar is then started.


        """
        local_vars = self.model.vars
        
        n_files = int(len(all_files))
        skiprow = 0
        if local_vars['signal ckbox behead']:
            skiprow = int(local_vars['signal behead'])
        
        example_dataframe = pd.read_csv(all_files[0], index_col=False, skiprows=skiprow)
        if local_vars['signal select columns ckbox']:
            n_columns = int(local_vars['signal select columns number'])
        else:
            n_columns = int(
                len([col for col in example_dataframe.columns if self.model.vars["except column"] not in col]))
        
        self.processing_progress = ProgressBar("Processing progression", app=self.view.app)
        self.processing_progress.total_tasks = self.update_number_of_tasks(n_files, n_columns)
        self.processing_progress.start()
        
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
        """
        Adds or removes a value from the 'to_include' list in the model, based on user input.

        This method updates the `to_include` list in the model by either adding or removing a value,
        depending on the specified mode. If the entry is valid (does not contain forbidden characters),
        it either appends the value to the list (if mode is 'add') or removes it (if mode is 'subtract').
        The textbox is updated to reflect the change, and the entry field is cleared.

        Parameters
        ----------
        entry : ctk.CTkEntry
            The entry widget that contains the value to add or remove.

        textbox : ctk.CTkTextbox
            The textbox widget that will be updated with the new 'to_include' list.

        mode : str, optional, default='add'
            The mode to determine whether to add or subtract the value. 'add' will append the value
            to the list, while 'subtract' will remove it.

        Returns
        -------
        bool
            Returns False if the entry contains forbidden characters or is empty, otherwise None.
        """
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
        """
        Adds or removes a value from the 'to_exclude' list in the model, based on user input.

        This method updates the `to_exclude` list in the model by either adding or removing a value,
        depending on the specified mode. If the entry is valid (does not contain forbidden characters),
        it either appends the value to the list (if mode is 'add') or removes it (if mode is 'subtract').
        The textbox is updated to reflect the change, and the entry field is cleared.

        Parameters
        ----------
        entry : ctk.CTkEntry
            The entry widget that contains the value to add or remove.

        textbox : ctk.CTkTextbox
            The textbox widget that will be updated with the new 'to_exclude' list.

        mode : str, optional, default='add'
            The mode to determine whether to add or subtract the value. 'add' will append the value
            to the list, while 'subtract' will remove it.

        Returns
        -------
        bool
            Returns False if the entry contains forbidden characters or is empty, otherwise None.
        """
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
        """
        Adds or removes a target key-value pair in the model's targets, based on user input.

        This method updates the `targets` dictionary in the model by either adding a new key-value pair
        (if mode is 'add') or removing an existing key (if mode is 'subtract'). It checks for forbidden
        characters in the key and value entries and displays an error message if necessary. The textbox
        is updated to reflect the change, and the entry fields are cleared.

        Parameters
        ----------
        key_entry : ctk.CTkEntry
            The entry widget that contains the key for the target.

        value_entry : ctk.CTkEntry
            The entry widget that contains the value for the target.

        textbox : ctk.CTkTextbox
            The textbox widget that will be updated with the new targets.

        mode : str, optional, default='add'
            The mode to determine whether to add or subtract the key-value pair. 'add' will add a new
            key-value pair, while 'subtract' will remove the specified key.

        Returns
        -------
        bool
            Returns False if either the key or value contains forbidden characters, or if the entries
            are empty. Otherwise, the method updates the model's targets and the textbox.
        """
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
        """
        Updates the model's variables, checkboxes, entries, comboboxes, or textboxes based on the provided widget values.
        
        This method iterates over the dictionary of widgets, retrieves the current values from each widget,
        and updates the corresponding attributes in the `model.vars`, `model.ckboxes`, `model.entries`,
        `model.cbboxes`, or `model.textboxes` based on the widget type.
        
        Parameters
        ----------
        widgets : dict
           A dictionary of widgets where the keys are widget identifiers and the values are the widget objects.
           The widget objects can be of various types such as `ctk.StringVar`, `ctk.IntVar`, `ctk.DoubleVar`,
           `ctk.CTkCheckBox`, `ctk.CTkEntry`, `ErrEntry`, `tk.ttk.Combobox`, or `ctk.CTkTextbox`.
        
        Returns
        -------
        None
           This method does not return a value. It updates the corresponding attributes in the model based on
           the widget values.
        
        Notes
        -----
        - The method supports updating different widget types, including string variables, integer variables,
         checkboxes, entries, comboboxes, and textboxes.
        - It ensures that the appropriate model dictionary (`vars`, `ckboxes`, `entries`, `cbboxes`, or `textboxes`)
         is updated based on the widget type.
        """
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
            if type(list(widgets.values())[0]) == ctk.CTkCheckBox:
                for key, value in widgets.items():
                    local_dict[key] = value.get()
                self.model.ckboxes.update(local_dict)
    
    def update_number_of_tasks(self, n_file, n_col, ):
        """
        Calculates the total number of tasks to be processed based on the configuration and input parameters.

        This method calculates the total number of tasks that need to be completed, taking into account
        various flags and parameters set in the model. The total task count is used to drive the progress
        bar, indicating how many tasks remain to be processed.

        Parameters
        ----------
        n_file : int
            The number of files to process.

        n_col : int
            The number of columns to process per file.

        Returns
        -------
        int
            The total number of tasks to be completed.
        """
        local_vars = self.model.vars
        
        
        mea = int(local_vars['signal ckbox behead'])
        electrodes = int(local_vars['signal select columns ckbox'])
        sampling = int(local_vars['signal sampling ckbox'])
        
        n_sample = int(local_vars['signal sampling']) if sampling else 1

        merge = int(local_vars['signal average'])
        interpolation = int(local_vars['signal interpolation ckbox'])
        make_dataset = int(local_vars['filename make dataset'])
        filtering = int(local_vars['signal filter'])
        fft = int(local_vars['signal fft'])
        
        concat_result = n_file #* n_sample
        
        saving_dataset = 1
        
        file_level_tasks = mea + electrodes + sampling # performed only once per file
        sample_level_tasks = merge + interpolation # performed only once per sample (multiple times per file)
        column_level_tasks = filtering * n_col + fft * n_col # performed once per column (multiple times per sample)
        
        total_tasks = n_file * (file_level_tasks + n_sample * (sample_level_tasks + column_level_tasks))
        total_tasks = n_file
        
        if make_dataset:
            
            total_tasks += n_file + saving_dataset#  * n_sample  + concat_result
        
        # total_tasks = n_file if not make_dataset else n_file + 1
        return total_tasks
    
    def update_view_from_model(self, ):
        """
        Update the view's variables from the model's data.

        This function synchronizes the view with the model by updating the view's UI components
        with the current values from the model's attributes.

        Parameters
        ----------

        Returns
        -------
        """
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
                if key in self.model.switches.keys():
                    widget.select()
                else:
                    widget.deselect()
                    
        for key, widget in self.view.ckboxes.items():
            if widget.cget('state') == 'normal':
                if key in self.model.ckboxes.keys():
                    if self.model.ckboxes[key] == 1:
                        widget.select()
                    else:
                        widget.deselect()
            else:
                widget.configure(state='normal')
                if key in self.model.ckboxes.keys():
                    if self.model.ckboxes[key] == 1:
                        widget.select()
                    else:
                        widget.deselect()
                widget.configure(state='disabled')


        
        for key, widget in self.view.textboxes.items():
            MainController.update_textbox(widget, self.model.textboxes[key].split("\n"))
    
    @staticmethod
    def modulate_entry_state_by_switch(switch, entry):
        """
        Modulates the state of an entry widget based on the state of a switch.

        This method acts as a helper function to update the state (enabled/disabled) of an entry widget depending on the
        state of a switch. It delegates the actual logic to the `modulate_entry_state_by_switch` method of the `MainController`.

        Parameters
        ----------
        switch : ctk.CTkSwitch
            The switch widget that determines the state of the entry.
        entry : ctk.CTkEntry
            The entry widget whose state (enabled/disabled) is being modified.

        Returns
        -------
        None
            This method does not return any value. It updates the state of the entry widget directly.

        Notes
        -----
        - This method is static and relies on the `MainController` class for the actual state modification logic.
        - It is intended to be used in scenarios where the state of an entry widget needs to be tied to the status of a switch.
        """
        
        MainController.modulate_entry_state_by_switch(switch, entry)
    
    def load_config(self, ):
        """
        Loads a configuration file and updates the model.

        This method prompts the user to select a configuration file with the `.pcfg` extension. If a valid file is selected,
        it attempts to load the model using the `load_model` method of the `model`. After the model is successfully loaded,
        it updates the view to reflect the changes made to the model.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method does not return any value. It updates the model and the view based on the loaded configuration.

        Notes
        -----
        - The method uses a file dialog to allow the user to select the configuration file.
        - If the file is successfully loaded, the view is updated to reflect the new state of the model.
        """
        
        f = filedialog.askopenfilename(title="Open file", filetypes=(("Processing config", "*.pcfg"),))
        if f:
            if self.model.load_model(path=f):
                self.update_view_from_model()
    
    def save_config(self, ):
        """
        Saves the current configuration to a file.

        This method checks the validity of the current parameters, updates the model with the values from the view widgets,
        and then prompts the user to save the configuration to a file. If the user selects a valid location,
        the configuration is saved using the `save_model` method of the `model`.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method does not return any value. It saves the model's configuration to a file.

        Notes
        -----
        - The method ensures that all parameters in the view (checkboxes, entries, comboboxes, etc.) are updated before saving.
        - The file is saved with the `.pcfg` extension by default, but the user can specify a different filename or location.
        """
        if self.check_params_validity():
            for widgets in [self.view.ckboxes, self.view.entries, self.view.cbboxes, self.view.sliders, self.view.vars,
                            self.view.switches, self.view.textboxes, self.view.labels]:
                self.update_params(widgets)
            
            
            f = filedialog.asksaveasfilename(defaultextension=".pcfg",
                                             filetypes=[("Processing", "*.pcfg"), ])
            if f:
                self.model.save_model(path=f, )
    
    def check_params_validity(self):
        """
        Validates the processing parameters before starting the processing of the files.

        Returns
        -------
        bool
            True if parameters are valid, otherwise False with an error message.
        """
        filesorter_errors = []
        signal_errors = []
        filename_errors = []
        
        # -------- FILESORTER
        if self.workers_alive:
            if self.cancelled:
                messagebox.showerror("Workers alive",
                                     "Workers from previous processing are still alive and being terminated."
                                     " Please wait a bit before starting a new processing")
                return False
            else:
                messagebox.showerror("Workers alive", "Workers are currently alive."
                                                      "To start a new processing, please either cancel the current one "
                                                      "or wait for it to finish.")
                return False
        
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
            filename_errors.append(f"The selected path {self.view.vars['filename save under'].get()} is not a directory.")
        
        if self.view.vars['filename keyword ckbox'].get():
            if not self.view.vars['filename keyword'].get():
                filename_errors.append("Keyword needed.")
        
        # for key, entry in self.view.entries.items():
        #     if type(entry) == ErrEntry:
        #         if entry.error_message.get() != '':
        #             filename_errors.append(f"{key} : {entry.error_message.get()}")
        
        # forbidden characters
        for entry in ["filename keyword", ]:
            fc = self.view.parent_view.has_forbidden_characters(self.view.entries[entry])
            if not fc:
                filename_errors.append(f"entry {entry} (\"{self.view.entries[entry].get()}\") contains forbidden characters")
            
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
    
    def delay(self, ms:int ):
        var = ctk.IntVar()
        self.view.app.after(ms, var.set, 1)
        self.view.app.wait_variable(var)
    def export_summary(self):
        """
        Generates and exports a detailed processing summary to a text file.

        This method creates a formatted summary of various configuration and processing parameters, including file sorting, signal processing, and output management. The summary is displayed using a combination of separators and text, organized into different sections. After the summary is generated, the user is prompted to specify a file path to save the text summary.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method does not return any value. It saves the summary to a text file.

        Exceptions
        ----------
        - If the user provides a file path or there is an issue while saving the file, an exception may occur.
        - The method ensures that the file is saved with the `.txt` extension.

        Notes
        -----
        - The summary includes details such as signal processing settings (e.g., filtering, FFT, interpolation), file sorting parameters (e.g., included/excluded files, sorting options), and output management options (e.g., file naming, random key, timestamp).
        """
        
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

            