import random
from functools import partial

import numpy as np
import pandas as pd
from fiiireflyyy.learn import confidence_ellipse
from matplotlib import pyplot as plt
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from scripts.MODEL.PcaModel import PcaModel
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from scripts import params as p
from scripts.WIDGETS.ErrEntry import ErrEntry
from scripts.WIDGETS.Separator import Separator


class PcaController:
    def __init__(self, view, ):
        self.model = PcaModel()
        self.view = view
        self.view.controller = self  # set controller
        self.progress = None
    
    def dummy_figure(self):
        fig, ax = plt.subplots(figsize=(p.DEFAULT_FIGUREWIDTH, p.DEFAULT_FIGUREHEIGHT))
        t = np.arange(0, 3, .01)
        ax.plot(t, random.randint(1, 4) *
                np.sin(random.randint(1, 4) * np.pi * t))
        ax.set_xlabel("time [s]")
        ax.set_ylabel("f(t)")
        
        return fig, ax
    
    @staticmethod
    def fit_pca(dataframe: pd.DataFrame, n_components=3, label_column="label"):
        features = dataframe.loc[:, dataframe.columns != label_column].columns
        x = dataframe.loc[:, features].values
        x = StandardScaler().fit_transform(x)  # normalizing the features
        pca = PCA(n_components=n_components)
        principalComponent = pca.fit_transform(x)
        principal_component_columns = [f"principal component {i + 1}" for i in range(n_components)]
        
        pcdf = pd.DataFrame(data=principalComponent
                            , columns=principal_component_columns, )
        pcdf.reset_index(drop=True, inplace=True)
        dataframe.reset_index(drop=True, inplace=True)
        
        pcdf[label_column] = dataframe[label_column]
        
        return pca, pcdf, pca.explained_variance_ratio_
    
    @staticmethod
    def apply_pca(pca, dataframe, label_column="label"):
        features = dataframe.loc[:, dataframe.columns != label_column].columns
        x = dataframe.loc[:, features].values
        x = StandardScaler().fit_transform(x)  # normalizing the features
        transformed_ds = pca.transform(x)
        transformed_df = pd.DataFrame(data=transformed_ds,
                                      columns=[f"principal component {i + 1}" for i in range(transformed_ds.shape[1])])
        
        transformed_df.reset_index(drop=True, inplace=True)
        dataframe.reset_index(drop=True, inplace=True)
        transformed_df[label_column] = dataframe[label_column]
        return transformed_df
    
    def draw_figure(self):
        """
        Draws the PCA figure, setting up the plot, applying PCA, and rendering the visualization.
        """
        if self.check_params_validity():
            fig, ax = self._initialize_canvas()
            pcdf_applied, ratio = self._fit_and_apply_pca()
            self._plot_data(ax, pcdf_applied, ratio)
            self._set_labels(ax, ratio)
            self._set_ticks(ax)
            self._set_legend(ax)
            self.view.canvas["pca"].draw()
    
    def _initialize_canvas(self):
        """
        Initializes the Matplotlib figure and toolbar for the PCA plot.

        Returns
        -------
        tuple
            The figure and axis objects.
        """
        fig, ax = plt.subplots(figsize=(4, 4))
        new_canvas = FigureCanvasTkAgg(fig, master=self.view.frames["pca frame"])
        new_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
        self.view.canvas["pca toolbar"].destroy()
        toolbar = NavigationToolbar2Tk(new_canvas, self.view.frames["pca frame"], pack_toolbar=False)
        toolbar.update()
        toolbar.grid(row=1, column=0, sticky='we')
        self.view.canvas["pca"] = new_canvas
        self.view.figures["pca"] = (fig, ax)
        return fig, ax
    
    def _fit_and_apply_pca(self):
        """
        Fits PCA on selected data and applies transformation.

        Returns
        -------
        tuple
            Transformed PCA dataframe and explained variance ratio.
        """
        df = self.model.dataset
        label_column = self.view.vars["label column"].get()
        labels_to_fit = [self.model.plot_data[f"label data {yi}"] for yi in range(self.model.n_labels + 1) if
                         self.view.vars[f"fit {yi}"].get()]
        labels_to_apply = [self.model.plot_data[f"label data {yi}"] for yi in range(self.model.n_labels + 1) if
                           self.model.plot_data[f"apply {yi}"]]
        
        df_fit = df[df[label_column].isin(labels_to_fit)]
        n_components = int(self.model.plot_data["n components"])
        pca, pcdf_fit, ratio = self.fit_pca(df_fit, n_components=n_components, label_column=label_column)
        df_apply = df[df[label_column].isin(labels_to_apply)]
        pcdf_applied = self.apply_pca(pca, df_apply, label_column=label_column)
        return pcdf_applied, [round(x * 100, 2) for x in ratio]
    
    def _plot_data(self, ax, pcdf_applied, ratio):
        """
        Plots PCA transformed data onto the provided axis.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The axis to plot on.
        pcdf_applied : pandas.DataFrame
            The transformed PCA data.
        ratio : list
            Explained variance ratio in percentage.
        """
        label_column = self.view.vars["label column"].get()
        n_components = int(self.model.plot_data["n components"])
        
        for yi in range(self.model.n_labels + 1):
            current_label = self.view.cbboxes[f"label data {yi}"].get()
            x_data = pcdf_applied.loc[pcdf_applied[label_column] == current_label, pcdf_applied.columns[0]]
            y_data = pcdf_applied.loc[pcdf_applied[label_column] == current_label, pcdf_applied.columns[1]]
            label = self.view.vars[f"label data legend {yi}"].get() or self.view.vars[f"label data {yi}"].get()
            ax.scatter(x_data, y_data,
                       s=int(self.view.vars[f"marker size {yi}"].get()),
                       marker=p.MARKERS[self.view.vars[f"marker style {yi}"].get()],
                       color=self.view.vars[f"color {yi}"].get(),
                       alpha=self.view.vars[f"alpha {yi}"].get(),
                       label=label)
            
            if self.view.vars["ellipsis"].get():
                ax.scatter(np.mean(x_data), np.mean(y_data), marker="+", color=self.view.vars[f"color {yi}"].get(),
                           linewidth=2, s=160)
                confidence_ellipse(x_data, y_data, ax, n_std=1.0, alpha=self.model.plot_data["ellipsis alpha"],
                                   color=self.view.vars[f"color {yi}"].get(), fill=False, linewidth=2)
    
    def _set_labels(self, ax, ratio):
        """
        Sets labels and title for the PCA plot.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The axis to set labels on.
        ratio : list[float]
            Explained variance ratio in percentage.
        """
        show_ratiox = f' ({ratio[0]}%)' if self.view.vars["show ratio"].get() else ''
        show_ratioy = f' ({ratio[1]}%)' if self.view.vars["show ratio"].get() else ''
        ax.set_xlabel(self.model.plot_axes["x label"] + show_ratiox,
                      fontdict={"font": self.model.plot_axes["axes font"],
                                "fontsize": self.model.plot_axes["x label size"]})
        ax.set_ylabel(self.model.plot_axes["y label"] + show_ratioy,
                      fontdict={"font": self.model.plot_axes["axes font"],
                                "fontsize": self.model.plot_axes["y label size"]})
        ax.set_title(self.model.plot_general_settings["title"],
                     fontdict={"font": self.model.plot_general_settings["title font"],
                               "fontsize": self.model.plot_general_settings["title size"]})
    
    def _set_ticks(self, ax):
        """
        Configures the x and y ticks for the PCA plot.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The axis to set ticks on.
        """
        ax.tick_params(axis='x', labelsize=self.model.plot_axes["x ticks size"],
                       labelrotation=float(self.model.plot_axes["x ticks rotation"]))
        ax.tick_params(axis='y', labelsize=self.model.plot_axes["y ticks size"],
                       labelrotation=float(self.model.plot_axes["y ticks rotation"]))
    
    def _set_legend(self, ax):
        """
        Configures the legend for the PCA plot if enabled.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
            The axis to set the legend on.
        """
        if self.model.plot_legend["show legend"]:
            ax.legend(loc=self.model.plot_legend["legend anchor"],
                      fontsize=int(self.model.plot_legend["legend fontsize"]),
                      framealpha=float(self.model.plot_legend["legend alpha"]))
        elif ax.get_legend():
            ax.get_legend().remove()
            
    def input_validation_plot(self):
        """
        Validates user input for plot settings.

        Ensures that numerical inputs are valid and within appropriate ranges.
        Displays error messages if any validation check fails.

        Returns
        -------
        bool
            True if all inputs are valid, otherwise False.
        """
        plt_entries = {key: value for (key, value) in self.view.entries.items() if "plt" in key}
        # todo : input validation /!\ multiple y
        
        # if float(plt_entries["linewidth"].get()) < 0:
        #     messagebox.showerror("Value error", "Line width must be positive.")
        #
        # for key, value in {"linewidth": "Line width", "n x ticks": "Number of x ticks",
        #                    "n y ticks": "Number of y ticks", "dpi": "Figure dpi"}.items():
        #     if not ival.is_number(plt_entries["linewidth"].get()):
        #         messagebox.showerror("Value error", f"{value} must be a number.")
        #         return False
        #
        # for key, value in {"round x ticks": "Round x ticks", "round y ticks": "Round y ticks",
        #                    "dpi": "Figure dpi"}.items():
        #     if not ival.isint(plt_entries[key].get()):
        #         messagebox.showerror("Value error", f"{value} must be a positive integer.")
        #         return False
        #
        # for key, value in {"linewidth": "Line width", }.items():
        #     if ival.value_is_empty_or_none(plt_entries[key].get()):
        #         messagebox.showerror("Value error", f"{value} can not be empty or None")
        #         return False
        #
        # if int(self.view.entries["n x ticks"].get()) < 2:
        #     messagebox.showerror("Value error", "Can not have les than 2 ticks.")
        
        return True
    
    def save_figure(self, fig):
        """
        Saves the given figure to a file selected by the user.

        Parameters
        ----------
        fig : matplotlib.figure.Figure
            The figure to be saved.
        """
        filepath = filedialog.asksaveasfilename(title="Open file", filetypes=(("Image", "*.png"),))
        if filepath:
            fig.savefig(filepath, dpi=int(self.view.entries["dpi"].get()))
    
    def check_params_validity(self):
        """
        Checks the validity of user-defined parameters.

        Returns
        -------
        bool
            True if all parameters are valid, otherwise False.
        """
        errors = []
        
        for key, entry in self.view.entries.items():
            if type(entry) == ErrEntry:
                if entry.error_message.get() != '':
                    errors.append(f"{key} : {entry.error_message.get()}")
        
        if self.model.n_labels < 0:
            errors.append("Need data to plot.")
        if errors:
            messagebox.showerror('Value Error', '\n'.join(errors))
            return False
        
        return True
    
    def save_config(self, ):
        """
        Saves the current configuration settings to a file.

        The function first checks the validity of parameters before allowing the save operation.
        """
        
        if self.check_params_validity():
            f = filedialog.asksaveasfilename(defaultextension=".pltcfg",
                                             filetypes=[("Analysis - pca", "*.pcacfg"), ])
            if f:
                self.model.save_model(path=f, )
    
    def load_config(self, ):
        """
        Loads configuration settings from a selected file.

        Updates the view with the loaded settings if the model is successfully loaded.
        """
        
        f = filedialog.askopenfilename(title="Open file", filetypes=(("Analysis - pca", "*.pcacfg"),))
        if f:
            if self.model.load_model(path=f):
                self.update_view_from_model()  # todo : does not work with multiple y :
    
    def update_view_from_model(self, ):
        """
        Updates the user interface view using data from the model.

        Synchronizes stored values for plot settings, legend, axes, and general settings.
        """
        for key, value in self.model.plot_data.items():
            self.view.vars[key].set(value)
        for key, value in self.model.plot_legend.items():
            self.view.vars[key].set(value)
        for key, value in self.model.plot_axes.items():
            self.view.vars[key].set(value)
        for key, value in self.model.plot_general_settings.items():
            self.view.vars[key].set(value)
    
    def load_plot_dataset(self, ):
        """
        Loads a dataset for plotting.

        The user selects a dataset file, which is then read into a pandas DataFrame.
        Updates relevant UI elements with dataset information.
        """
        filename = filedialog.askopenfilename(title="Open file",
                                              filetypes=(("Tables", "*.txt *.csv"),))
        if filename:
            df = pd.read_csv(filename)
            self.model.dataset_path = filename
            self.model.dataset = df
            self.view.vars["load dataset"].set(filename)
            
            columns = list(df.columns)
            self.view.cbboxes["label column"].configure(values=columns)
            
            label_col = columns[0]
            for col in columns:
                if 'label' in col or 'target' in col:  # try to auto-detect the label column
                    label_col = col
            self.view.cbboxes["label column"].set(label_col)
            
            label_data_curves = {key: value for (key, value) in self.view.cbboxes.items() if "label data " in key}
            for key, value in label_data_curves.items():
                all_labels = sorted(set(list(df[label_col])))
                value.configure(values=all_labels)
                value.set(all_labels[0])
    
    def add_label_data(self, scrollable_frame):
        """
        Adds label-related data to the UI.

        Parameters
        ----------
        scrollable_frame : tk.Frame
            The frame to which the label-related data elements will be added.
        """
        if self.model.dataset_path:
            df = self.model.dataset
            label_col = self.view.vars["label column"].get()
            all_labels = sorted(set(list(df[label_col])))
            
            self.model.n_labels += 1
            n_labels = self.model.n_labels
            label_data_subframe = ctk.CTkFrame(master=scrollable_frame,)
            
            # row separator 0
            # row separator 1
            n_labels_label = ctk.CTkLabel(master=label_data_subframe, text=f"DATA: {n_labels}")
            # row separator 3
            # row separator 4

            labels_label = ctk.CTkLabel(master=label_data_subframe, text="Label:")
            label_var = tk.StringVar(value=all_labels[0])
            labels_cbbox = tk.ttk.Combobox(master=label_data_subframe, values=all_labels, state='readonly',
                                           textvariable=label_var)
            # row separator 6

            fit_var = tk.IntVar(value=1)
            apply_var = tk.IntVar(value=1)
            fit_ckbox = ctk.CTkCheckBox(master=label_data_subframe, text="Fit", variable=fit_var)
            apply_ckbox = ctk.CTkCheckBox(master=label_data_subframe, text="Apply", variable=apply_var)
            # row separator 8

            labels_legend_label = ctk.CTkLabel(master=label_data_subframe, text="Legend label:")
            labels_legend_var = tk.StringVar(value='')
            labels_legend_entry = ErrEntry(master=label_data_subframe, textvariable=labels_legend_var)
            # row separator 10

            markerstyle_label = ctk.CTkLabel(master=label_data_subframe, text="Markers:")
            markerstyle_var = tk.StringVar(value='point')
            markerstyle_cbbox = tk.ttk.Combobox(master=label_data_subframe, values=list(sorted(p.MARKERS.keys())),
                                                state='readonly', textvariable=markerstyle_var)
            # row separator 12

            markersize_label = ctk.CTkLabel(master=label_data_subframe, text="Marker size:")
            markersize_var = tk.StringVar(value='1')
            markersize_entry = ErrEntry(master=label_data_subframe, textvariable=markersize_var)
            # row separator 14

            color_label = ctk.CTkLabel(master=label_data_subframe, text="Color:")
            color_var = tk.StringVar(value='green')
            color_button = ctk.CTkButton(master=label_data_subframe, textvariable=color_var,
                                         fg_color=color_var.get(), text_color='black')
            # row separator 16

            alpha_label = ctk.CTkLabel(master=label_data_subframe, text="Alpha:")
            alpha_var = tk.DoubleVar(value=p.DEFAULT_ALPHA)
            alpha_slider = ctk.CTkSlider(master=label_data_subframe, from_=0, to=1, number_of_steps=10,
                                         variable=alpha_var)
            alpha_value_label = ctk.CTkLabel(master=label_data_subframe, textvariable=alpha_var)
            # ----- MANAGE WIDGETS
            label_data_subframe.grid(row=n_labels+self.model.n_labels_offset,
                                     column=0, sticky='nsew', pady=25, columnspan=3)

            n_labels_label.grid(row=2, column=0, columnspan=3, sticky="we")
            
            labels_label.grid(row=5, column=0, sticky='w')
            labels_cbbox.grid(row=5, column=2, sticky='we')
            fit_ckbox.grid(row=7, column=0, sticky='we')
            apply_ckbox.grid(row=7, column=2, sticky='we')
            labels_legend_label.grid(row=9, column=0, sticky='w')
            labels_legend_entry.grid(row=9, column=2, sticky='we')
            markerstyle_label.grid(row=11, column=0, sticky='w')
            markerstyle_cbbox.grid(row=11, column=2, sticky='we')
            markersize_label.grid(row=13, column=0, sticky='w')
            markersize_entry.grid(row=13, column=2, sticky='we')
            color_label.grid(row=15, column=0, sticky='w')
            color_button.grid(row=15, column=2, sticky='we')
            alpha_label.grid(row=17, column=0, sticky='w')
            alpha_slider.grid(row=17, column=2, sticky='we')
            alpha_value_label.grid(row=17, column=0, sticky='e')
            
            # --------------- MANAGE SEPARATORS
            general_params_separators_indices = [0, 1, 3, 4, 6, 8, 10, 12, 14, 16, 18]
            general_params_vertical_separator_ranges = [(4, 19), ]
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
            
            markersize_entry.configure(validate='focus',
                                       validatecommand=(self.view.register(partial(self.view.main_view.is_positive_int,
                                                                                   markersize_entry)), '%P'))
            
            
            # ------- STORE WIDGETS
            
            self.view.labels_subframes[str(n_labels)] = label_data_subframe
            self.view.vars[f"label data {n_labels}"] = label_var
            self.view.cbboxes[f"label data {n_labels}"] = labels_cbbox
            self.view.ckboxes[f"fit {n_labels}"] = fit_ckbox
            self.view.ckboxes[f"apply {n_labels}"] = apply_ckbox
            self.view.vars[f"fit {n_labels}"] = fit_var
            self.view.vars[f"apply {n_labels}"] = apply_var
            self.view.vars[f"label data legend {n_labels}"] = labels_legend_var
            self.view.cbboxes[f"marker style {n_labels}"] = markerstyle_cbbox
            self.view.vars[f"marker style {n_labels}"] = markerstyle_var
            self.view.vars[f"marker size {n_labels}"] = markersize_var
            self.view.buttons[f"color {n_labels}"] = color_button
            self.view.vars[f"color {n_labels}"] = color_var
            self.view.vars[f"alpha {n_labels}"] = alpha_var
            self.view.sliders[f"alpha {n_labels}"] = alpha_slider
            # ----- TRACE
            for key, widget in {f'color {n_labels}': color_var, f'fit {n_labels}': fit_var,
                                f'apply {n_labels}': apply_var, f'alpha {n_labels}': alpha_var,
                                f'marker size {n_labels}': markersize_var,
                                f'label data {n_labels}': label_var,
                                f'label data legend {n_labels}': labels_legend_var,
                                f'marker style {n_labels}': markerstyle_var,
                                }.items():
                self.model.plot_data[key] = widget.get()
                widget.trace("w", partial(self.trace_vars_to_model, key))
        
        else:
            messagebox.showerror("Missing Values", "No dataset loaded")
            return False
    
    def remove_label_data(self, ):
        """
        Removes the last added label data entry from the UI and associated model parameters.
        """
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
            del self.view.cbboxes[f"marker style {n_labels}"]
            del self.view.vars[f"marker size {n_labels}"]
            del self.view.vars[f"color {n_labels}"]
            del self.view.vars[f"fit {n_labels}"]
            del self.view.vars[f"apply {n_labels}"]
            del self.view.vars[f"alpha {n_labels}"]
            del self.view.ckboxes[f"fit {n_labels}"]
            del self.view.ckboxes[f"apply {n_labels}"]
            
            self.model.n_labels -= 1
    
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
        elif key in self.model.plot_data.keys():
            self.model.plot_data[key] = self.view.vars[key].get()
