import math
import multiprocessing
import random
import threading
from multiprocessing import Queue
from datetime import datetime
from functools import partial

import numpy as np
import pandas as pd
from PIL import Image
from matplotlib import pyplot as plt
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from scripts.CONTROLLER import data_processing
from scripts.CONTROLLER.MainController import MainController
from scripts.CONTROLLER.ProgressBar import ProgressBar
from scripts.MODEL.SpikeModel import SpikeModel
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from scripts import params as p
from scripts.PROCESSES.SpikeDetector import SpikeDetectorProcess
from scripts.WIDGETS.ErrEntry import ErrEntry
from scripts.WIDGETS.Separator import Separator
from scripts.params import resource_path
from fiiireflyyy import files as ff
import scripts.CONTROLLER.input_validation as ival
import seaborn as sns

class SpikeController:
    def __init__(self, view, ):
        self.model = SpikeModel()
        self.view = view
        self.view.controller = self  # set controller
        self.progress = None
        self.queue = Queue()
    
    def save_figure(self, fig):
        filepath = filedialog.asksaveasfilename(title="Open file", filetypes=(("Image", "*.png"),))
        if filepath:
            fig.savefig(filepath, dpi=int(self.model.plot_general_settings["dpi"]))
    
    def check_params_validity(self):
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
        if len(targets)==0 and not self.view.vars["single ckbox"].get():
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
        return n_file * n_col
    
    def compute_spike_thread(self):
        # fig, ax = self.view.figures["plot"]
        
        files = []
        start = datetime.now()
        
        if self.view.vars["single"].get():
            files.append(self.view.vars["single"].get())
        elif self.view.vars["multiple"].get():
            files = ff.get_all_files(self.model.parent_directory, to_include=self.model.to_include,
                                     to_exclude=self.model.to_exclude)
        all_spikes = {value: [] for target, value in self.model.targets.items()}
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
        self.progress = ProgressBar("Processing progression", app=self.view.app)
        self.progress.total_tasks = self.update_number_of_tasks(len(files), n_cols)
        self.progress.start()
        self.progress.update_task("Spike detection...")
        for file in files:
            target, value = [(k, v) for k, v in self.model.targets.items() if k in file][0]
            samples_per_target[value] += 1
            if not target:
                messagebox.showerror("Missing Value", "No corresponding target has been found in the "
                                                      "file name.")
                break
            if self.model.vars["behead ckbox"]:
                df = pd.read_csv(file, skiprows=int(self.model.vars["behead"]), dtype=float, index_col=False)
            else:
                df = pd.read_csv(file, dtype=float, index_col=False)
                
            if self.model.vars["select columns ckbox"]:
                df = data_processing.top_n_electrodes(df, n_cols,  self.model.vars["except column"])
                
            columns_with_exception = [col for col in df.columns if self.model.vars["except column"] not in col]
            
            n_workers = 8 if 8 < len(df.columns)/2 else int(len(df.columns)/2)
            worker_ranges = np.linspace(0, len(columns_with_exception), n_workers + 1).astype(int)
            
            params_list = []
            all_workers = []
            manager = multiprocessing.Manager()
            return_dict = manager.dict()
            
            for n_worker in range(n_workers):
                low_index = worker_ranges[n_worker]
                high_index = worker_ranges[n_worker + 1]
                # sub_array = df_array[:, low_index:high_index]
                
                if high_index > low_index: # so no workers have empty datasets
                    worker = SpikeDetectorProcess(df.loc[:, columns_with_exception[low_index:high_index]].values,
                                                  columns_with_exception[low_index:high_index],
                                                  float(self.model.vars["std threshold"]),
                                                  int(self.model.vars["sampling frequency"]),
                                                  float(self.model.vars["dead window"]),
                                                  return_dict,
                                                  self.queue,)
                    worker.name = f"worker_{n_worker}"
                    worker.start()
                    all_workers.append(worker)
            
            while any([w.is_alive() for w in all_workers]):
                if not self.queue.empty():
                    self.progress.increment_progress(self.queue.get(timeout=1))
            
            for worker in all_workers:
                worker.join(timeout=10)
                if worker.is_alive():
                    worker.terminate()
            detected_spikes = dict(return_dict.items())
            all_spikes[value].append(np.sum(list(detected_spikes.values())))
        self.model.spike_params["all_spikes"] = all_spikes
        self.model.spike_params["samples_per_target"] = samples_per_target
        
    
    def compute_spikes(self):
        if self.check_params_validity():
            for widgets in [self.view.ckboxes, self.view.entries, self.view.cbboxes, self.view.sliders, self.view.vars,
                            self.view.switches, self.view.textboxes, ]:
                self.update_params(widgets)
            
            self.compute_spike_thread()
            # thread = threading.Thread(name='spike', target=self.compute_spike_thread, daemon=True)
            # thread.start()
            # thread.join()
            self.draw_figure()
            
       
    def check_plot_params_validity(self):
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
        return True if len(errors)==0 else False
        
    def draw_figure(self):
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
            all_spikes = self.model.spike_params["all_spikes"]
            ymin = 0
            ymax = -math.inf
            
            new_indices = {self.model.vars[f"label data {n_label}"]: int(self.model.vars[f"index {n_label}"])
                           for n_label in range(self.model.n_labels+1)}
            inverted_new_indices = {v: k for k, v in new_indices.items()}
            label_order = [inverted_new_indices[key] for key in sorted(inverted_new_indices, key=int)]
            color_dict = {self.model.vars[f"label data {n_label}"]:self.model.vars[f"color {n_label}"]
                          for n_label in range(self.model.n_labels+1)}
            
            for n_label in range(self.model.n_labels+1):
                label = self.model.vars[f"label data {n_label}"]
                label_legend = self.model.vars[f"label data legend {n_label}"]
                index = self.model.vars[f"index {n_label}"]
                x_ticks_label.append(label_legend) if label_legend else x_ticks_label.append(label)
                x_ticks.append(index)
                
                height = int(np.sum(all_spikes[label])/self.model.spike_params["samples_per_target"][label])
                for spike in all_spikes[label]:
                    if spike > ymax:
                        ymax = spike
                    
                if self.model.cbboxes[f"plot type"] == "bar":
                    yerr = np.std(all_spikes[label]) if self.model.vars[f"error bar {index}"] else None
                    ax.bar(x=index, height=height,
                           yerr=yerr,
                           color=self.model.vars[f"color {n_label}"],)

                elif self.model.cbboxes[f"plot type"] == "violin":
                    sns.violinplot(all_spikes, order=label_order, ax=ax, palette=color_dict)
                
            for n_label in range(self.model.n_labels + 1):
                label = self.model.vars[f"label data {n_label}"]
                if self.model.ckboxes["show points"] == 1:
                    for spike in all_spikes[label]:
                        offset = 0.15
                        rand_index = random.uniform(new_indices[label] - offset, new_indices[label] + offset)  # Add jitter
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
            
            
            yticks = np.linspace(ymin, ymax, int(self.model.entries["n y ticks"]))
            rounded_yticks = list(np.around(np.array(yticks), int(self.model.entries["round y ticks"])))
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
        if key in self.model.plot_general_settings.keys():
            self.model.plot_general_settings[key] = self.view.vars[key].get()
        elif key in self.model.plot_axes.keys():
            self.model.plot_axes[key] = self.view.vars[key].get()
        elif key in self.model.plot_legend.keys():
            self.model.plot_legend[key] = self.view.vars[key].get()
        elif key in self.model.spike_params.keys():
            self.model.spike_params[key] = self.view.vars[key].get()
    
    def validate_step(self, step):
        img = ctk.CTkImage(dark_image=Image.open(resource_path(f"data/firelearn_img/{step}_green.png")),
                           size=(120, 120))
        self.view.image_buttons[step].configure(image=img)
        self.view.step_check[step] = 1
    
    def invalidate_step(self, step):
        img = ctk.CTkImage(dark_image=Image.open(resource_path(f"data/firelearn_img/{step}_red.png")), size=(120, 120))
        self.view.image_buttons[str(step)].configure(image=img)
        self.view.step_check[step] = 0

    def select_parent_directory(self, strvar):
        dirname = filedialog.askdirectory(mustexist=True, title="select directory")
        if type(strvar) == ctk.StringVar:
            strvar.set(dirname)
            self.model.parent_directory = dirname
    
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
        
    def select_single_file(self, display_in):
        filename = filedialog.askopenfilename(title="Open file",
                                              filetypes=(("Tables", "*.txt *.xls *.xlsx *.csv"),))
        if type(display_in) == ctk.StringVar:
            display_in.set(filename)
            self.model.single_file = filename
            
    def update_params(self, widgets: dict, ):
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
        for widget in parent.winfo_children():
            grid_info = widget.grid_info()
            if grid_info and int(grid_info['column']) == column:
                widget.destroy()
    
    def remove_label_data(self, ):
        
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
        f = filedialog.askopenfilename(title="Open file", filetypes=(("Spike analysis config", "*.skcfg"),))
        if f:
            if self.model.load_model(path=f):
                self.update_view_from_model()
    
    def save_config(self, ):
        if self.check_params_validity():
            for widgets in [self.view.ckboxes, self.view.entries, self.view.cbboxes, self.view.sliders, self.view.vars,
                            self.view.switches, self.view.textboxes, self.view.labels, self.view.labels_subframes]:
                self.update_params(widgets)
            
            f = filedialog.asksaveasfilename(defaultextension=".skcfg",
                                             filetypes=[("Spike analysis config", "*.skcfg"), ])
            if f:
                self.model.save_model(path=f, )
                
    def export_data(self):
        try:
            f = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("Table", "*.csv"), ],
                                             initialfile="spike_detection_export.csv")
            df = pd.DataFrame.from_dict(self.model.spike_params["all_spikes"], orient="index").transpose()
            
            df.to_csv(f, index=False)
            
            messagebox.showinfo("", "File correctly saved")
        except Exception as e:
            messagebox.showerror("", "An error has occurred while saving.")
            print(e)
        
        