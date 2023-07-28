import os
import pickle
import random
from functools import partial

import numpy as np
import pandas as pd
from fiiireflyyy.firelearn import confidence_ellipse
from matplotlib import pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from CONTROLLER.MainController import MainController
from MODEL.PcaModel import PcaModel
import customtkinter as ctk
from CONTROLLER import input_validation as ival
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import params as p


class PcaController:
    def __init__(self, view, ):
        self.model = PcaModel()
        self.view = view
        self.view.controller = self  # set controller
        self.progress = None

    def dummy_figure(self):  # todo create plot
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
                            , columns=principal_component_columns,)
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

    def draw_figure(self, ):
        fig, ax = self.view.figures["pca"]

        df = pd.read_csv(self.model.dataset_path, index_col=False)
        label_column = self.view.cbboxes["label column"].get()

        n_xticks = int(self.view.entries["n x ticks"].get())
        n_yticks = int(self.view.entries["n y ticks"].get())

        # ---- PLOTTING
        # todo : plotting
        labels_to_fit = []
        labels_to_apply = []
        for yi in range(self.model.n_labels + 1):
            if self.view.vars[f"fit {yi}"].get():
                labels_to_fit.append(self.view.cbboxes[f"label data {yi}"].get())
            if self.view.vars[f"apply {yi}"].get():
                labels_to_apply.append(self.view.cbboxes[f"label data {yi}"].get())

        df_fit = df[df[label_column].isin(labels_to_fit)]
        n_components = int(self.view.entries["n components"].get())
        pca, pcdf_fit, ratio = self.fit_pca(df_fit, n_components=n_components, label_column=label_column)
        df_apply = df[df[label_column].isin(labels_to_apply)]
        pcdf_applied = self.apply_pca(pca, df_apply, label_column=label_column)

        ax.clear()
        targets = list(set(list(df[label_column])))

        all_ymin = []  # for ticks
        all_ymax = []
        all_xmin = []
        all_xmax = []
        for yi in range(self.model.n_labels + 1):
            if n_components == 2:
                current_label = self.view.cbboxes[f"label data {yi}"].get()
                x_data = pcdf_applied.loc[pcdf_applied[label_column] == current_label][pcdf_applied.columns[0]]
                all_xmax.append(max(x_data))
                all_xmin.append(min(x_data))
                y_data = pcdf_applied.loc[pcdf_applied[label_column] == current_label][pcdf_applied.columns[1]]
                all_ymin.append(min(y_data))
                all_ymax.append(max(y_data))

                if self.view.entries[f"label data legend {str(yi)}"].get():
                    label = self.view.entries[f"label data legend {str(yi)}"].get()
                else:
                    label = self.view.cbboxes[f"label data {str(yi)}"].get()

                ax.scatter(x_data, y_data,
                           s=int(self.view.entries[f"marker size {str(yi)}"].get()),
                           marker=p.MARKERS[self.view.cbboxes[f"marker {str(yi)}"].get()],
                           color=self.view.vars[f"color {str(yi)}"].get(),
                           alpha=self.view.sliders[f"alpha {str(yi)}"].get(),
                           label=label
                           )
                if self.view.vars[f"ellipsis"].get():
                    ax.scatter(np.mean(x_data), np.mean(y_data),
                               marker="+",
                               color=self.view.vars[f"color {str(yi)}"].get(),
                               linewidth=2,
                               s=160)
                    confidence_ellipse(x_data, y_data, ax, n_std=1.0,
                                       color=self.view.vars[f"color {str(yi)}"].get(),
                                       fill=False, linewidth=2)

                # ---- LABELS
                ax.set_xlabel(self.view.entries["x label"].get(),
                              fontdict={"font": self.view.cbboxes["axes font"].get(),
                                        "fontsize": self.view.sliders["x label size"].get()})
                ax.set_ylabel(self.view.entries["y label"].get(),
                              fontdict={"font": self.view.cbboxes["axes font"].get(),
                                        "fontsize": self.view.sliders["y label size"].get()})
                ax.set_title(self.view.entries["title"].get(),)

                # ---- TICKS
                xmin = min(all_xmin)
                xmax = max(all_xmax)
                xstep = (xmax - xmin) / (n_xticks - 1)
                xtick = xmin
                xticks = []
                for i in range(n_xticks - 1):
                    xticks.append(xtick)
                    xtick += xstep
                xticks.append(xmax)
                rounded_xticks = list(np.around(np.array(xticks), int(self.view.entries["round x ticks"].get())))
                ax.set_xticks(rounded_xticks)
                ax.tick_params(axis='x',
                               labelsize=self.view.sliders["x ticks size"].get(),
                               labelrotation=float(self.view.sliders["x ticks rotation"].get()))

                ymin = min(all_ymin)
                ymax = max(all_ymax)
                ystep = (ymax - ymin) / (n_yticks - 1)
                ytick = ymin
                yticks = []
                for i in range(n_yticks - 1):
                    yticks.append(ytick)
                    ytick += ystep
                yticks.append(ymax)
                rounded_yticks = list(np.around(np.array(yticks), int(self.view.entries["round y ticks"].get())))
                ax.set_yticks(rounded_yticks)
                ax.tick_params(axis='y',
                               labelsize=self.view.sliders["y ticks size"].get(),
                               labelrotation=float(self.view.sliders["y ticks rotation"].get()))

                # ----- LEGEND
                # figure = self.create_figure()
                # self.view.canvas["feature importance"].figure = figure

                if self.view.switches["show legend"].get():
                    if self.view.cbboxes["legend anchor"].get() == 'custom':
                        legend = ax.legend(loc="upper left",
                                           bbox_to_anchor=(self.view.sliders["legend x pos"].get(),
                                                           self.view.sliders["legend y pos"].get()))
                    else:
                        legend = ax.legend(loc=self.view.cbboxes["legend anchor"].get(), )
                    for lh in legend.legendHandles:
                        lh.set_alpha(self.view.sliders["legend alpha"].get())


        # todo : 3D

        #     def update(handle, orig):
        #         handle.update_from(orig)
        #         handle.set_alpha(1)
        #
        #     plt.legend(prop={'size': 25}, handler_map={PathCollection: HandlerPathCollection(update_func=update),
        #                                                plt.Line2D: HandlerLine2D(update_func=update)})
        # elif options['n_components'] == 3:
        #     label_params = {'fontsize': 20, "labelpad": 8}
        #     ticks_params = {'fontsize': 20, }
        #     plt.figure(figsize=(10, 10))
        #     ax = plt.axes(projection='3d')
        #
        #     xlabel = f'Principal Component-1 ({options["ratios"][0]}%)'
        #     ylabel = f'Principal Component-2 ({options["ratios"][1]}%)'
        #     zlabel = f'Principal Component-3 ({options["ratios"][2]}%)'
        #     if len(options['pc_ratios']):
        #         xlabel += f" ({round(options['pc_ratios'][0] * 100, 2)}%)"
        #         ylabel += f" ({round(options['pc_ratios'][1] * 100, 2)}%)"
        #         zlabel += f" ({round(options['pc_ratios'][2] * 100, 2)}%)"
        #
        #     ax.set_xlabel(xlabel, **label_params)
        #     ax.set_ylabel(ylabel, **label_params)
        #     ax.set_zlabel(zlabel, **label_params)
        #     for target, color in zip(targets, colors):
        #         indicesToKeep = dataframe['label'] == target
        #         x = dataframe.loc[indicesToKeep, 'principal component 1']
        #         y = dataframe.loc[indicesToKeep, 'principal component 2']
        #         z = dataframe.loc[indicesToKeep, 'principal component 3']
        #         ax.scatter3D(x, y, z, c=color, s=10)
        #     plt.legend(targets, prop={'size': 18})
        #
        # if options['savedir']:
        #     if options["title"] == "":
        #         if options['commentary']:
        #             options["title"] += options["commentary"]
        #
        #     plt.savefig(os.path.join(options['savedir'], options["title"] + ".png"), dpi=1200)
        #
        # if options['show']:
        #     plt.show()
        # plt.close()
        #
        #
        #
        #
        #

        plt.tight_layout()  # todo : tight layout() not effective anymore because of legend ?

        self.view.figures["pca"] = (fig, ax)
        self.view.canvas["pca"].draw()

    def input_validation_plot(self):
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
        filepath = filedialog.asksaveasfilename(title="Open file", filetypes=(("Image", "*.png"),))
        fig.savefig(filepath, dpi=int(self.view.entries["dpi"].get()))

        # df = pd.DataFrame(columns=["X", "Y"])
        # df["X"] = x_data
        # df["Y"] = y_data
        #
        # df.to_csv(filepath, index=False)

    def check_params_validity(self):
        if not self.input_validation_plot():
            return False
        return True

    def save_config(self, ):
        if self.check_params_validity():
            self.update_params(self.view.entries)
            self.update_params(self.view.cbboxes)
            self.update_params(self.view.sliders)
            self.update_params(self.view.vars)
            self.update_params(self.view.switches)

            f = filedialog.asksaveasfilename(defaultextension=".pltcfg",
                                             filetypes=[("Analysis - pca", "*.pcacfg"), ])
            if f:
                self.model.save_model(path=f, )

    def update_params(self, widgets: dict, ):
        local_dict = {}
        for key, value in widgets.items():
            if type(value) == ctk.CTkTextbox:
                local_dict[key] = value.get('1.0', tk.END)
            else:
                local_dict[key] = value.get()
        if type(list(widgets.values())[0]) == ctk.CTkSwitch:
            self.model.switches.update(local_dict)
        if type(list(widgets.values())[0]) == ctk.CTkEntry:
            self.model.entries.update(local_dict)
        if type(list(widgets.values())[0]) == tk.ttk.Combobox:
            self.model.cbboxes.update(local_dict)
        if type(list(widgets.values())[0]) == ctk.CTkTextbox:
            local_dict = {}
            for key, value in widgets.items():
                local_dict[key] = value.get('1.0', tk.END)
            self.model.textboxes.update(local_dict)
        if type(list(widgets.values())[0]) == ctk.CTkSlider:
            self.model.sliders.update(local_dict)
        if type(list(widgets.values())[0]) == ctk.CTkCheckBox:
            self.model.checkboxes.update(local_dict)
        if type(list(widgets.values())[0]) == tk.IntVar or \
                type(list(widgets.values())[0]) == tk.StringVar or \
                type(list(widgets.values())[0]) == tk.DoubleVar:
            self.model.vars.update(local_dict)

    def load_config(self, ):
        f = filedialog.askopenfilename(title="Open file", filetypes=(("Analysis - pca", "*.pcacfg"),))
        if f:
            if self.model.load_model(path=f):
                self.update_view_from_model()  # todo : does not work with multiple y :

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

        for key, widget in self.view.sliders.items():
            if widget.cget('state') == "normal":
                self.view.vars[key].set(self.model.vars[key])
                self.view.sliders[key].set(self.model.sliders[key])

        for key, widget in self.view.textboxes.items():
            MainController.update_textbox(widget, self.model.textboxes[key].split("\n"))

    def load_plot_dataset(self, ):
        filename = filedialog.askopenfilename(title="Open file",
                                              filetypes=(("Tables", "*.txt *.csv"),))
        if filename:
            df = pd.read_csv(filename)
            self.model.dataset_path = filename
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
        if self.model.dataset_path:
            df = pd.read_csv(self.model.dataset_path, index_col=False)
            label_col = self.view.cbboxes["label column"].get()
            all_labels = sorted(set(list(df[label_col])))

            self.model.n_labels += 1
            n_labels = self.model.n_labels
            label_data_subframe = ctk.CTkFrame(master=scrollable_frame, height=250)
            label_data_subframe.grid(row=n_labels, column=0, sticky=ctk.NSEW, pady=25)
            self.view.labels_subframes[str(n_labels)] = label_data_subframe

            labels_label = ctk.CTkLabel(master=label_data_subframe, text="Label:")
            labels_label.place(relx=0, rely=0)
            labels_cbbox = tk.ttk.Combobox(master=label_data_subframe, values=all_labels, state='readonly')
            labels_cbbox.set(all_labels[0])
            labels_cbbox.place(relx=0, rely=0.12)
            self.view.cbboxes[f"label data {n_labels}"] = labels_cbbox

            add_label_data_button = ctk.CTkButton(master=label_data_subframe, text="+", width=25, height=25,
                                                  state='normal')
            add_label_data_button.place(anchor=tk.NE, relx=0.25, rely=0)
            self.view.buttons[f"add label data {n_labels}"] = add_label_data_button
            subtract_label_data_button = ctk.CTkButton(master=label_data_subframe, text="-", width=25, height=25,
                                                       state='normal')
            subtract_label_data_button.place(anchor=tk.NE, relx=0.38, rely=0)
            self.view.buttons[f"subtract label data {n_labels}"] = subtract_label_data_button

            fit_var = tk.IntVar()
            fit_var.set(1)
            apply_var = tk.IntVar()
            apply_var.set(1)
            fit_ckbox = ctk.CTkCheckBox(master=label_data_subframe, text="Fit", variable=fit_var)
            fit_ckbox.place(relx=0.65, rely=0)
            apply_ckbox = ctk.CTkCheckBox(master=label_data_subframe, text="Apply", variable=apply_var)
            apply_ckbox.place(relx=0.75, rely=0)
            self.view.checkboxes[f"fit {n_labels}"] = fit_ckbox
            self.view.checkboxes[f"apply {n_labels}"] = apply_ckbox
            self.view.vars[f"fit {n_labels}"] = fit_var
            self.view.vars[f"apply {n_labels}"] = apply_var

            labels_legend_label = ctk.CTkLabel(master=label_data_subframe, text="Legend label:")
            labels_legend_label.place(relx=0, rely=0.25)
            labels_legend_entry = ctk.CTkEntry(master=label_data_subframe)
            labels_legend_entry.place(relx=0, rely=0.37, relwidth=0.4)
            self.view.entries[f"label data legend {n_labels}"] = labels_legend_entry

            markerstyle_label = ctk.CTkLabel(master=label_data_subframe, text="Markers:")
            markerstyle_label.place(relx=0, rely=0.5)
            markerstyle_cbbox = tk.ttk.Combobox(master=label_data_subframe, values=list(sorted(p.MARKERS.keys())),
                                                state='readonly')
            markerstyle_cbbox.set("point")
            markerstyle_cbbox.place(relx=0, rely=0.62, relwidth=0.25)
            self.view.cbboxes[f"marker {n_labels}"] = markerstyle_cbbox

            markersize_label = ctk.CTkLabel(master=label_data_subframe, text="Marker size:")
            markersize_label.place(relx=0.3, rely=0.5)
            markersize_strvar = tk.StringVar()
            markersize_strvar.set("1")
            markersize_entry = ctk.CTkEntry(master=label_data_subframe, textvariable=markersize_strvar)
            markersize_entry.place(relx=0.3, rely=0.62, relwidth=0.2)
            self.view.entries[f"marker size {n_labels}"] = markersize_entry
            self.view.vars[f"marker size {n_labels}"] = markersize_strvar

            color_label = ctk.CTkLabel(master=label_data_subframe, text="Color:")
            color_label.place(relx=0.6, rely=0.5)
            color_var = tk.StringVar()
            color_var.set("green")
            color_button = ctk.CTkButton(master=label_data_subframe, textvariable=color_var,
                                         fg_color=color_var.get(), text_color='black')
            color_button.place(relx=0.6, rely=0.62)
            self.view.buttons[f"color {n_labels}"] = color_button
            self.view.vars[f"color {n_labels}"] = color_var

            alpha_label = ctk.CTkLabel(master=label_data_subframe, text="Alpha:")
            alpha_label.place(relx=0.5, rely=0.25)
            alpha_slider = ctk.CTkSlider(master=label_data_subframe, from_=0, to=1, number_of_steps=10)
            alpha_slider.set(p.DEFAULT_LINEALPHA)
            alpha_slider.place(relx=0.5, rely=0.37, relwidth=0.4)
            alpha_strvar = tk.StringVar()
            alpha_strvar.set(str(alpha_slider.get()))
            alpha_value_label = ctk.CTkLabel(master=label_data_subframe, textvariable=alpha_strvar)
            alpha_value_label.place(relx=0.7, rely=0.25)
            self.view.vars[f"alpha {n_labels}"] = alpha_strvar
            self.view.sliders[f"alpha {n_labels}"] = alpha_slider

            alpha_slider.configure(command=partial(self.view.update_slider_value, var=alpha_strvar))
            color_button.configure(command=partial(self.view.select_color, view=self.view,
                                                   selection_button_name=f'color {n_labels}'))
            add_label_data_button.configure(command=partial(self.add_label_data, scrollable_frame))
            subtract_label_data_button.configure(command=partial(self.remove_label_data, f'{n_labels}'))
        else:
            messagebox.showerror("Missing Values", "No dataset loaded")
            return False

    def remove_label_data(self, frame_key):
        n_labels = self.model.n_labels
        destroyed_number = int(frame_key.split(" ")[-1])

        for y in range(0, n_labels + 1):
            if 0 <= y < destroyed_number:
                pass
            elif y == destroyed_number:
                # destroying all widgets related
                for child in self.view.labels_subframes[str(y)].winfo_children():
                    child.destroy()

                # remove the frame from self.view.labels_subframes
                self.view.labels_subframes[str(y)].destroy()
                del self.view.labels_subframes[str(y)]

                # destroying all items related in dicts
                del self.view.entries[f"label data legend {destroyed_number}"]
                del self.view.entries[f"marker size {destroyed_number}"]
                del self.view.buttons[f"add label data {destroyed_number}"]
                del self.view.buttons[f"subtract label data {destroyed_number}"]
                del self.view.buttons[f"color {destroyed_number}"]
                del self.view.cbboxes[f"label data {destroyed_number}"]
                del self.view.cbboxes[f"marker {destroyed_number}"]
                del self.view.vars[f"marker size {destroyed_number}"]
                del self.view.vars[f"color {destroyed_number}"]
                del self.view.vars[f"fit {destroyed_number}"]
                del self.view.vars[f"apply {destroyed_number}"]
                del self.view.vars[f"alpha {destroyed_number}"]
                del self.view.sliders[f"alpha {destroyed_number}"]
                del self.view.checkboxes[f"fit {destroyed_number}"]
                del self.view.checkboxes[f"apply {destroyed_number}"]

            elif y > destroyed_number:
                self.view.rename_dict_key(self.view.entries, f"label data legend {y}", f"label data legend {y - 1}")
                self.view.rename_dict_key(self.view.entries, f"marker size {y}", f"marker size {y - 1}")
                self.view.rename_dict_key(self.view.buttons, f"add label data {y}", f"add label data {y - 1}")
                self.view.rename_dict_key(self.view.buttons, f"color {y}", f"color {y - 1}")
                self.view.rename_dict_key(self.view.buttons, f"subtract label data {y}", f"subtract label data {y - 1}")
                self.view.rename_dict_key(self.view.cbboxes, f"label data {y}", f"label data {y - 1}")
                self.view.rename_dict_key(self.view.cbboxes, f"marker {y}", f"marker {y - 1}")
                self.view.rename_dict_key(self.view.vars, f"marker size {y}", f"marker size {y - 1}")
                self.view.rename_dict_key(self.view.vars, f"color {y}", f"color {y - 1}")
                self.view.rename_dict_key(self.view.vars, f"alpha {y}", f"alpha {y - 1}")
                self.view.rename_dict_key(self.view.vars, f"fit {y}", f"fit {y - 1}")
                self.view.rename_dict_key(self.view.vars, f"apply {y}", f"apply {y - 1}")
                self.view.rename_dict_key(self.view.sliders, f"alpha {y}", f"alpha {y - 1}")
                self.view.rename_dict_key(self.view.checkboxes, f"fit {y}", f"fit {y - 1}")
                self.view.rename_dict_key(self.view.checkboxes, f"apply {y}", f"apply {y - 1}")

                self.view.rename_dict_key(self.view.labels_subframes, str(y), str(y - 1))
                self.view.labels_subframes[str(y - 1)].grid(row=y - 1, column=0,
                                                            sticky=ctk.NSEW)  # replace the frame in grid
                self.view.buttons[f"subtract label data {y - 1}"].configure(
                    command=partial(self.remove_label_data, f'{y - 1}'))

        self.model.n_labels -= 1
