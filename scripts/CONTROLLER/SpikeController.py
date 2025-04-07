import ast
import math
import multiprocessing
import random
import threading
import tkinter as tk
from datetime import datetime
from functools import partial
from queue import Empty
from tkinter import ttk, filedialog, messagebox

import customtkinter as ctk
import numpy as np
import pandas as pd
import seaborn as sns
from fiiireflyyy import files as ff
from matplotlib import pyplot as plt
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import scripts.CONTROLLER.input_validation as ival
from scripts.CONTROLLER import data_processing
from scripts.CONTROLLER.MainController import MainController
from scripts.CONTROLLER.ProgressBar import ProgressBar
from scripts.MODEL.SpikeModel import SpikeModel
from scripts.PROCESSES.SpikeDetector import SpikeDetectorProcess
from scripts.PROCESSES.WatchDog import WatchDog
from scripts.WIDGETS.ErrEntry import ErrEntry
from scripts.WIDGETS.Separator import Separator

import logging
logger = logging.getLogger("__SpikeDetection__")

class SpikeController:
    def __init__(self, view, ):
        self.model = SpikeModel()
        self.view = view
        self.view.controller = self  # set controller

        self.files_queue = None
        self.detection_progress = None
        self.progress_queue = None
        self.result_queue = None

        self.cancelled = False

    def check_params_validity(self):
        """
        Validates the processing parameters before starting the processing of the files and the plot of the figure.

        Returns
        -------
        bool
            True if parameters are valid, otherwise False with an error message.
        """
        plot_params_errors = []
        legend_errors = []
        figname_errors = []
        axes_errors = []
        if not self.view.vars["single ckbox"].get() and not self.view.vars["multiple ckbox"].get():
            plot_params_errors.append("Either 'single file' or 'multiple file' analysis must be selected")
        if self.view.vars["single ckbox"].get() and self.view.vars["multiple ckbox"].get():
            plot_params_errors.append("Either 'single file' or 'multiple file' analysis must be selected")

        if self.view.vars["single ckbox"].get() and not self.view.vars["single"].get():
            plot_params_errors.append("No file selected to analyze.")
        if self.view.vars["multiple ckbox"].get() and not self.view.vars["multiple"].get():
            plot_params_errors.append("No file selected to analyze.")

        if self.view.vars['select columns ckbox'].get():
            if not self.view.vars['select columns number'].get():
                plot_params_errors.append("You have to indicate a number of columns to select.")
            if self.view.vars['select columns mode'].get() == 'None':
                plot_params_errors.append("You have to select a mode for column selection.")

            if self.view.vars['select columns metric'].get() == 'None':
                plot_params_errors.append("You have to select a metric to use for the electrode selection.")

        targets = self.view.textboxes["targets"].get(1.0, ctk.END)
        if len(targets) == 0 and not self.view.vars["single ckbox"].get():
            plot_params_errors.append('At least one target is needed to plot')

        if float(self.view.vars["dead window"].get()) < 0:
            plot_params_errors.append('Dead window length must be a positive number.')

        if int(self.view.vars["sampling frequency"].get()) <= 0:
            plot_params_errors.append('Sampling frequency must be a positive number.')
        if float(self.view.vars["std threshold"].get()) < 0:
            plot_params_errors.append('Std threshold must be a positive number.')

        for key, textbox in self.view.textboxes.items():
            elements = textbox.get(1.0, ctk.END)
            for element in elements:
                fcs = ival.value_has_forbidden_character(element)
                if fcs:
                    plot_params_errors.append(f"Forbidden characters in '{element}' : {fcs}")

        # ---- axis errors
        axes_entry_keys = ["round y ticks", "n y ticks"]
        for key in axes_entry_keys:
            e = self.view.entries[key].error_message.get()
            if e:
                axes_errors.append(e)

        # ---- figname errors

        if plot_params_errors or axes_errors or figname_errors or legend_errors:
            errors = [error for errors in [plot_params_errors, axes_errors, figname_errors, legend_errors] for error in
                      errors]
            messagebox.showerror('Value Error', '\n'.join(errors))
            return False
        return True

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
        return n_file * n_col

    def compute_spike_thread_launcher(self):
        # fig, ax = self.view.figures["plot"]

        files = []
        start = datetime.now()

        if self.view.vars["single"].get():
            files.append(self.view.vars["single"].get())
        elif self.view.vars["multiple"].get():
            files = ff.get_all_files(self.model.parent_directory, to_include=self.model.to_include,
                                     to_exclude=self.model.to_exclude)
            yesno = messagebox.askyesno("Files found", f"{len(files)} files have been found using "
                                                       f"the multiple file sorting option."
                                                       f"\nProceed with the processing ?")
            if not yesno:
                return

        samples_per_target = {value: 0 for target, value in self.model.targets.items()}
        skiprow = 0
        if self.model.vars['behead ckbox']:
            skiprow = int(self.model.vars['behead'])

        example_dataframe = pd.read_csv(files[0], dtype=float, index_col=False, skiprows=skiprow)
        if self.model.vars['select columns ckbox']:
            n_cols = int(self.model.vars['select columns number'])
        else:
            n_cols = int(
                len([col for col in example_dataframe.columns if self.model.vars["except column"] not in col]))
        self.detection_progress = ProgressBar("Processing progression", app=self.view.app, controller=self)
        self.detection_progress.total_tasks = self.update_number_of_tasks(len(files), n_cols)
        self.detection_progress.start()
        self.detection_progress.update_task("Spike detection...")

        n_cpu = multiprocessing.cpu_count()
        # n_workers = 1
        if len(files) > int(0.7 * n_cpu):
            n_workers = 1 if int(0.7 * n_cpu) == 0 else int(0.7 * n_cpu)
        elif len(files) < int(0.7 * n_cpu):
            n_workers = len(files)
        else:
            n_workers = 1

        logger.debug("Using n workers for processing: ", n_workers)

        self.files_queue = multiprocessing.Queue()
        self.progress_queue = multiprocessing.Queue()
        self.result_queue = multiprocessing.Queue()

        # populate the queue with parameters combinations to test
        for file in files:
            self.files_queue.put(file)

            # add sentinel values
        for _ in range(n_workers):
            self.files_queue.put(None)

        columns_with_exception = [col for col in example_dataframe.columns if
                                  self.model.vars["except column"] not in col]
        lock = threading.Lock()
        all_prisoners = [SpikeDetectorProcess(self.model.vars,
                                              self.model.targets,
                                              n_cols,
                                              self.result_queue,
                                              self.files_queue,
                                              self.progress_queue,
                                              columns_with_exception,
                                              lock)
                         for _ in range(1)]

        for p in all_prisoners:
            logger.info(p)
            p.start()

        watch_dog = WatchDog(all_prisoners)
        watch_dog.start()
        results = {}
        finished_prisoners = 0

        results = {value: {col: [] for col in columns_with_exception} for target, value in self.model.targets.items()}
        while watch_dog.watching() and finished_prisoners != len(
                all_prisoners) and self.detection_progress.progress_window.winfo_exists():
            self.detection_progress.update_task("Threaded spike detection...")
            try:
                while not self.progress_queue.empty():
                    progress_item = self.progress_queue.get_nowait()
                    if progress_item:
                        self.detection_progress.increment_progress(progress_item)
                        logger.debug("increment progress")
            except Empty:
                pass

            try:
                while not self.result_queue.empty():
                    self.detection_progress.update_task("Storing results...")
                    detected_spikes, target = self.result_queue.get_nowait()  # Use get_nowait() to avoid blocking
                    if type(detected_spikes) is str:  # A Worker finished ! joining it
                        finished_prisoners += 1
                        logger.info("Prisoner finishing", detected_spikes, "finished prisoners:", finished_prisoners)

                    else:
                        for col in detected_spikes.keys():
                            results[target][col] += detected_spikes[col]
                        samples_per_target[target] += 1  # Store results dynamically
            except Empty:
                # No progress item was available; just continue looping.
                pass

            self.view.app.update_idletasks()

        if self.cancelled:
            logger.info("Spike detection has been cancelled ! Cleaning threads and queues")
            watch_dog.stop()
            # emptying queues
            while not self.files_queue.empty():
                self.files_queue.get_nowait()

            while not self.progress_queue.empty():
                self.progress_queue.get_nowait()

            while not self.result_queue.empty():
                self.result_queue.get_nowait()  # Use get_nowait() to avoid blocking

        else:
            self.detection_progress.update_task("Finishing threaded detection...")
            if finished_prisoners == len(all_prisoners):
                watch_dog.stop()
            while not self.progress_queue.empty():
                self.detection_progress.increment_progress(self.progress_queue.get_nowait())

            while not self.result_queue.empty():
                detected_spikes, target = self.result_queue.get_nowait()  # Use get_nowait() to avoid blocking
                for col in detected_spikes.keys():
                    results[target][col] += detected_spikes[col]
                samples_per_target[target] += 1  # Store results dynamically # Store results dynamically

            self.cancelled = True if any(
                [w.is_alive() for w in all_prisoners]) and not self.detection_progress.is_alive() else False

            self.detection_progress.update_task("Terminating threads...")
            for worker in all_prisoners:
                logger.info("joining ", worker.name)
                worker.join(timeout=5)
                if worker.is_alive():
                    logger.info("thread is alive, joining")
                    worker.join()
            watch_dog.join()
            logger.info("Watch dog is joined")

            self.model.spike_params["spike results"] = results

            self.draw_figure()

        if self.cancelled:
            messagebox.showinfo("Cancel Learning", "All workers properly terminated.")
        else:
            logger.info("All threads properly terminated.")

        self.cancelled = False

    def check_thread_status(self, thread):
        if thread.is_alive():
            self.view.app.after(500, self.check_thread_status, thread)  # Check again after 500ms
        else:
            logger.info("Thread finished!")  # Do any post-processing here

    def compute_spikes(self):
        # thread = threading.Thread(target=self.compute_spike_thread, daemon=True)
        if self.check_params_validity():
            for widgets in [self.view.ckboxes, self.view.entries, self.view.cbboxes, self.view.sliders, self.view.vars,
                            self.view.switches, self.view.textboxes, ]:
                self.update_params(widgets)
            self.compute_spike_thread_launcher()
            # thread.start()
            # self.view.app.after(500, self.check_thread_status, thread)  # Check if thread is done

    def check_plot_params_validity(self):
        """
        Validates the plot parameters before plotting the figure.

        Returns
        -------
        bool
            True if parameters are valid, otherwise False with an error message.
        """
        errors = []
        if not self.model.n_labels > -1:
            errors.append("You need to add data to plot.")

        indices = []
        for n_label in range(self.model.n_labels):
            index = self.view.vars[f"index {n_label}"].get()
            indices.append(index)

        if len(indices) != len(set(indices)):
            errors.append("Two data point can not have the same plot index.")

        if errors:
            messagebox.showerror("Not plottable", "\n".join(errors))
        return True if len(errors) == 0 else False

    def draw_figure(self):
        """
        Draws the Spike figure, setting up the plot, computing spikes, and rendering the visualization.
        """
        if self.check_plot_params_validity() and self.check_params_validity():
            for widgets in [self.view.ckboxes, self.view.entries, self.view.cbboxes, self.view.sliders, self.view.vars,
                            self.view.switches, self.view.textboxes, ]:
                self.update_params(widgets)

            fig, ax = plt.subplots(figsize=(4, 4))
            new_canvas = FigureCanvasTkAgg(fig, master=self.view.frames["plot frame"])
            new_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
            self.view.canvas["plot toolbar"].destroy()
            toolbar = NavigationToolbar2Tk(new_canvas,
                                           self.view.frames["plot frame"], pack_toolbar=False)
            toolbar.update()
            toolbar.grid(row=1, column=0, sticky='we')
            self.view.canvas["spike"].get_tk_widget().destroy()
            self.view.canvas["spike"] = new_canvas
            self.view.figures["spike"] = (fig, ax)
            ax.clear()

            x_ticks = []
            x_ticks_label = []
            results = self.model.spike_params["spike results"]
            all_spikes = {value: [] for t, value in self.model.targets.items()}
            for target in results.keys():
                for col in results[target].keys():
                    all_spikes[target] += results[target][col]

            ymin = 0
            ymax = -math.inf

            new_indices = {self.model.vars[f"label data {n_label}"]: int(self.model.vars[f"index {n_label}"])
                           for n_label in range(self.model.n_labels + 1)}
            inverted_new_indices = {v: k for k, v in new_indices.items()}
            label_order = [inverted_new_indices[key] for key in sorted(inverted_new_indices, key=int)]
            color_dict = {self.model.vars[f"label data {n_label}"]: self.model.vars[f"color {n_label}"]
                          for n_label in range(self.model.n_labels + 1)}

            for n_label in range(self.model.n_labels + 1):
                label = self.model.vars[f"label data {n_label}"]
                label_legend = self.model.vars[f"label data legend {n_label}"]
                index = self.model.vars[f"index {n_label}"]
                x_ticks_label.append(label_legend) if label_legend else x_ticks_label.append(label)
                x_ticks.append(index)

                for spike in all_spikes[label]:
                    if spike > ymax:
                        ymax = spike

                if self.model.cbboxes[f"plot type"] == "bar":
                    height = int(np.mean(all_spikes[label])) # / self.model.spike_params["samples_per_target"][label])
                    yerr = np.std(all_spikes[label]) if self.model.vars[f"error bar {index}"] else None
                    ax.bar(x=index, height=height,
                           yerr=yerr,
                           color=self.model.vars[f"color {n_label}"], )

                elif self.model.cbboxes[f"plot type"] == "violin":
                    sns.violinplot({k: v for k, v in all_spikes.items() if k in label_order}, order=label_order, ax=ax,
                                   palette=color_dict)

            for n_label in range(self.model.n_labels + 1):
                label = self.model.vars[f"label data {n_label}"]
                if self.model.ckboxes["show points"] == 1:
                    for spike in all_spikes[label]:
                        offset = 0.15
                        rand_index = random.uniform(new_indices[label] - offset,
                                                    new_indices[label] + offset)  # Add jitter
                        ax.scatter(x=rand_index, y=spike, color='black', alpha=0.7, s=15)

            # ---- LABELS
            ax.set_xlabel(self.model.vars["x label"],
                          fontdict={"font": self.model.vars["axes font"],
                                    "fontsize": self.model.vars["x label size"]})
            ax.set_ylabel(self.model.vars["y label"],
                          fontdict={"font": self.model.vars["axes font"],
                                    "fontsize": self.model.vars["y label size"]})
            ax.set_title(self.model.entries["title"],
                         fontdict={"font": self.model.cbboxes["title font"],
                                   "fontsize": self.model.vars["title size"]}, )

            # ----- TICKS
            ax.set_xticks(x_ticks, x_ticks_label)
            ax.tick_params(axis='x',
                           labelsize=self.model.vars["x ticks size"],
                           labelrotation=float(self.model.vars["x ticks rotation"]))
            bottom_limit, top_limit = ax.get_ylim()
            ymin = min(ymin, bottom_limit)
            ymax = max(ymax, top_limit)
            yticks = np.linspace(ymin, ymax, int(self.model.entries["n y ticks"]))
            rounded_yticks = list(np.around(np.array(yticks), int(self.model.entries["round y ticks"])))
            ax.set_ylim(bottom=min(rounded_yticks), top=max(rounded_yticks))
            ax.set_yticks(rounded_yticks)
            ax.tick_params(axis='y',
                           labelsize=self.model.vars["y ticks size"],
                           labelrotation=float(self.model.vars["y ticks rotation"]))
            # ---------- LEGEND
            # if self.model.ckboxes["show legend"]:
            #     if not self.model.vars["legend fontsize"] == '':
            #         if self.model.cbboxes["legend anchor"] == 'custom':
            #             ax.legend(loc='upper left',
            #                       bbox_to_anchor=(float(self.model.sliders["legend x pos"]),
            #                                       float(self.model.sliders["legend y pos"])),
            #                       draggable=bool(self.model.ckboxes["legend draggable"]),
            #                       ncols=int(self.model.entries["legend ncols"]),
            #                       fontsize=int(self.model.vars["legend fontsize"]),
            #                       framealpha=float(self.model.vars["legend alpha"]),
            #                       )
            #         else:
            #             ax.legend(loc=self.model.cbboxes["legend anchor"],
            #                       draggable=bool(self.model.ckboxes["legend draggable"]),
            #                       ncols=int(self.model.entries["legend ncols"]),
            #                       fontsize=int(self.model.vars["legend fontsize"]),
            #                       framealpha=float(self.model.vars["legend alpha"]),
            #                       )
            #
            #         for t, lh in zip(ax.get_legend().texts, ax.get_legend().legendHandles):
            #             t.set_alpha(float(self.model.vars["legend alpha"]))
            #             lh.set_alpha(float(self.model.vars["legend alpha"]))
            #
            # elif ax.get_legend():
            #     ax.get_legend().remove()

            self.view.figures["spike"] = (fig, ax)
            self.view.canvas["spike"].draw()
        else:
            messagebox.showerror("", "Missing data", )

    def trace_vars_to_model(self, key, *args):
        """
        Synchronizes UI variables with the model.

        Parameters
        ----------
        key : str
            The key of the variable being traced.
        *args : tuple
            Additional arguments passed by the trace callback.
        """
        if key in self.model.plot_general_settings.keys():
            self.model.plot_general_settings[key] = self.view.vars[key].get()
        elif key in self.model.plot_axes.keys():
            self.model.plot_axes[key] = self.view.vars[key].get()
        elif key in self.model.plot_legend.keys():
            self.model.plot_legend[key] = self.view.vars[key].get()
        elif key in self.model.spike_params.keys():
            self.model.spike_params[key] = self.view.vars[key].get()

    def select_parent_directory(self, strvar):
        """
        Opens a file dialog to select a parent directory and updates the model with the selected path.

        This method prompts the user to select a directory using a file dialog. If the user selects a
        valid directory, the method updates the provided `StringVar` with the directory path and stores
        it in the model's `parent_directory` attribute.

        Parameters
        ----------
        strvar : ctk.StringVar
            The tkinter or customtkinter StringVar to hold the selected directory path.

        Returns
        -------
        None
        """
        dirname = filedialog.askdirectory(mustexist=True, title="select directory")
        if type(strvar) == ctk.StringVar:
            strvar.set(dirname)
            self.model.parent_directory = dirname

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

    def select_single_file(self, display_in):
        """
        Opens a file dialog to select a file and updates the model with the selected path.

        This method prompts the user to select a file using a file dialog. If the user selects a
        valid file, the method updates the provided `StringVar` with the file path and stores
        it in the model's `single_file` attribute.

        Parameters
        ----------
        display_in : ctk.StringVar
            The tkinter or customtkinter StringVar to hold the selected directory path.

        Returns
        -------
        None
        """
        filename = filedialog.askopenfilename(title="Open file",
                                              filetypes=(("Tables", "*.txt *.xls *.xlsx *.csv"),))
        if type(display_in) == ctk.StringVar:
            display_in.set(filename)
            self.model.single_file = filename

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
            if type(list(widgets.values())[0]) == ctk.CTkCheckBox:
                for key, value in widgets.items():
                    local_dict[key] = value.get()
                self.model.ckboxes.update(local_dict)
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

    def add_label_data(self, scrollable_frame):
        """
        Adds a new label entry to the provided scrollable frame, allowing the user to configure a label, its
        associated properties, and display settings.

        This method checks if the model has targets and if the number of labels is within the maximum allowed.
        If so, it creates a set of UI components for label configuration such as comboboxes, color selectors,
        and legend entries, and places them in the scrollable frame. It also updates the relevant view dictionaries
        for managing these UI elements.

        Parameters
        ----------
        scrollable_frame : ctk.CTkFrame
            The frame in which the label data widgets will be added. This frame should support scrolling to accommodate
            the added widgets.

        Returns
        -------
        None
            This method does not return a value. It updates the UI by adding widgets to the provided frame and storing
            widget references in the model and view.

        Raises
        ------
        messagebox.showinfo
            If the maximum number of labels has been reached, an informational message will be displayed.
        messagebox.showerror
            If no targets have been specified in the model, an error message will be shown.

        Notes
        -----
        - The method ensures that only a valid number of labels are added (up to the maximum allowed).
        - A series of widgets are created, including comboboxes for selecting the label, error bars, index, and color settings.
        - The method also manages separators in the UI for better layout.
        - The relevant UI elements are stored in the `view` and `model` for further interaction.
        """

        if self.model.targets:
            if self.model.n_labels + 1 <= self.model.max_n_labels:
                targets = sorted(set(list(self.model.targets.values())))
                self.model.n_labels += 1
                n_labels = self.model.n_labels
                column = n_labels + self.model.n_labels_offset
                # label_data_subframe = ctk.CTkFrame(master=scrollable_frame, )
                # row separator
                n_labels_label = ctk.CTkLabel(master=scrollable_frame, text=f"DATA: {n_labels}")
                # row separator
                # row separator
                label_var = tk.StringVar(value=targets[n_labels] if n_labels < len(targets) else 0)
                labels_cbbox = tk.ttk.Combobox(master=scrollable_frame, values=targets, state='readonly',
                                               textvariable=label_var)
                # row separator
                labels_legend_var = tk.StringVar(value='')
                labels_legend_entry = ErrEntry(master=scrollable_frame, textvariable=labels_legend_var)
                # row separator
                index_cbbox_var = ctk.IntVar(value=n_labels if n_labels < len(targets) else 0)
                index_cbbox = tk.ttk.Combobox(master=scrollable_frame, textvariable=index_cbbox_var,
                                              values=[str(x) for x in range(len(targets))], state='readonly')
                # row separator
                error_bar_var = tk.StringVar(value='None')
                error_bar_cbbox = tk.ttk.Combobox(master=scrollable_frame, values=["None", 'std'],
                                                  textvariable=error_bar_var)
                # row separator
                color_var = tk.StringVar(value='green')
                color_button = ctk.CTkButton(master=scrollable_frame, textvariable=color_var,
                                             fg_color=color_var.get(), text_color='black')

                # ----- MANAGE WIDGETS
                n_labels_label.grid(row=1, column=column, sticky="we", padx=2)
                labels_cbbox.grid(row=4, column=column, sticky='we', padx=2)
                labels_legend_entry.grid(row=6, column=column, sticky='we', padx=2)
                index_cbbox.grid(row=8, column=column, sticky='we', padx=2)
                error_bar_cbbox.grid(row=10, column=column, sticky='we', padx=2)
                color_button.grid(row=12, column=column, sticky='we', padx=2)

                # --------------- MANAGE SEPARATORS
                general_params_separators_indices = [0, 2, 3, 5, 7, 9, 11, 13, ]
                general_params_vertical_separator_ranges = [(0, 14), ]
                for r in range(general_params_separators_indices[-1] + 2):
                    if r in general_params_separators_indices:
                        sep = Separator(master=scrollable_frame, orient='h')
                        sep.grid(row=r, column=column, columnspan=1, sticky='ew')
                # for couple in general_params_vertical_separator_ranges:
                #     general_v_sep = Separator(master=scrollable_frame, orient='v')
                #     general_v_sep.grid(row=couple[0], column=column, rowspan=couple[1] - couple[0], sticky='ns')

                # ----- CONFIGURE WIDGETS
                color_button.configure(command=partial(self.view.select_color, view=self.view,
                                                       selection_button_name=f'color {n_labels}'))

                scrollable_frame.grid_columnconfigure(index=column, weight=1)
                # ------- STORE WIDGETS

                # self.view.labels_subframes[str(n_labels)] = label_data_subframe
                self.view.cbboxes[f"label data {n_labels}"] = labels_cbbox
                self.view.cbboxes[f"error bar {n_labels}"] = error_bar_cbbox
                self.view.cbboxes[f"index {n_labels}"] = index_cbbox
                self.view.vars[f"label data {n_labels}"] = label_var
                self.view.vars[f"error bar {n_labels}"] = error_bar_var
                self.view.vars[f"index {n_labels}"] = index_cbbox_var
                self.view.vars[f"label data legend {n_labels}"] = labels_legend_var
                self.view.buttons[f"color {n_labels}"] = color_button
                self.view.vars[f"color {n_labels}"] = color_var
                # ----- TRACE
            else:
                messagebox.showinfo("", f"Maximum number of labels {self.model.max_n_labels} reached.")
        else:
            messagebox.showerror("Missing Values", "No targets indicated")
            return False

    @staticmethod
    def clear_column(parent, column):
        """
        Clears all widgets in a specific column of a parent widget's grid layout.

        This method iterates through all child widgets of the provided parent widget and checks the grid placement
        of each widget. If the widget is placed in the specified column, it will be destroyed, effectively removing
        it from the UI.

        Parameters
        ----------
        parent : tkinter.Widget
            The parent widget containing the grid of widgets. This should be a widget that uses the grid layout manager.

        column : int
            The index of the column from which the widgets will be removed.

        Returns
        -------
        None
            This method does not return any value. It directly manipulates the UI by destroying widgets in the specified column.

        Notes
        -----
        - Only widgets that are placed in the specified column will be removed.
        - If no widgets are placed in the specified column, this method has no effect.
        """

        for widget in parent.winfo_children():
            grid_info = widget.grid_info()
            if grid_info and int(grid_info['column']) == column:
                widget.destroy()

    def remove_label_data(self, ):
        """
        Removes the label data UI components and related entries from the model.

        This method clears the UI components corresponding to the current label data, removes the associated widgets
        from the grid layout, and deletes the related entries from the model and view dictionaries. It also decrements
        the number of labels in the model.

        Returns
        -------
        None
            This method does not return any value. It directly modifies the UI and model by removing label-related data.

        Notes
        -----
        - The method assumes that the number of labels is non-negative (`n_labels >= 0`).
        - It clears widgets and updates dictionaries to ensure the UI and model remain synchronized.
        """

        n_labels = self.model.n_labels
        column = n_labels + self.model.n_labels_offset
        if n_labels >= 0:
            self.clear_column(self.view.scrollable_frames["data"], column)

            # remove the frame from self.view.labels_subframes
            # self.view.labels_subframes[str(n_labels)].destroy()
            # del self.view.labels_subframes[str(n_labels)]

            # destroying all items related in dicts
            del self.view.buttons[f"color {n_labels}"]
            del self.view.cbboxes[f"label data {n_labels}"]
            del self.view.vars[f"color {n_labels}"]
            del self.view.cbboxes[f"error bar {n_labels}"]
            del self.view.cbboxes[f"index {n_labels}"]
            del self.view.vars[f"error bar {n_labels}"]
            del self.view.vars[f"index {n_labels}"]
            del self.view.vars[f"label data legend {n_labels}"]
            self.model.n_labels -= 1

    def load_config(self, ):
        """
        Loads a configuration file and updates the model.

        This method prompts the user to select a configuration file with the `.skcfg` extension. If a valid file is selected,
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

        f = filedialog.askopenfilename(title="Open file", filetypes=(("Spike analysis config", "*.skcfg"),))
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
        - The file is saved with the `.skcfg` extension by default, but the user can specify a different filename or location.
        """
        if self.check_params_validity():
            for widgets in [self.view.ckboxes, self.view.entries, self.view.cbboxes, self.view.sliders, self.view.vars,
                            self.view.switches, self.view.textboxes, self.view.labels, self.view.labels_subframes]:
                self.update_params(widgets)

            f = filedialog.asksaveasfilename(defaultextension=".skcfg",
                                             filetypes=[("Spike analysis config", "*.skcfg"), ])
            if f:
                self.model.save_model(path=f, )

    def export_data(self):
        """
        Exports the spike detection data to two CSV file.

        This method allows the user to save the spike detection data contained in `self.model.spike_params["spike results"]`
        to a CSV file. It prompts the user to choose a file location and name, and then exports the data as a CSV file.
        If successful, it shows a success message; otherwise, it handles exceptions and displays an error message.

        Parameters
        ----------
        None

        Returns
        -------
        None
            This method does not return any value. It saves the spike detection data to a CSV file.

        Exceptions
        ----------
        - If an error occurs during the file-saving process, an error message is displayed, and the error is printed to the console.

        Notes
        -----
        - The data is converted to a pandas DataFrame and exported using the `.to_csv()` method.
        - The default filename is `spike_detection_export.csv`, but the user can specify a different name or location.
        """
        is_error = False
        f = ''
        try:
            f = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("Table", "*.csv"), ],
                                             initialfile="spike_detection_export")
            indices = [target for target in self.model.spike_params["spike results"].keys()]
            columns = [col for col in self.model.spike_params["spike results"][indices[0]].keys()]

            data = np.zeros((len(indices), len(columns)), dtype=object)

            for itarget, target in enumerate(self.model.spike_params["spike results"].keys()):
                for icol, col in enumerate(self.model.spike_params["spike results"][target].keys()):
                    item = self.model.spike_params["spike results"][target][col]
                    logger.debug(item)
                    data[itarget, icol] = item

            df = pd.DataFrame(index=indices,
                              columns=columns, dtype=object, data=data)
            logger.debug(df)

            if '.csv' not in f:
                f += '.csv'
            df.to_csv(f, index=False)

        except Exception as e:
            messagebox.showerror("", "An error has occurred while saving count.")
            logger.error(e)
            is_error = True

        if not is_error:
            messagebox.showinfo("", "Files correctly saved")
