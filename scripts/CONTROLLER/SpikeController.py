from functools import partial

import numpy as np
import pandas as pd
from PIL import Image
from matplotlib import pyplot as plt
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from scripts.CONTROLLER.MainController import MainController
from scripts.CONTROLLER.ProgressBar import ProgressBar
from scripts.MODEL.SpikeModel import SpikeModel
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from scripts import params as p
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
    
    def save_config(self, ):
        if self.check_params_validity():
            f = filedialog.asksaveasfilename(defaultextension=".spkcfg",
                                             filetypes=[("Analysis - Simple plot", "*.spkcfg"), ])
            if f:
                self.model.save_model(path=f, )
    
    def load_config(self, ):
        f = filedialog.askopenfilename(title="Open file", filetypes=(("Analysis - Simple plot", "*.spkcfg"),))
        if f:
            if self.model.load_model(path=f):
                self.update_view_from_model()
                # todo : does not work because widgets are not created while the top-levels are not created
    
    def update_view_from_model(self, ):
        
        for key, value in self.model.plot_data.items():
            if key in self.view.vars.keys():
                self.view.vars[key].set(value)
        for key, value in self.model.plot_legend.items():
            if key in self.view.vars.keys():
                self.view.vars[key].set(value)
        for key, value in self.model.plot_axes.items():
            if key in self.view.vars.keys():
                self.view.vars[key].set(value)
        for key, value in self.model.plot_general_settings.items():
            if key in self.view.vars.keys():
                self.view.vars[key].set(value)
    
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
    
    def add_ydata(self, scrollable_frame):
        if self.model.dataset_path:
            df = pd.read_csv(self.model.dataset_path, index_col=False)
            columns = list(df.columns)
            
            self.model.n_ydata += 1
            n_ydata = self.model.n_ydata
            
            ydata_subframe = ctk.CTkFrame(master=scrollable_frame, )
            self.view.ydata_subframes[str(n_ydata)] = ydata_subframe
            
            n_ydata_label = ctk.CTkLabel(master=ydata_subframe, text=f"Y-DATA : {self.model.n_ydata}")
            
            ydata_label = ctk.CTkLabel(master=ydata_subframe, text="Y-data column:")
            ydata_cbbox_var = tk.StringVar(value=columns[-1])
            ydata_cbbox = tk.ttk.Combobox(master=ydata_subframe, values=columns, state='readonly',
                                          textvariable=ydata_cbbox_var)
            
            self.view.cbboxes[f"ydata {n_ydata}"] = ydata_cbbox
            self.view.vars[f"ydata {n_ydata}"] = ydata_cbbox_var
            
            ydata_legend_label = ctk.CTkLabel(master=ydata_subframe, text="Legend label:")
            ydata_legend_var = tk.StringVar()
            ydata_legend_entry = ctk.CTkEntry(master=ydata_subframe, textvariable=ydata_legend_var)
            
            self.view.entries[f"ydata legend {n_ydata}"] = ydata_legend_entry
            self.view.vars[f"ydata legend {n_ydata}"] = ydata_legend_var
            
            linestyle_label = ctk.CTkLabel(master=ydata_subframe, text="Linestyle:")
            linestyle_var = tk.StringVar(value=p.DEFAULT_LINESTYLE)
            linestyle_cbbox = tk.ttk.Combobox(master=ydata_subframe, values=list(p.LINESTYLES.keys()), state='readonly',
                                              textvariable=linestyle_var)
            
            self.view.cbboxes[f"linestyle {n_ydata}"] = linestyle_cbbox
            self.view.vars[f"linestyle {n_ydata}"] = linestyle_var
            
            linewidth_label = ctk.CTkLabel(master=ydata_subframe, text="Linewidth:")
            linewidth_var = tk.StringVar(value=p.DEFAULT_LINEWIDTH)
            linewidth_entry = ErrEntry(master=ydata_subframe, textvariable=linewidth_var)
            
            self.view.entries[f"linewidth {n_ydata}"] = linewidth_entry
            self.view.vars[f"linewidth {n_ydata}"] = linewidth_var
            
            color_label = ctk.CTkLabel(master=ydata_subframe, text="Color:")
            color_var = tk.StringVar(value=p.DEFAULT_COLOR)
            color_button = ctk.CTkButton(master=ydata_subframe, textvariable=color_var,
                                         fg_color=color_var.get(), text_color='black')
            
            self.view.buttons[f"color {n_ydata}"] = color_button
            self.view.vars[f"color {n_ydata}"] = color_var
            
            alpha_label = ctk.CTkLabel(master=ydata_subframe, text="Alpha:")
            alpha_var = tk.DoubleVar(value=p.DEFAULT_ALPHA)
            alpha_slider = ctk.CTkSlider(master=ydata_subframe, from_=0, to=1, number_of_steps=10, variable=alpha_var)
            alpha_value_label = ctk.CTkLabel(master=ydata_subframe, textvariable=alpha_var)
            
            self.view.vars[f"alpha {n_ydata}"] = alpha_var
            self.view.sliders[f"alpha {n_ydata}"] = alpha_slider
            
            color_button.configure(command=partial(self.view.select_color, view=self.view,
                                                   selection_button_name=f'color {n_ydata}'))
            
            ydata_subframe.grid_columnconfigure(0, weight=10)
            ydata_subframe.grid_columnconfigure(1, weight=1)
            ydata_subframe.grid_columnconfigure(2, weight=10)
            
            # --------------- MANAGE WIDGETS
            
            ydata_subframe.grid(row=n_ydata + self.model.n_ydata_offset, column=0, sticky='nsew', pady=25, columnspan=3)
            n_ydata_label.grid(row=2, column=0, columnspan=3, sticky='we')
            ydata_label.grid(row=5, column=0, sticky='w')
            ydata_cbbox.grid(row=5, column=2, sticky='we')
            ydata_legend_label.grid(row=7, column=0, sticky='w')
            ydata_legend_entry.grid(row=7, column=2, sticky='we')
            linestyle_label.grid(row=9, column=0, sticky='w')
            linestyle_cbbox.grid(row=9, column=2, sticky='we')
            linewidth_label.grid(row=11, column=0, sticky='w')
            linewidth_entry.grid(row=11, column=2, sticky='we')
            color_label.grid(row=13, column=0, sticky='w')
            color_button.grid(row=13, column=2, sticky='we')
            alpha_label.grid(row=15, column=0, sticky='w')
            alpha_slider.grid(row=15, column=2, sticky='we')
            alpha_value_label.grid(row=15, column=0, sticky='e')
            
            # --------------- MANAGE SEPARATORS
            general_params_separators_indices = [0, 1, 3, 4, 6, 8, 10, 12, 14, 16]
            general_params_vertical_separator_ranges = [(4, 17), ]
            for r in range(general_params_separators_indices[-1] + 2):
                if r in general_params_separators_indices:
                    sep = Separator(master=ydata_subframe, orient='h')
                    sep.grid(row=r, column=0, columnspan=3, sticky='ew')
            for couple in general_params_vertical_separator_ranges:
                general_v_sep = Separator(master=ydata_subframe, orient='v')
                general_v_sep.grid(row=couple[0], column=1, rowspan=couple[1] - couple[0], sticky='ns')
            
            # ----- ENTRY VALIDATION
            
            linewidth_entry.configure(validate='focus',
                                      validatecommand=(
                                          self.view.register(partial(self.view.parent_view.parent_view.is_positive_int,
                                                                     linewidth_entry)),
                                          '%P'))
        
        else:
            messagebox.showerror("Missing Values", "No dataset loaded")
            return False
    
    def remove_ydata(self):
        n_ydata = self.model.n_ydata
        if n_ydata >= 0:
            
            # destroying all widgets related
            for child in self.view.ydata_subframes[str(n_ydata)].winfo_children():
                child.destroy()
            
            # remove the frame from self.view.ydata_subframes
            self.view.ydata_subframes[str(n_ydata)].destroy()
            del self.view.ydata_subframes[str(n_ydata)]
            
            # destroying all items related in dicts
            del self.view.entries[f"ydata legend {n_ydata}"]
            del self.view.entries[f"linewidth {n_ydata}"]
            del self.view.buttons[f"color {n_ydata}"]
            del self.view.cbboxes[f"ydata {n_ydata}"]
            del self.view.cbboxes[f"linestyle {n_ydata}"]
            del self.view.vars[f"linewidth {n_ydata}"]
            del self.view.vars[f"color {n_ydata}"]
            del self.view.vars[f"alpha {n_ydata}"]
            del self.view.vars[f"ydata legend {n_ydata}"]
            del self.view.vars[f"linestyle {n_ydata}"]
            del self.view.vars[f"ydata {n_ydata}"]
            del self.view.sliders[f"alpha {n_ydata}"]
            
            self.model.n_ydata -= 1
    def spikes_number_of_tasks(self, n_files,):
        reading_file = 1
        finalizing = 1
        spikes_detect = 11
        return n_files * (reading_file + spikes_detect)  + finalizing
        
    def compute_spikes(self):
        if self.check_params_validity():
            self.update_params(self.view.entries)
            self.update_params(self.view.ckboxes)
            self.update_params(self.view.vars)
            self.update_params(self.view.textboxes)
            
            
            
            files = []
            if self.view.vars["single"].get():
                files.append(self.view.vars["single"].get())
            elif self.view.vars["multiple"].get():
                all_files = ff.get_all_files(self.model.parent_directory)

                for file in all_files:
                    if all(i in file for i in self.model.to_include) and (
                            not any(e in file for e in self.model.to_exclude)):
                        files.append(file)
            
            targets_list = self.view.textboxes["targets"].get(1.0, ctk.END).split("\n")
            targets_list = [x for x in targets_list if x]
            targets = {t.split('-')[0].strip(): t.split('-')[1].strip() for t in targets_list }
            spikes_detailed_per_target = {v: [] for k, v in targets.items()}
            if not files:
                messagebox.showerror('Missing files', 'No files have been selected using the parameters.')
            
            n_steps_per_file = 10
            self.progress = ProgressBar("Spikes detection", app=self.view.app)
            self.progress.total_tasks = self.spikes_number_of_tasks(len(files))
            self.progress.start()
            
            for file in files:
                self.progress.update_task("Reading file")
                print(file)
                file_target = ''
                for t in targets.keys():
                    if t in file:
                        file_target = targets[t]
                if not file_target:
                    messagebox.showerror('Missing value', 'No target has been assigned to a file.')
                    break
                    
               
                skiprows = 0 if not self.model.vars["ckbox behead"] else int(self.model.vars["behead"])
                df = pd.read_csv(file, skiprows=skiprows)
                df_array = np.array(df)
                self.progress.increment_progress(1)
                self.progress.update_task("Spikes detection")
                for i_col in range(1, len(df.columns)):
                    col_array = df_array[:, i_col]
                    if np.any(col_array):
                        std = col_array.std()
                        detected_indices = []
                        i = 0
                        
                        while i < len(col_array):
                            # Check if the value is above or below the threshold
                            if (col_array[i] <= -self.view.vars["std threshold"].get() * std
                                    or col_array[i] >= self.view.vars["std threshold"].get() * std):
                                detected_indices.append(i)  # Record the spike index
                                dead_samples = int(self.view.vars['dead window'].get() * self.view.vars['sampling frequency'].get())
                                i += dead_samples  # Skip the dead time window
                            else:
                                i += 1  # Move to the next index
                        if len(detected_indices) > 0:
                            print(df.columns[i_col], len(detected_indices))
                            spikes_detailed_per_target[file_target].append(len(detected_indices)) # increment spike count
                self.progress.increment_progress(1)
                

            
            self.progress.update_task('Draw figure')
            spikes_per_target = {k: sum(v) for k, v in spikes_detailed_per_target.items()}
            std_per_target = {k: np.array(v).std() for k, v in spikes_detailed_per_target.items()}
            
            self.model.spikes_per_target = spikes_per_target
            self.model.spikes_detailed_per_target = spikes_detailed_per_target
            self.model.std_per_target = std_per_target
            
            target_index = 0
            for target in self.model.std_per_target.keys():
                self.model.xlabels_indexes[target] = target_index
                target_index += 1
            print(self.model.xlabels_indexes)
            self.draw_figure()
            self.progress.increment_progress(1)

            
    
    
    def draw_figure(self):
        if self.check_params_validity():
            
            targets = self.model.xlabels_indexes.keys()
            duplicates = ival.dict_has_duplicate_values(self.model.xlabels_indexes)
            if duplicates:
                print(duplicates)
                messagebox.showerror("Duplicate Values", f"The labels {duplicates} have duplicates index values.")
            else:
                self.update_params(self.view.entries)
                self.update_params(self.view.ckboxes)
                self.update_params(self.view.vars)
                self.update_params(self.view.textboxes)
                # fig, ax = self.view.figures["plot"]
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
                
                ibar = 0.5
                print(self.model.xlabels_indexes)
                
                ticks_labels = [(t, i + ibar) for t, i in self.model.xlabels_indexes.items()]
                ticks_labels = sorted(ticks_labels, key=lambda x: x[1])
                
                print(ticks_labels)
                for target, index in ticks_labels:
                    plt.bar(x=index+ibar, height=self.model.spikes_per_target[target], color='gray',)

                
                ax.set_xticks([i[1] for i in ticks_labels], [i[0] for i in ticks_labels])
                
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
    
    def trace_label_indices(self, ti):
        target = self.view.entries[f"label index {ti}"].get()
        self.model.xlabels_indexes[target] = self.view.vars[f"label index {ti}"].get()
    
    def update_label_sorter(self,):
        # destroying all widgets related
        for child in self.view.scrollable_frames["label sorter"].winfo_children():
            child.destroy()
        
        label_sorter_separators_indices = [0, 1, 3, 4, ]
        targets = self.model.xlabels_indexes.keys()
        ti = 0
        if targets:
            while ti < len(targets):
                target_entry = ctk.CTkEntry(master=self.view.scrollable_frames["label sorter"], text=targets[ti])
                index_var = ctk.StringVar(value=self.model.xlabels_indexes[targets[ti]])
                index_cbbox = ttk.Combobox(master=self.view.scrollable_frames["label sorter"], values=[str(x) for x in range(len(targets))],
                                           textvariable=index_var, state='readonly')
                
                target_entry.grid(row=5+2*ti, column=0, sticky='we')
                index_cbbox.grid(row=5+2*ti, column=2, sticky='we')
                
                label_sorter_separators_indices.append(5+2*ti+1)
                
                self.view.entries[f"label index {ti}"] = target_entry
                self.view.vars[f"label index {ti}"] = index_var
                
                index_var.trace('w', partial(self.trace_label_indices, ti))
    
            
            n_labels = len(self.model.xlabels_indexes.keys())
            for r in range(label_sorter_separators_indices[-1] + 2):
                if r in label_sorter_separators_indices:
                    sep = Separator(master=self.view.scrollable_frames["label sorter"], orient='h')
                    sep.grid(row=r, column=0, columnspan=3, sticky='ew')
            
            general_v_sep = Separator(master=self.view.scrollable_frames["label sorter"], orient='v')
            general_v_sep.grid(row=5, column=1, rowspan=(n_labels * 2 - 5), sticky='ns')