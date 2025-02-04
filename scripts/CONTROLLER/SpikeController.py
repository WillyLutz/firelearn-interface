import multiprocessing
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

class SpikeController:
    def __init__(self, view, ):
        self.model = SpikeModel()
        self.view = view
        self.view.controller = self  # set controller
        self.progress = None
    
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
        
        targets = self.view.textboxes["targets"].get(1.0, ctk.END)
        if len(targets)==0 and not self.view.vars["single ckbox"].get():
            plot_params_errors.append('At least one target is needed to plot')
            
        if self.view.vars["dead window"].get() < 0:
            plot_params_errors.append('Dead window length must be a positive number.')
        
        if self.view.vars["sampling frequency"].get() <= 0:
            plot_params_errors.append('Sampling frequency must be a positive number.')
        if self.view.vars["std threshold"].get() < 0:
            plot_params_errors.append('Std threshold must be a positive number.')
        
        for key, textbox in self.view.textboxes.items():
            elements = textbox.get(1.0, ctk.END)
            for element in elements:
                fcs = ival.value_has_forbidden_character(element)
                if fcs:
                    plot_params_errors.append(f"Forbidden characters in '{element}' : {fcs}")
        
        
        # ---- legend errors
        legend_entry_keys = ["legend ncols", "dpi"]
        for key in legend_entry_keys:
            e = self.view.entries[key].error_message.get()
            if e:
                legend_errors.append(e)
        
        # ---- axis errors
        axes_entry_keys = ["round x ticks", "round y ticks", "n x ticks", "n y ticks"]
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
    
    def load_plot_dataset(self, ):
        filename = filedialog.askopenfilename(title="Open file",
                                              filetypes=(("Tables", "*.txt *.csv"),))
        if filename:
            # fig, ax = self.view.figures["plot"]
            # ax.clear()
            for n in range(self.model.n_ydata + 1):
                self.remove_ydata()
            
            df = pd.read_csv(filename)
            self.model.dataset = df
            self.model.dataset_path = filename
            self.view.vars["load dataset"].set(filename)
            
            columns = list(df.columns)
            self.view.cbboxes["xdata"].configure(values=columns)
            
            label_col = columns[0]
            for col in columns:
                if 'label' in col or 'target' in col:  # try to auto-detect the label column
                    label_col = col
            self.view.cbboxes["xdata"].set(label_col)
            
            ydata_curves = {key: value for (key, value) in self.view.cbboxes.items() if "ydata " in key}
            for key, value in ydata_curves.items():
                value.configure(values=columns)
                value.set(columns[-1])
    
    def compute_spikes(self):
        if self.check_params_validity():
            for widgets in [self.view.ckboxes, self.view.entries, self.view.cbboxes, self.view.sliders, self.view.vars,
                            self.view.switches, self.view.textboxes, ]:
                self.update_params(widgets)
            
            # fig, ax = self.view.figures["plot"]
            
            
            files = []
            start = datetime.now()
            
            if self.view.vars["single"].get():
                files.append(self.view.vars["single"].get())
            elif self.view.vars["multiple"].get():
                files = ff.get_all_files(self.model.parent_directory, to_include=self.model.to_include,
                                         to_exclude=self.model.to_exclude)
            
            all_spikes = {target: [] for target in self.model.targets.keys()}
            print(all_spikes)
            # for file in files:
            #     target = [x for x in self.model.targets.keys() if x in file][0]
            #     df = pd.read_csv(file, skiprows=6, dtype=float, )
            #     # df = data_processing.top_n_electrodes(df, 30, "TimeStamp [µs]") todo : add column selection
            #
            #     n_workers = 10
            #     worker_ranges = np.linspace(0, len(df.columns), n_workers + 1).astype(int)
            #
            #     params_list = []
            #     all_workers = []
            #     manager = multiprocessing.Manager()
            #     return_dict = manager.dict()
            #
            #     for n_worker in range(n_workers):
            #         low_index = worker_ranges[n_worker]
            #         high_index = worker_ranges[n_worker + 1]
            #         # sub_array = df_array[:, low_index:high_index]
            #
            #         worker = SpikeDetectorProcess(file,
            #                                       df.columns[low_index:high_index],
            #                                       self.model.vars["std threshold"],
            #                                       self.model.vars["sampling frequency"],
            #                                       self.model.vars["dead window"],
            #                                       return_dict)
            #         worker.name = f"worker_{n_worker}"
            #         worker.start()
            #         all_workers.append(worker)
            #
            #     for worker in all_workers:
            #         worker.join()
            #
            #     detected_spikes = dict(return_dict.items())
            #     all_spikes[target].append(np.sum(list(detected_spikes.values())))
            self.model.spike_params["all_spikes"] = all_spikes
            
            self.draw_figure()
            
    def draw_figure(self):
        fig, ax = plt.subplots(figsize=(4, 4))
        new_canvas = FigureCanvasTkAgg(fig, master=self.view.frames["plot frame"])
        new_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
        self.view.canvas["plot toolbar"].destroy()
        toolbar = NavigationToolbar2Tk(new_canvas,
                                       self.view.frames["plot frame"], pack_toolbar=False)
        toolbar.update()
        toolbar.grid(row=1, column=0, sticky='we')
        self.view.canvas["plot"].get_tk_widget().destroy()
        self.view.canvas["plot"] = new_canvas
        self.view.figures["plot"] = (fig, ax)
        
        x_ticks = []
        x_ticks_label = []
        for index, (key, value) in enumerate(self.model.spike_params["all_spikes"].items()):
            x_ticks.append(index)
            x_ticks_label.append(key)
            ax.bar(x=index, height=np.sum(value), yerr=np.std(value))
        
        ax.set_xticks(x_ticks, x_ticks_label)
        self.view.figures["plot"] = (fig, ax)
        self.view.canvas["plot"].draw()
    
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
            
            targets = sorted(set(list(self.model.targets.values())))
            
            self.model.n_labels += 1
            n_labels = self.model.n_labels
            label_data_subframe = ctk.CTkFrame(master=scrollable_frame, )
            
            # row separator 0
            # row separator 1
            n_labels_label = ctk.CTkLabel(master=label_data_subframe, text=f"DATA: {n_labels}")
            # row separator 3
            # row separator 4
            
            labels_label = ctk.CTkLabel(master=label_data_subframe, text="Label:")
            label_var = tk.StringVar(value=targets[0])
            labels_cbbox = tk.ttk.Combobox(master=label_data_subframe, values=targets, state='readonly',
                                           textvariable=label_var)
            # row separator 6
            labels_legend_label = ctk.CTkLabel(master=label_data_subframe, text="Legend label:")
            labels_legend_var = tk.StringVar(value='')
            labels_legend_entry = ErrEntry(master=label_data_subframe, textvariable=labels_legend_var)
            
            # row separator 8
            index_label = ctk.CTkLabel(master=label_data_subframe, text="Index:")
            index_cbbox_var = ctk.IntVar(value=0)
            index_cbbox = tk.ttk.Combobox(master=label_data_subframe, textvariable=index_cbbox_var,
                                          values=[str(x) for x in range(len(targets))],)
            
            # row separator 10
            error_bar_label = ctk.CTkLabel(master=label_data_subframe, text="Error bar")
            error_bar_var = tk.StringVar(value='None')
            error_bar_cbbox = tk.ttk.Combobox(master=label_data_subframe, values=["None", 'std'],
                                              textvariable=error_bar_var)
            
            # row separator 12
            
            color_label = ctk.CTkLabel(master=label_data_subframe, text="Color:")
            color_var = tk.StringVar(value='green')
            color_button = ctk.CTkButton(master=label_data_subframe, textvariable=color_var,
                                         fg_color=color_var.get(), text_color='black')
            # row separator 14
            # ----- MANAGE WIDGETS
            label_data_subframe.grid(row=n_labels + self.model.n_labels_offset,
                                     column=0, sticky='nsew', pady=25, columnspan=3)
            
            n_labels_label.grid(row=2, column=0, columnspan=3, sticky="we")
            
            labels_label.grid(row=5, column=0, sticky='w')
            labels_cbbox.grid(row=5, column=2, sticky='we')
            labels_legend_label.grid(row=7, column=0, sticky='w')
            labels_legend_entry.grid(row=7, column=2, sticky='we')
            index_label.grid(row=9, column=0, sticky='w')
            index_cbbox.grid(row=9, column=2, sticky='we')
            error_bar_label.grid(row=11, column=0, sticky='w')
            error_bar_cbbox.grid(row=11, column=2, sticky='we')
            color_label.grid(row=13, column=0, sticky='w')
            color_button.grid(row=13, column=2, sticky='we')
            
            # --------------- MANAGE SEPARATORS
            general_params_separators_indices = [0, 1, 3, 4, 6, 8, 10, 12, 14, ]
            general_params_vertical_separator_ranges = [(4, 14), ]
            for r in range(general_params_separators_indices[-1] + 2):
                if r in general_params_separators_indices:
                    sep = Separator(master=label_data_subframe, orient='h')
                    sep.grid(row=r, column=0, columnspan=3, sticky='ew')
            for couple in general_params_vertical_separator_ranges:
                general_v_sep = Separator(master=label_data_subframe, orient='v')
                general_v_sep.grid(row=couple[0], column=1, rowspan=couple[1] - couple[0], sticky='ns')
            
            # ----- CONFIGURE WIDGETS
            color_button.configure(command=partial(self.view.select_color, view=self.view,
                                                   selection_button_name=f'color {n_labels}'))
            
            
            # ------- STORE WIDGETS
            
            self.view.labels_subframes[str(n_labels)] = label_data_subframe
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
            # for key, widget in {f'color {n_labels}': color_var, f"error bar {n_labels}": error_bar_var,
            #                     f"index {n_labels}": index_cbbox_var,
            #                     f'label data {n_labels}': label_var,
            #                     f'label data legend {n_labels}': labels_legend_var,
            #                     }.items():
            #     self.model.plot_data[key] = widget.get()
            #     widget.trace("w", partial(self.trace_vars_to_model, key))
        
        else:
            messagebox.showerror("Missing Values", "No targets indicated")
            return False
    
    def remove_label_data(self, ):
        n_labels = self.model.n_labels
        
        if n_labels >= 0:
            for child in self.view.labels_subframes[str(n_labels)].winfo_children():
                child.destroy()
            
            # remove the frame from self.view.labels_subframes
            self.view.labels_subframes[str(n_labels)].destroy()
            del self.view.labels_subframes[str(n_labels)]
            
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