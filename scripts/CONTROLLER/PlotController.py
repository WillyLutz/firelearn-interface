from functools import partial

import numpy as np
import pandas as pd
from PIL import Image
from matplotlib import pyplot as plt
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from scripts.MODEL.PlotModel import PlotModel
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from scripts import params as p
from scripts.WIDGETS.ErrEntry import ErrEntry
from scripts.WIDGETS.Separator import Separator
from scripts.params import resource_path


class PlotController:
    def __init__(self, view, ):
        self.model = PlotModel()
        self.view = view
        self.view.controller = self  # set controller
        self.progress = None
    
    def save_figure(self, fig):
        """
        Saves the given figure to a user-selected file.

        Parameters
        ----------
        fig : matplotlib.figure.Figure
            The figure object to be saved.
        """
        filepath = filedialog.asksaveasfilename(title="Open file", filetypes=(("Image", "*.png"),))
        if filepath:
            fig.savefig(filepath, dpi=int(self.model.plot_general_settings["dpi"]))
    
    def check_params_validity(self):
        """
        Validates the plotting parameters before generating the plot.

        Returns
        -------
        bool
            True if parameters are valid, otherwise False with an error message.
        """
        plot_params_errors = []
        legend_errors = []
        figname_errors = []
        axes_errors = []
        
        # ---- plot params errors
        
        if self.model.n_ydata < 0:
            plot_params_errors.append("At least one y data is needed to plot.")
        
        if not self.model.dataset_path:
            plot_params_errors.append("No dataset loaded")
        
        plotparams_entry_keys = [f"linewidth {n}" for n in range(0, self.model.n_ydata+1)] \
            if self.model.n_ydata >= 0 else []
        for key in plotparams_entry_keys:
            e = self.view.entries[key].error_message.get()
            if e:
                plot_params_errors.append(e)
        
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
        # nothing to check for the moment
        
        if plot_params_errors or axes_errors or figname_errors or legend_errors:
            errors = [error for errors in [plot_params_errors, axes_errors, figname_errors, legend_errors] for error in
                      errors]
            messagebox.showerror('Value Error', '\n'.join(errors))
            return False
        return True
    
    
    def save_config(self, ):
        """
        Saves the current plot configuration to a file.

        The function first checks the validity of parameters before proceeding with the save operation.
        """
        if self.check_params_validity():
            f = filedialog.asksaveasfilename(defaultextension=".pltcfg",
                                             filetypes=[("Analysis - Simple plot", "*.pltcfg"), ])
            if f:
                self.model.save_model(path=f, )
    
    def load_config(self, ):
        """
        Loads plot configuration settings from a user-selected file.

        If successfully loaded, updates the view with the stored settings.
        """
        f = filedialog.askopenfilename(title="Open file", filetypes=(("Analysis - Simple plot", "*.pltcfg"),))
        if f:
            if self.model.load_model(path=f):
                self.update_view_from_model()
                # todo : does not work because widgets are not created while the top-levels are not created
    
    def update_view_from_model(self, ):
        """
        Synchronizes the UI elements with the model's stored plot settings.
        """
        
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
        """
        Loads a dataset from a user-selected file and updates UI elements.

        If a dataset is selected, it updates available columns for plotting.
        """
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
        """
        Adds a new Y-axis data selection to the UI.

        Parameters
        ----------
        scrollable_frame : tk.Frame
            The frame where Y-data selection widgets will be added.
        """
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
            
            ydata_subframe.grid(row=n_ydata+self.model.n_ydata_offset, column=0, sticky='nsew', pady=25, columnspan=3)
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
                                    self.view.register(partial(self.view.parent_view.parent_view.is_positive_int, linewidth_entry)),
                                    '%P'))

        else:
            messagebox.showerror("Missing Values", "No dataset loaded")
            return False
    
    def remove_ydata(self):
        """
        Removes the most recently added Y-data selection from the UI and the model.
        """
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
            
            
    
    def draw_figure(self):
        """
        Generates and displays the plot using the selected dataset and parameters.

        If validation checks pass, updates the figure and toolbar in the UI.
        """
        # todo: if validation
        
        if self.check_params_validity():
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
            if self.model.n_ydata >= 0:
                ax.clear()
                # ----- PLOT
                df = self.model.dataset
                for n_ydata in range(self.model.n_ydata + 1):
                    ax.plot(df[self.view.vars["xdata"].get()],
                            df[self.view.vars[f"ydata {n_ydata}"].get()],
                            label=self.view.vars[f"ydata legend {n_ydata}"].get(),
                            linestyle=self.view.vars[f"linestyle {n_ydata}"].get(),
                            linewidth=self.view.vars[f"linewidth {n_ydata}"].get(),
                            color=self.view.vars[f"color {n_ydata}"].get(),
                            alpha=self.view.vars[f"alpha {n_ydata}"].get(),
                            )
                
                # ----- TITLE
                ax.set_title(self.model.plot_general_settings["title"],
                             fontdict={"font": self.model.plot_general_settings["title font"],
                                       "fontsize": self.model.plot_general_settings["title size"], })
                
                # ---- LABELS
                
                ax.set_xlabel(self.model.plot_axes["x label"],
                              fontdict={"font": self.model.plot_axes["axes font"],
                                        "fontsize": self.model.plot_axes["x label size"]})
                ax.set_ylabel(self.model.plot_axes["y label"],
                              fontdict={"font": self.model.plot_axes["axes font"],
                                        "fontsize": self.model.plot_axes["y label size"]})
                
                # ---- TICKS
                
                first_x = ax.lines[0].get_xdata()
                first_y = ax.lines[0].get_ydata()
                xmin = min(first_x)
                xmax = max(first_x)
                ymin = min(first_y)
                ymax = max(first_y)
                for x in range(self.model.n_ydata + 1):
                    # handle = plt.gca()
                    line = ax.lines[x]
                    x_data = line.get_xdata()
                    y_data = line.get_ydata()
                    
                    if min(x_data) < xmin:
                        xmin = min(x_data)
                    if max(x_data) > xmax:
                        xmax = max(x_data)
                    if min(y_data) < ymin:
                        ymin = min(y_data)
                    if max(y_data) > ymax:
                        ymax = max(y_data)
                
                if all([self.model.plot_axes["n x ticks"], self.model.plot_axes["round x ticks"],
                        self.model.plot_axes["n y ticks"], self.model.plot_axes["round y ticks"]]):
                    n_xticks = int(self.model.plot_axes["n x ticks"])
                    xstep = (int(xmax) - int(xmin)) / (int(n_xticks) - 1)
                    xtick = xmin
                    xticks = []
                    for i in range(n_xticks - 1):
                        xticks.append(xtick)
                        xtick += xstep
                    xticks.append(xmax)
                    rounded_xticks = list(np.around(np.array(xticks), int(self.model.plot_axes["round x ticks"])))
                    ax.set_xticks(rounded_xticks)
                    ax.tick_params(axis='x',
                                   labelsize=self.model.plot_axes["x ticks size"],
                                   labelrotation=float(self.model.plot_axes["x ticks rotation"]))
                    
                    n_yticks = int(self.model.plot_axes["n y ticks"])
                    ystep = (int(ymax) - int(ymin)) / (int(n_yticks) - 1)
                    ytick = ymin
                    yticks = []
                    for i in range(n_yticks - 1):
                        yticks.append(ytick)
                        ytick += ystep
                    yticks.append(ymax)
                    rounded_yticks = list(np.around(np.array(yticks), int(self.model.plot_axes["round y ticks"])))
                    ax.set_yticks(rounded_yticks)
                    ax.tick_params(axis='y',
                                   labelsize=self.model.plot_axes["y ticks size"],
                                   labelrotation=float(self.model.plot_axes["y ticks rotation"]))
                
                # ---- LEGEND
                if self.model.plot_legend["show legend"]:
                    if not self.model.plot_legend["legend fontsize"] == '':
                        if self.model.plot_legend["legend anchor"] == 'custom':
                            ax.legend(loc='upper left',
                                      bbox_to_anchor=(float(self.model.plot_legend["legend x pos"]),
                                                      float(self.model.plot_legend["legend y pos"])),
                                      draggable=bool(self.model.plot_legend["legend draggable"]),
                                      ncols=int(self.model.plot_legend["legend ncols"]),
                                      fontsize=int(self.model.plot_legend["legend fontsize"]),
                                      framealpha=float(self.model.plot_legend["legend alpha"]),
                                      )
                        else:
                            ax.legend(loc=self.model.plot_legend["legend anchor"],
                                      draggable=bool(self.model.plot_legend["legend draggable"]),
                                      ncols=int(self.model.plot_legend["legend ncols"]),
                                      fontsize=int(self.model.plot_legend["legend fontsize"]),
                                      framealpha=float(self.model.plot_legend["legend alpha"]),
                                      )
                        
                        for t, lh in zip(ax.get_legend().texts, ax.get_legend().legendHandles):
                            t.set_alpha(float(self.model.plot_legend["legend alpha"]))
                            lh.set_alpha(float(self.model.plot_legend["legend alpha"]))
                
                elif ax.get_legend():
                    ax.get_legend().remove()
                
            else:
                ax.clear()
            self.view.figures["plot"] = (fig, ax)
            self.view.canvas["plot"].draw()
    
    def trace_vars_to_model(self, key, *args):
        """
        Updates the model whenever a UI variable changes.

        Parameters
        ----------
        key : str
            The key associated with the changed variable.
        *args : tuple
            Additional arguments passed by the trace callback.
        """
        if key in self.model.plot_general_settings.keys():
            self.model.plot_general_settings[key] = self.view.vars[key].get()
        elif key in self.model.plot_axes.keys():
            self.model.plot_axes[key] = self.view.vars[key].get()
        elif key in self.model.plot_legend.keys():
            self.model.plot_legend[key] = self.view.vars[key].get()
    

    

