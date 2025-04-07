import os
import pickle
import sys
from functools import partial

import matplotlib.axes
import numpy as np
import seaborn as sns

import pandas as pd
from matplotlib import pyplot as plt
from scripts.CONTROLLER.ProgressBar import ProgressBar

from scripts.MODEL.ConfusionModel import ConfusionModel
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from scripts import params as p

import fiiireflyyy.learn as fl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from scripts.WIDGETS.ErrEntry import ErrEntry


class ConfusionController:
    def __init__(self, view, ):
        self.model = ConfusionModel()
        self.view = view
        self.view.controller = self  # set controller
        self.progress = None

        self.TRAIN_CORRESPONDENCE = {}
        self.TEST_CORRESPONDENCE = {}

        self.cancelled = False

    @staticmethod
    def rename_dict_key(d, old_key, new_key):
        """
        Renames a key in a dictionary. Changes are in-place.

        Parameters
        ----------
        d : dict
            The dictionary in which the key needs to be renamed.

        old_key : str
            The key that needs to be renamed.

        new_key : str
            The new name for the key.

        Returns
        -------
        """
        if old_key in d:
            d[new_key] = d.pop(old_key)

    def load_clf(self, loaded=False):
        """
        Loads a classifier model (.rfc file) and updates the UI accordingly.

        If `loaded` is True, it assumes the classifier is already set in the model.
        Otherwise, it opens a file dialog to allow the user to select a classifier file.

        Args:
            loaded (bool): Whether the classifier is already loaded (default: False).
        """
        if loaded:
            self.view.vars["load clf"].set(self.model.clf_path)

            training_classes = list(set(list(self.model.clf.classes_)))

            for child in self.view.scrollable_frames["training"].winfo_children():
                child.destroy()
            for t in range(len(training_classes)):
                target_index_var = ctk.StringVar(value=str(t))
                target_cbbox = ttk.Combobox(master=self.view.scrollable_frames["training"],
                                            textvariable=target_index_var,
                                            values=[str(x) for x in range(len(training_classes))],
                                            state='readonly')
                target_radio = ctk.CTkRadioButton(master=self.view.scrollable_frames["training"],
                                                  text=training_classes[t],
                                                  state='disabled', text_color_disabled='white'
                                                  )
                target_radio.select()
                target_radio.grid(row=t, column=0, padx=10, pady=10, sticky='w')
                target_cbbox.grid(row=t, column=1, padx=10, pady=10, sticky='w')
                self.view.vars[f"train label {t} index"] = target_index_var
        else:
            filename = filedialog.askopenfilename(title="Open file",
                                                  filetypes=(("AI model", "*.rfc"),))
            if filename:
                clf = pickle.load(open(filename, "rb"))
                self.model.clf = clf
                self.model.clf_path = filename

                self.view.vars["load clf"].set(filename)

                training_classes = list(set(list(self.model.clf.classes_)))

                for child in self.view.scrollable_frames["training"].winfo_children():
                    child.destroy()
                for t in range(len(training_classes)):
                    target_index_var = ctk.StringVar(value=str(t))
                    target_cbbox = ttk.Combobox(master=self.view.scrollable_frames["training"],
                                                textvariable=target_index_var,
                                                values=[str(x) for x in range(len(training_classes))],
                                                state='readonly')
                    target_radio = ctk.CTkRadioButton(master=self.view.scrollable_frames["training"],
                                                      text=training_classes[t],
                                                      state='disabled', text_color_disabled='white'
                                                      )
                    target_radio.select()
                    target_radio.grid(row=t, column=0, padx=10, pady=10, sticky='w')
                    target_cbbox.grid(row=t, column=1, padx=10, pady=10, sticky='w')

                    self.view.vars[f"train label {t} index"] = target_index_var

    def predict_X_values(self, X):
        """
        Predict the values for a given dataframe `X` using the trained classifier.

        Parameters
        ----------
        X : pd.DataFrame
            Dataframe containing all the entries that need to be predicted.

        Returns
        -------
        predictions : list of tuple of size 2
            List of tuples containing the predicted class label (`y_pred`) as the first element
            and the associated probabilities for all classes (`proba_class`) as the second element.
        """
        predictions = []
        for i in range(len(X.values)):
            row = X.iloc[i]
            y_pred = self.model.clf.predict([row])[0]
            proba_class = self.model.clf.predict_proba([row])[0]
            predictions.append((y_pred, proba_class))
            self.progress.increment_progress(1)
            if self.cancelled:
                return None

        return predictions

    def compute_confusion(self, ):
        """
        Computes the confusion matrix for a trained classifier based on the selected testing classes and iterations.

        This function validates inputs, prepares the data, and uses the classifier to generate confusion matrices
        (numeric, percent, and CUP values). It updates the model's confusion data and triggers the plotting process.

        The process involves:
            - Validating input parameters.
            - Selecting the training and testing classes based on the view.
            - Filtering the dataset according to the selected classes.
            - Computing confusion matrices using multiple iterations.
            - Storing the results (numeric, percentage, and CUP) in the model.
            - Updating the visualization with the computed results.

        Returns:
            None
        """
        for _ in range(1):
            if self._input_validation():
                if self.cancelled:
                    break
                plt.close()
                training_classes = list(set(list(self.model.clf.classes_)))
                all_testing_classes = {key: value for (key, value) in self.view.vars.items() if "test label " in key}

                checked_classes = {key: value for (key, value) in all_testing_classes.items() if value.get() == 1}
                checked_classes_names = {self.view.ckboxes[key].cget('text'): value for (key, value) in
                                         checked_classes.items()}.keys()
                testing_classes = list(checked_classes_names)

                self.model.training_classes = training_classes
                self.model.testing_classes = testing_classes

                df = self.model.dataset
                df = df[df[self.view.vars["label column"].get()].isin(testing_classes)]

                self.progress = ProgressBar("Confusion computation", app=self.view.app, controller=self)
                self.progress.total_tasks = self._confusion_number_of_tasks(df)
                self.progress.start()
                if self.cancelled:
                    break
                overall_matrix_numeric, overall_matrix_percent, overall_matrix_cup \
                    = self._test_clf_by_confusion(df, training_targets=training_classes,
                                                  testing_targets=testing_classes,
                                                  iterations=self.view.vars["iterations"].get(),
                                                  )  # todo : update fiiireflyyy
                if self.cancelled:
                    break

                self.cancelled = False
                self.model.confusion_data["overall matrix numeric"] = overall_matrix_numeric
                self.model.confusion_data["overall matrix percent"] = overall_matrix_percent

                self.model.confusion_data["overall matrix cup"] = overall_matrix_cup
                self.model.confusion_data["train correspondence"] = self.TRAIN_CORRESPONDENCE
                self.model.confusion_data["test correspondence"] = self.TEST_CORRESPONDENCE
                if self.cancelled:
                    break
                self.update_figure()

        if self.cancelled:
            messagebox.showinfo("Cancel Computation", "Process gracefully interrupted.")
        else:
            print("Process finished.")

        self.cancelled = False

    def update_figure(self):
        """
        Updates and displays the confusion matrix figure in the GUI.

        This function generates and formats the confusion matrix based on the previously computed values,
        and updates the figure within the GUI. It also handles the customization of labels, annotations, and axes.

        It involves:
            - Choosing the correct confusion matrix (numeric or percent) based on user settings.
            - Applying custom annotations such as numeric values, CUP, or both.
            - Renaming the x-axis and y-axis labels based on user preferences.
            - Updating the plot with the new matrix and setting up the visualization in the Tkinter canvas.
            - Updating the toolbar for the plot.

        Returns:
            None
        """
        plt.close()
        overall_matrix = self.model.confusion_data["overall matrix percent"] \
            if self.model.plot_specific_settings["annot mode"] == 'percent' \
            else self.model.confusion_data["overall matrix numeric"]
        overall_matrix_cup = self.model.confusion_data["overall matrix cup"]
        TRAIN_CORRESPONDENCE = self.model.confusion_data["train correspondence"]
        TEST_CORRESPONDENCE = self.model.confusion_data["test correspondence"]

        acc_array = overall_matrix.to_numpy().astype(float) if self.model.plot_specific_settings[
                                                                   "annot mode"] == 'percent' else overall_matrix.to_numpy().astype(
            int)
        cup_array = overall_matrix_cup.to_numpy()
        mixed_labels_matrix = np.empty((len(TRAIN_CORRESPONDENCE.keys()), len(TEST_CORRESPONDENCE.keys()))).tolist()

        compute_train_index_to_plot_index = {}
        compute_test_index_to_plot_index = {}

        def has_unique_second_elements(dct):
            second_elements = {v for k, v in dct.items()}  # Extract all second elements into a set
            return len(second_elements) == len(dct.values())  # If set size matches list size, they are unique

        for t in range(len(self.model.training_classes)):
            plot_index = int(self.view.vars[f"train label {t} index"].get())
            compute_index = t
            compute_train_index_to_plot_index[compute_index] = plot_index

        for t in range(len(self.model.testing_classes)):
            plot_index = int(self.view.vars[f"test label {t} index"].get())
            compute_index = t
            compute_test_index_to_plot_index[compute_index] = plot_index

        if not has_unique_second_elements(compute_train_index_to_plot_index) or not has_unique_second_elements(
                self.TRAIN_CORRESPONDENCE):
            messagebox.showerror('Unique Values', 'You can not have multiple training targets having the same index.')
            return
        if not has_unique_second_elements(compute_test_index_to_plot_index) or not has_unique_second_elements(
                self.TEST_CORRESPONDENCE):
            messagebox.showerror('Unique Values', 'You can not have multiple testing targets having the same index.')
            return

        translated_train_correspondence = {v: k for k, v in self.TRAIN_CORRESPONDENCE.items()}
        translated_test_correspondence = {v: k for k, v in self.TEST_CORRESPONDENCE.items()}

        translated_acc_array = acc_array.copy()
        for r in range(len(acc_array)):
            for c in range(len(acc_array[0])):
                translated_r = compute_train_index_to_plot_index[r]
                translated_c = compute_test_index_to_plot_index[c]
                translated_acc_array[translated_r][translated_c] = acc_array[r][c]

        for r in range(len(acc_array)):
            for c in range(len(acc_array[0])):
                if self.model.plot_specific_settings["annot only cup"]:
                    case = f"CUP={cup_array[r][c]}"
                    mixed_labels_matrix[r][c] = case
                else:
                    case = f"{acc_array[r][c]}%\nCUP={cup_array[r][c]}" \
                        if self.model.plot_specific_settings["annot mode"] == 'percent' \
                        else f"{acc_array[r][c]}\nCUP={cup_array[r][c]}"
                    mixed_labels_matrix[r][c] = case

        translated_mixed_labels_matrix = [row.copy() for row in mixed_labels_matrix]
        for r in range(len(acc_array)):
            for c in range(len(acc_array[0])):
                translated_r = compute_train_index_to_plot_index[r]
                translated_c = compute_test_index_to_plot_index[c]
                translated_mixed_labels_matrix[translated_r][translated_c] = mixed_labels_matrix[r][c]

        fig, ax = plt.subplots(figsize=(4, 4))
        new_canvas = FigureCanvasTkAgg(fig, master=self.view.frames["plot frame"])
        new_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
        self.view.canvas["confusion toolbar"].destroy()
        toolbar = NavigationToolbar2Tk(new_canvas,
                                       self.view.frames["plot frame"], pack_toolbar=False)
        toolbar.update()
        toolbar.grid(row=1, column=0, sticky='we')
        self.view.canvas["confusion"].get_tk_widget().destroy()
        self.view.canvas["confusion"] = new_canvas
        self.view.figures["confusion"] = (fig, ax)

        annot_kws = {"font": self.model.plot_specific_settings["annot font"],
                     "size": self.model.plot_specific_settings["annot size"]}

        sns.heatmap(ax=ax, data=translated_acc_array, annot=translated_mixed_labels_matrix, annot_kws=annot_kws, fmt='',
                    cmap="Blues",
                    square=True, cbar_kws={'shrink': 0.5, 'location': 'right'}, )
        ax.xaxis.tick_top()
        ax.xaxis.set_label_position('top')
        ax.set_ylabel(self.model.plot_axes["y label"], fontdict={"font": self.model.plot_axes["axes font"],
                                                                 "fontsize": self.model.plot_axes["y label size"]})
        ax.set_xlabel(self.model.plot_axes["x label"], {"font": self.model.plot_axes["axes font"],
                                                        "fontsize": self.model.plot_axes["x label size"]})

        renames_queries = {key: value.get() for (key, value) in self.view.vars.items() if "x rename " in key}
        original_labels = {key: value.get() for (key, value) in self.view.vars.items() if "x label " in key}

        label_to_rename = []
        for rename_key, rename in renames_queries.items():
            if rename != '':
                index = rename_key.split(' ')[-1]
                label_to_rename.append(f"x label {index}")

        for label in label_to_rename:
            old_key = original_labels[label]
            new_key = renames_queries[label.replace('label', 'rename')]

            self.rename_dict_key(TRAIN_CORRESPONDENCE, old_key, new_key)
            self.rename_dict_key(TEST_CORRESPONDENCE, old_key, new_key)

            self.model.training_classes = [x.replace(old_key, new_key) for x in self.model.training_classes]
            self.model.testing_classes = [x.replace(old_key, new_key) for x in self.model.testing_classes]

            self.view.vars[label].set(new_key)

        ax.set_xticks(
            [compute_test_index_to_plot_index[TEST_CORRESPONDENCE[x]] + 0.5 for x in self.model.testing_classes],
            self.model.testing_classes,
            fontsize=self.model.plot_axes["x ticks size"], )
        ax.tick_params(axis='x', labelrotation=self.model.plot_axes["x ticks rotation"],
                       labelsize=self.model.plot_axes["x ticks size"],
                       labelfontfamily=self.model.plot_axes["axes font"])
        ax.tick_params(axis='y', labelrotation=self.model.plot_axes["y ticks rotation"],
                       labelsize=self.model.plot_axes["y ticks size"],
                       labelfontfamily=self.model.plot_axes["axes font"])

        ax.set_title(self.model.plot_general_settings["title"],
                     fontdict={"font": self.model.plot_general_settings["title font"],
                               "fontsize": self.model.plot_general_settings["title size"]}, )
        ax.set_yticks(
            [compute_train_index_to_plot_index[TRAIN_CORRESPONDENCE[x]] + 0.5 for x in self.model.training_classes],
            self.model.training_classes, fontsize=self.model.plot_axes["y ticks size"])
        self.view.figures["confusion"] = (fig, ax)
        self.view.canvas["confusion"].draw()

    def save_config(self, ):
        """
        Save the current model state as a *.*cfg file.
        
        Returns
        -------

        """
        if self._input_validation():
            f = filedialog.asksaveasfilename(defaultextension=".confcfg",
                                             filetypes=[("Analysis - Confusion", "*.confcfg"), ])
            if f:
                self.model.save_model(path=f, )

    def load_config(self, ):
        """
        Load a previously saved configuration file and update the view based on the model.
        
        Returns
        -------

        """
        f = filedialog.askopenfilename(title="Open file", filetypes=(("Analysis - Confusion", "*.confcfg"),))
        if f:
            if self.model.load_model(path=f):
                if self.model.dataset_path:
                    self.load_clf(loaded=True)
                    self.load_dataset(loaded=True)

                self.update_view_from_model()

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
        for key, value in self.model.plot_data.items():
            self.view.vars[key].set(value)
        for key, value in self.model.plot_legend.items():
            self.view.vars[key].set(value)
        for key, value in self.model.plot_axes.items():
            self.view.vars[key].set(value)
        for key, value in self.model.plot_general_settings.items():
            self.view.vars[key].set(value)

    def load_dataset(self, loaded=False):
        """
        Load a dataset and update the corresponding view elements.

        If `loaded` is True, the function updates the view with information about an already
        loaded dataset and its associated label column. It removes any training-related
        elements from the view and model. If `loaded` is False, it opens a file dialog to
        allow the user to select a dataset file (CSV or TXT), loads the dataset, and updates
        the model and view accordingly.

        Parameters
        ----------
        loaded : bool, optional, default: False
            If True, the function assumes the dataset is already loaded and updates the view
            accordingly. If False, the function prompts the user to select a file to load.

        Returns
        -------
        """
        if loaded:
            # fig, ax = self.view.figures["confusion"]

            training_labels = {key: value for (key, value) in self.model.plot_data.items() if "training" in key}
            for key, widget in training_labels.items():
                widget.destroy()
                del self.view.vars[key]
                del self.view.ckboxes[key]
                del self.model.plot_data[key]

            df = self.model.dataset
            filename = self.model.dataset_path

            columns = list(df.columns)
            self.view.cbboxes["label column"].configure(values=columns)
            label_col = columns[0]
            for col in columns:
                if 'label' in col or 'target' in col:  # try to auto-detect the label column
                    label_col = col
            self.view.vars["load dataset"].set(filename)
            self.view.vars["label column"].set(label_col)

        else:
            filename = filedialog.askopenfilename(title="Open file",
                                                  filetypes=(("Tables", "*.txt *.csv"),))
            if filename:
                # fig, ax = self.view.figures["confusion"]
                # ax.clear()
                training_labels = {key: value for (key, value) in self.model.plot_data.items() if "training" in key}
                for key, widget in training_labels.items():
                    widget.destroy()
                    del self.view.vars[key]
                    del self.view.ckboxes[key]
                    del self.model.plot_data[key]

                df = pd.read_csv(filename)
                self.model.dataset = df
                self.model.dataset_path = filename

                columns = list(df.columns)
                self.view.cbboxes["label column"].configure(values=columns)
                label_col = columns[0]
                for col in columns:
                    if 'label' in col or 'target' in col:  # try to auto-detect the label column
                        label_col = col
                self.view.vars["load dataset"].set(filename)
                self.view.vars["label column"].set(label_col)

    def deselect_all_test_targets(self):
        """
        Deselect all test targets checkboxes in the view.
        
        Returns
        -------

        """
        ckboxes = {key: value for (key, value) in self.view.vars.items() if "test label" in key}
        for key, widget in ckboxes.items():
            widget.set(0)

    def select_all_test_targets(self):
        """
        Select all test targets checkboxes in the view.

        Returns
        -------

        """
        ckboxes = {key: value for (key, value) in self.view.vars.items() if "test label" in key}
        for key, widget in ckboxes.items():
            widget.set(1)

    def trace_testing_labels(self, *args):
        """
        Trace and update the testing labels in the view based on the selected label column.

        This function retrieves the unique values from the selected label column in the dataset,
        and dynamically creates checkboxes for each unique value to represent testing labels.
        If there are more than 20 unique values in the column, the user is prompted to confirm
        whether they want to proceed with creating checkboxes for all values.

        The function clears any existing test label checkboxes, creates new ones for the possible targets,
        and updates the associated variables and model data accordingly.

        Parameters
        ----------
        *args : tuple
            Variable arguments passed from the event triggering the function, typically used
            in event handling, but not explicitly required in the function body.

        Returns
        -------
        """

        if self.view.vars["label column"].get() != 'None':
            possible_targets = list(set(list(self.model.dataset[self.view.vars["label column"].get()])))
            proceed = True
            if len(possible_targets) > 20:  # hard cap the number of possible targets to prevent a data column to be put
                proceed = messagebox.askyesno("Too many labels", f"There are {len(possible_targets)} different"
                                                                 f" values in the column you selected."
                                                                 f"\nProceed ?")
            if proceed:
                for child in self.view.scrollable_frames["testing"].winfo_children():
                    child.destroy()
                targets = {key: value for (key, value) in self.view.vars.items() if "test label" in key}
                for key in targets.keys():
                    del self.view.vars[key]

                for t in range(len(possible_targets)):
                    target_var = tk.IntVar(value=1)
                    target_index_var = ctk.StringVar(value=str(t))

                    target_checkbox = ctk.CTkCheckBox(master=self.view.scrollable_frames["testing"],
                                                      variable=target_var,
                                                      text=possible_targets[t])

                    target_cbbox = ttk.Combobox(master=self.view.scrollable_frames["testing"],
                                                textvariable=target_index_var,
                                                values=[str(x) for x in range(len(possible_targets))],
                                                state='readonly')
                    target_checkbox.grid(row=t, column=0, padx=10, pady=10, sticky='w')
                    target_cbbox.grid(row=t, column=1, padx=10, pady=10, sticky='w')
                    self.view.vars[f"test label {t}"] = target_var
                    self.view.vars[f"test label {t} index"] = target_index_var
                    self.view.ckboxes[f"test label {t}"] = target_checkbox
                    self.model.plot_data[f"test label {t}"] = target_var.get()
                    target_var.trace("w", partial(self.trace_vars_to_model, f"test label {t}"))

    def trace_vars_to_model(self, key, *args):
        """
        Trace the tk or ctk variable into the corresponding model attribute.
        
        Parameters
        ----------
        key : str
            key id of the widget
        args :
            required args for ctk trace. To leave empty.

        Returns
        -------

        """
        if key in self.model.plot_general_settings.keys():
            self.model.plot_general_settings[key] = self.view.vars[key].get()
        elif key in self.model.plot_axes.keys():
            self.model.plot_axes[key] = self.view.vars[key].get()
        elif key in self.model.plot_legend.keys():
            self.model.plot_legend[key] = self.view.vars[key].get()
        elif key in self.model.plot_specific_settings.keys():
            self.model.plot_specific_settings[key] = self.view.vars[key].get()

    def update_confusion_ticks(self, ):
        """
        Updates the ticks of the confusion matrix plot based on values in the model.
        
        Returns
        -------

        """

        if self.model.dataset_path and self.model.clf:
            ticks_train_scrollable = self.view.scrollable_frames["ticks train"]
            ticks_test_scrollable = self.view.scrollable_frames["ticks test"]

            vars_and_model_to_destroy = []
            for key, value in self.model.plot_data.items():
                for key_to_destroy in ["y rename", "y label", "x rename", "x label"]:
                    if key_to_destroy in key:
                        vars_and_model_to_destroy.append(key)
            for key in vars_and_model_to_destroy:
                del self.view.vars[key]
                del self.model.plot_data[key]

            for child in ticks_test_scrollable.winfo_children():
                child.destroy()
            for child in ticks_train_scrollable.winfo_children():
                child.destroy()

            training_classes = tuple(list(set(list(self.model.clf.classes_))))
            all_testing_classes = {key: value for (key, value) in self.view.vars.items() if "test label" in key}

            checked_classes = {key: value for (key, value) in all_testing_classes.items() if value.get() == 1}
            checked_classes_names = {self.view.ckboxes[key].cget('text'): value for (key, value) in
                                     checked_classes.items()}.keys()
            testing_classes = tuple(checked_classes_names)

            for target in training_classes:
                target_train_frame = ctk.CTkFrame(master=ticks_train_scrollable, height=130, width=225)
                original_train_label = ctk.CTkLabel(master=target_train_frame, text="Original target:")
                target_train_label_var = tk.StringVar(value=target)
                target_train_label = ctk.CTkLabel(master=target_train_frame, textvariable=target_train_label_var)
                rename_train_label = ctk.CTkLabel(master=target_train_frame, text="Rename target")
                rename_train_var = tk.StringVar()
                rename_train_entry = ErrEntry(master=target_train_frame, textvariable=rename_train_var)

                original_train_label.place(relx=0.05, rely=0)
                target_train_label.place(relx=0.05, rely=0.2)
                rename_train_label.place(relx=0.05, rely=0.5)
                rename_train_entry.place_errentry(relx=0.05, rely=0.7)
                target_train_frame.grid(row=training_classes.index(target), column=0, pady=10)

                self.view.vars[f"y rename {training_classes.index(target)}"] = rename_train_var
                self.view.vars[f"y label {training_classes.index((target))}"] = target_train_label_var

                self.model.plot_data[f"y rename {training_classes.index(target)}"] = rename_train_var.get()
                self.model.plot_data[f"y label {training_classes.index(target)}"] = target_train_label_var.get()

                for key, widget in {f"y rename {training_classes.index(target)}": rename_train_var,
                                    f"y label {training_classes.index(target)}": target_train_label_var}.items():
                    widget.trace("w", partial(self.trace_vars_to_model, key))

            for target in testing_classes:
                target_test_frame = ctk.CTkFrame(master=ticks_test_scrollable, height=130, width=225)
                original_test_label = ctk.CTkLabel(master=target_test_frame, text="Original target:")
                target_test_label_var = tk.StringVar(value=target)
                target_test_label = ctk.CTkLabel(master=target_test_frame, textvariable=target_test_label_var)
                rename_test_label = ctk.CTkLabel(master=target_test_frame, text="Rename target")
                rename_test_var = tk.StringVar()
                rename_test_entry = ErrEntry(master=target_test_frame, textvariable=rename_test_var)

                original_test_label.place(relx=0.05, rely=0)
                target_test_label.place(relx=0.05, rely=0.2)
                rename_test_label.place(relx=0.05, rely=0.5)
                rename_test_entry.place_errentry(relx=0.05, rely=0.7)
                target_test_frame.grid(row=testing_classes.index(target), column=0, pady=10)

                self.view.vars[f"x rename {testing_classes.index(target)}"] = rename_test_var
                self.view.vars[f"x label {testing_classes.index((target))}"] = target_test_label_var

                self.model.plot_data[f"x rename {testing_classes.index(target)}"] = rename_test_var.get()
                self.model.plot_data[f"x label {testing_classes.index(target)}"] = target_test_label_var.get()

                for key, widget in {f"x rename {testing_classes.index(target)}": rename_test_var,
                                    f"x label {testing_classes.index(target)}": target_test_label_var}.items():
                    widget.trace("w", partial(self.trace_vars_to_model, key))

    def _input_validation(self):
        """
       Validates the input data and configuration before performing actions that depend on them.

       If any errors are found, an error message is displayed in a popup, and the function returns `False`.
       If no errors are found, the function returns `True`.

       Returns:
           bool: `True` if validation passes, `False` if validation fails and errors are shown.
       """
        errors = []
        if not self.model.clf:
            errors.append("No classifier loaded.")

        if self.model.dataset is None:
            errors.append("No dataset loaded.")

        for key, entry in self.view.entries.items():
            if type(entry) == ErrEntry:
                if entry.error_message.get() != '':
                    errors.append(f"{key} : {entry.error_message.get()}")

        if errors:
            messagebox.showerror('Value Error', '\n'.join(errors))
            return False

        return True

    def _build_confusion_matrix(self, predictions, targets, training_targets, testing_targets):
        """
          Builds a confusion matrix and computes the mean probabilities of predictions for each class.
    
          Parameters
          ----------
          predictions : list of tuple
              Each element is a tuple containing predicted label and its associated probabilities.
    
          targets : list[int]
              List of true labels for the dataset.
    
          training_targets : list[str]
              List of unique class labels used for training.
    
          testing_targets : list[str]
              List of unique class labels used for testing.
    
          Returns
          -------
          matrix : np.ndarray
              A confusion matrix counting the occurrences of predicted vs true labels.
    
          mean_probabilities : np.ndarray
              A matrix containing the mean probabilities for each predicted vs true label combination.
          """
        if self.cancelled:
            return None, None
        self.progress.update_task("Building matrix")
        matrix = np.zeros((len(training_targets), len(testing_targets)))

        probabilities_matrix = np.empty((len(training_targets), len(testing_targets)), dtype=object)
        if self.cancelled:
            return None, None
        # Initializing the matrix containing the probabilities
        for i in range(len(probabilities_matrix)):
            for j in range(len(probabilities_matrix[i])):
                probabilities_matrix[i][j] = []

        if self.cancelled:
            return None, None
        for i in range(len(targets)):
            y_true = targets[i]
            y_pred = predictions[i][0]
            y_proba = max(predictions[i][1])
            matrix[self.TRAIN_CORRESPONDENCE[y_pred]][self.TEST_CORRESPONDENCE[y_true]] += 1

            probabilities_matrix[self.TRAIN_CORRESPONDENCE[y_pred]][self.TEST_CORRESPONDENCE[y_true]].append(y_proba)

        if self.cancelled:
            return None, None
        mean_probabilities = np.zeros((len(training_targets), len(testing_targets)))

        for i in range(len(probabilities_matrix)):
            for j in range(len(probabilities_matrix[i])):
                mean_probabilities[i][j] = np.mean(probabilities_matrix[i][j])
        if self.cancelled:
            return None, None
        self.progress.increment_progress(1)

        return matrix, mean_probabilities

    def _mix_counts_and_probs(self, overall_matrix, mean_probabilities_matrix,
                              accuracies_numeric, accuracies_percent, ):
        """
        Combines count-based confusion matrix values with probability-based metrics (CUP).
    
        Parameters
        ----------
        overall_matrix : np.ndarray
            Confusion matrix with raw count values.
    
        mean_probabilities_matrix : np.ndarray
            Matrix containing the mean probabilities of predictions.
    
        accuracies_numeric : np.ndarray
            Numeric confusion matrix (integer values).
    
        accuracies_percent : np.ndarray
            Percentage-based confusion matrix.
    
        Returns
        -------
        cups : list
            Matrix containing CUP values (rounded mean probabilities).
        """
        total_per_column = np.sum(overall_matrix, axis=0, where=overall_matrix != 0)  # Avoid division by zero
        cups = [[0] * overall_matrix.shape[1] for _ in range(overall_matrix.shape[0])]

        for i in range(len(overall_matrix)):
            for j in range(len(overall_matrix[i])):
                count_value = np.nan_to_num(overall_matrix[i][j])  # Ensure no NaNs
                mean_prob = np.nan_to_num(mean_probabilities_matrix[i][j])

                # Calculate CUP (mean probability), but only if count > 0
                CUP = round(float(mean_prob), 3) if int(count_value) != 0 else 0

                # Calculate percentage accuracy, ensuring no division by zero
                if int(count_value) != 0 and total_per_column[j] > 0:
                    percent = round(int(count_value) / total_per_column[j] * 100, 1)
                else:
                    percent = "0"

                accuracies_numeric[i][j] = int(count_value)
                accuracies_percent[i][j] = percent
                cups[i][j] = CUP

                if self.cancelled:
                    return None, None, None
                self.progress.increment_progress(1)
        return accuracies_percent, accuracies_numeric, cups

    def _init_train_and_test_correspondence(self, training_targets, testing_targets):
        """
        Initialize TRAIN_CORRESPONDENCE and TEST_CORRESPONDENCE of the train and test targets.
    
        Parameters
        ----------
        training_targets : list[str]
              List of unique class labels used for training.
    
        testing_targets : list[str]
          List of unique class labels used for testing.
    
        Returns
        -------
    
        """
        self.TRAIN_CORRESPONDENCE.clear()
        self.TEST_CORRESPONDENCE.clear()

        train_target_id = 0
        test_target_id = 0
        for t in training_targets:
            if t not in self.TRAIN_CORRESPONDENCE:
                self.TRAIN_CORRESPONDENCE[t] = train_target_id
                train_target_id += 1
        for t in testing_targets:
            if t not in self.TEST_CORRESPONDENCE:
                self.TEST_CORRESPONDENCE[t] = test_target_id
                test_target_id += 1

        if not self.TEST_CORRESPONDENCE:
            self.TEST_CORRESPONDENCE = self.TRAIN_CORRESPONDENCE.copy()

    def _test_clf_by_confusion(self, test_dataset: pd.DataFrame, training_targets, testing_targets, iterations=1,
                               **kwargs):
        """
        Tests a trained Random Forest classifier model using a confusion matrix.
    
        This method evaluates the classifier on a test dataset, which can have different
        target labels than those used for training. The confusion matrix and relevant
        performance metrics are computed.
    
        Parameters
        ----------
        test_dataset : pd.DataFrame
            Contains the test data. Each row represents an entry, while
            the columns correspond to the features on which the model was trained.
            The last column should be 'label', containing the target labels.
    
        training_targets : list[str]
            The target labels used during model training.
        
        testing_targets : list[str]
                    The target labels for testing. Can be different from `training_targets`.
            
        iterations : int, optional, default=10
            Number of iterations to run the test.
    
        Returns
        -------
        tuple of pd.DataFrame
            df_acc_numeric : pd.DataFrame
                Confusion matrix with raw count values.
    
            df_acc_percent : pd.DataFrame
                Confusion matrix with percentage-based accuracy values.
    
            df_cup : pd.DataFrame
                Matrix containing mean prediction probabilities (CUP).
    
    
        Notes
        -----
        - The function assumes a trained Random Forest classifier is already loaded in `self.model.clf`.
        - The test dataset must contain all necessary features for inference.
        - If `iterations` is greater than 1, the test runs multiple times for better statistical representation.
    
        """
        if self.cancelled:
            return None, None, None
        self.progress.update_task("Data preparation")
        if not testing_targets:
            testing_targets = training_targets

        self._init_train_and_test_correspondence(training_targets, testing_targets)

        if self.cancelled:
            return None, None, None
        X = test_dataset.loc[:, ~test_dataset.columns.isin(['label', 'ID'])]
        y = test_dataset["label"]

        X.reset_index(drop=True, inplace=True)

        if self.cancelled:
            return None, None, None
        self.progress.increment_progress(1)

        # get predictions and probabilities
        all_matrices = []
        all_probability_matrices = []

        if self.cancelled:
            return None, None, None
        for iters in range(iterations):
            if self.cancelled:
                return None, None, None
            self.progress.update_task("Predicting")
            predictions = self.predict_X_values(X)

            targets = []
            for i in y.index:
                targets.append(y.loc[i])

            matrix, mean_probabilities = self._build_confusion_matrix(predictions, targets, training_targets,
                                                                      testing_targets)
            if self.cancelled:
                return None, None, None
            all_matrices.append(matrix)
            all_probability_matrices.append(mean_probabilities)
        if self.cancelled:
            return None, None, None
        self.progress.update_task("Formatting matrices")
        mean_probabilities_matrix = np.empty((len(training_targets), len(testing_targets)))
        overall_matrix = np.mean(np.array([i for i in all_matrices]), axis=0)
        overall_probabilities = np.mean(np.array([i for i in all_probability_matrices]), axis=0)
        accuracies_percent = np.empty((len(training_targets), len(testing_targets))).tolist()
        accuracies_numeric = np.empty((len(training_targets), len(testing_targets))).tolist()

        if self.cancelled:
            return None, None, None
        # averaging the probabilities
        for i in range(len(overall_probabilities)):
            for j in range(len(overall_probabilities[i])):
                mean_probabilities_matrix[i][j] = np.mean(overall_probabilities[i][j])
                if self.cancelled:
                    return None, None, None
                self.progress.increment_progress(1)

        # mixing count and probabilities for displaying
        accuracies_percent, accuracies_numeric, cups = (
            self._mix_counts_and_probs(overall_matrix, mean_probabilities_matrix, accuracies_numeric,
                                       accuracies_percent))

        if self.cancelled:
            return None, None, None
        self.progress.update_task("Formatting results")
        columns = [x for x in self.TEST_CORRESPONDENCE.keys()]
        indexes = [x for x in self.TRAIN_CORRESPONDENCE.keys()]
        df_acc_percent = pd.DataFrame(columns=columns, index=indexes, data=accuracies_percent)
        df_acc_numeric = pd.DataFrame(columns=columns, index=indexes, data=accuracies_numeric)

        df_cup = pd.DataFrame(columns=columns, index=indexes, data=cups)
        df_acc_percent.index.name = "Train label"
        df_acc_numeric.index.name = "Train label"
        df_cup.index.name = "Train label"
        if self.cancelled:
            return None, None, None
        self.progress.increment_progress(1)

        return df_acc_numeric, df_acc_percent, df_cup,

    def _confusion_number_of_tasks(self, df):
        """
        Calculates the total number of tasks involved in generating and formatting a confusion matrix.
    
        This includes tasks related to data preparation, making predictions, building the confusion matrix,
        formatting the results, and returning the final output.
    
        Args:
            df (pd.DataFrame): DataFrame containing the data, where the last column is 'label' with the target values,
                               and the other columns represent the feature set for model predictions.
    
        Returns:
            int: Total number of tasks required to complete the confusion matrix generation.
        """
        data_preparation = 1
        n_iter = self.view.vars["iterations"].get()
        X = df.loc[:, ~df.columns.isin(['label', 'ID'])]
        y = df["label"]
        n_predictions = len(X.values)
        n_targets = len(y.index)
        building_matrix = 1 * n_iter
        formatting_matrices = len(self.model.testing_classes) * len(self.model.training_classes) * 2
        returning = 1
        total_tasks = (n_iter * n_predictions + data_preparation + building_matrix +
                       formatting_matrices + returning)
        return total_tasks
