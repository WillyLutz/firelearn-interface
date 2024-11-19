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
from tkinter import filedialog, messagebox
from scripts import params as p

import fiiireflyyy.learn as fl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,  NavigationToolbar2Tk

from scripts.WIDGETS.ErrEntry import ErrEntry


class ConfusionController:
    def __init__(self, view, ):
        self.model = ConfusionModel()
        self.view = view
        self.view.controller = self  # set controller
        self.progress = None

    def load_clf(self, loaded=False):
        if loaded:
            self.view.vars["load clf"].set(self.model.clf_path)

            training_classes = list(set(list(self.model.clf.classes_)))

            for child in self.view.scrollable_frames["training"].winfo_children():
                child.destroy()
            for t in range(len(training_classes)):
                target_radio = ctk.CTkRadioButton(master=self.view.scrollable_frames["training"],
                                                  text=training_classes[t],
                                                  state='disabled', text_color_disabled='white'
                                                  )
                target_radio.select()
                target_radio.grid(row=t, column=0, padx=10, pady=10, sticky='w')
        else:
            filename = filedialog.askopenfilename(title="Open file",
                                                  filetypes=(("AI model", "*.rfc"),))
            if filename:
                clf = pickle.load(open(filename, "rb"))
                self.model.clf = clf

                self.view.vars["load clf"].set(filename)

                training_classes = list(set(list(self.model.clf.classes_)))

                for child in self.view.scrollable_frames["training"].winfo_children():
                    child.destroy()
                for t in range(len(training_classes)):
                    target_radio = ctk.CTkRadioButton(master=self.view.scrollable_frames["training"],
                                                      text=training_classes[t],
                                                      state='disabled', text_color_disabled='white'
                                                      )
                    target_radio.select()
                    target_radio.grid(row=t, column=0, padx=10, pady=10, sticky='w')
    
    def test_clf_by_confusion(self, test_dataset: pd.DataFrame, training_targets: tuple, return_data=False, **kwargs):
        """
        Test an already trained Random forest classifier model,
        resulting in a confusion matrix. The test can be done
        on targets_labels different from the targets_labels used for training
        the model.
            Parameters
            ----------
            clf: RandomForestClassifier
                the trained model.
            test_dataset:  pandas Dataframe.
                Dataframe containing the data used for testing the
                model. The rows are the entries, and the columns are
                the features on which the model has been trained.
                The last column is 'status' containing the labels
                of the targets_labels for each entry.
            training_targets: tuple of str
                the targets on which the model has been trained.
            **kwargs: keyword arguments
                savepath: str, optional, default: ""
                    If not empty, path where le result will be saved.
                verbose: Bool, optional. Default: False
                    Whether to display more information when computing
                    or not.
                show: Bool, optional. Default: True
                    Whether to show the resulting confusion matrix or not.
                iterations: int, optional. Default: 10
                    Number of iterations the test will be computed.
                commentary: str, optional. Default: ""
                    If any specification to add to the file name.
                testing_targets: tuple of str
                    the targets on which the model will be tested.
                    Can be different from the training targets.
                mode: ['numeric', 'percent'], default 'numeric'
        """
        options = {"verbose": False, "show": True,
                   "testing_targets": (),
                   "iterations": 10,
                   "commentary": "", "savepath": "", "title": ""}
        options.update(**kwargs)
        self.progress.update_task("Data preparation")
        if not options["testing_targets"]:
            options["testing_targets"] = training_targets
        TRAIN_CORRESPONDENCE = {}
        TEST_CORRESPONDENCE = {}
        train_target_id = 0
        test_target_id = 0
        for t in training_targets:
            if t not in TRAIN_CORRESPONDENCE:
                TRAIN_CORRESPONDENCE[t] = train_target_id
                train_target_id += 1
        for t in options["testing_targets"]:
            if t not in TEST_CORRESPONDENCE:
                TEST_CORRESPONDENCE[t] = test_target_id
                test_target_id += 1
        
        if not TEST_CORRESPONDENCE:
            TEST_CORRESPONDENCE = TRAIN_CORRESPONDENCE.copy()
        
        X = test_dataset.loc[:, ~test_dataset.columns.isin(['label', 'ID'])]
        y = test_dataset["label"]
        
        X.reset_index(drop=True, inplace=True)
        
        if options["verbose"]:
            progress = 0
            sys.stdout.write(f"\rTesting model: {progress}%")
            sys.stdout.flush()
        self.progress.increment_progress(1)
        
        # get predictions and probabilities
        all_matrices = []
        all_probability_matrices = []
        for iters in range(options["iterations"]):
            self.progress.update_task("Predicting")
            matrix = np.zeros((len(training_targets), len(options['testing_targets'])))
            probabilities_matrix = np.empty((len(training_targets), len(options['testing_targets'])), dtype=object)
            
            # Initializing the matrix containing the probabilities
            for i in range(len(probabilities_matrix)):
                for j in range(len(probabilities_matrix[i])):
                    probabilities_matrix[i][j] = []
            
            # Making predictions and storing the results in predictions[]
            predictions = []
            for i in range(len(X.values)):
                row = X.iloc[i]
                y_pred = self.model.clf.predict([row])[0]
                proba_class = self.model.clf.predict_proba([row])[0]
                predictions.append((y_pred, proba_class))
                self.progress.increment_progress(1)
            
            #
            targets = []
            for i in y.index:
                targets.append(y.loc[i])
            # Building the confusion matrix
            self.progress.update_task("Building matrix")
            for i in range(len(targets)):
                y_true = targets[i]
                y_pred = predictions[i][0]
                y_proba = max(predictions[i][1])
                matrix[TRAIN_CORRESPONDENCE[y_pred]][TEST_CORRESPONDENCE[y_true]] += 1
                
                probabilities_matrix[TRAIN_CORRESPONDENCE[y_pred]][TEST_CORRESPONDENCE[y_true]].append(y_proba)
                
            mean_probabilities = np.zeros((len(training_targets), len(options['testing_targets'])))
            
            for i in range(len(probabilities_matrix)):
                for j in range(len(probabilities_matrix[i])):
                    mean_probabilities[i][j] = np.mean(probabilities_matrix[i][j])
            all_matrices.append(matrix)
            all_probability_matrices.append(mean_probabilities)
            self.progress.increment_progress(1)

        self.progress.update_task("Formatting matrices")
        mean_probabilities_matrix = np.empty((len(training_targets), len(options['testing_targets'])))
        overall_matrix = np.mean(np.array([i for i in all_matrices]), axis=0)
        
        overall_probabilities = np.mean(np.array([i for i in all_probability_matrices]), axis=0)
        
        accuracies_percent = np.empty((len(training_targets), len(options['testing_targets']))).tolist()
        accuracies_numeric = np.empty((len(training_targets), len(options['testing_targets']))).tolist()
        
        cups = np.empty((len(training_targets), len(options['testing_targets']))).tolist()
        
        # averaging the probabilities
        for i in range(len(overall_probabilities)):
            for j in range(len(overall_probabilities[i])):
                mean_probabilities_matrix[i][j] = np.mean(overall_probabilities[i][j])
                self.progress.increment_progress(1)

        
        # mixing count and probabilities for displaying
        
        total_per_column = np.sum(overall_matrix, axis=0)
        
        for i in range(len(overall_probabilities)):
            for j in range(len(overall_probabilities[i])):
                np.nan_to_num(overall_matrix[i][j])
                np.nan_to_num(mean_probabilities_matrix[i][j])
                CUP = round(mean_probabilities_matrix[i][j], 3) if int(overall_matrix[i][j]) != 0 else 0
                
                percent = round(int(overall_matrix[i][j]) / total_per_column[j] * 100, 1) if int(
                    overall_matrix[i][j]) != 0 else "0"
                
                accuracies_numeric[i][j] = int(overall_matrix[i][j])
                accuracies_percent[i][j] = percent
                cups[i][j] = CUP
                self.progress.increment_progress(1)
                
        
        self.progress.update_task("Formatting results")
        columns = [x for x in TEST_CORRESPONDENCE.keys()]
        indexes = [x for x in TRAIN_CORRESPONDENCE.keys()]
        df_acc_percent = pd.DataFrame(columns=columns, index=indexes, data=accuracies_percent)
        df_acc_numeric = pd.DataFrame(columns=columns, index=indexes, data=accuracies_numeric)
        
        df_cup = pd.DataFrame(columns=columns, index=indexes, data=cups)
        df_acc_percent.index.name = "Train label"
        df_acc_numeric.index.name = "Train label"
        df_cup.index.name = "Train label"
        self.progress.increment_progress(1)
        if return_data:
            return df_acc_numeric, df_acc_percent, df_cup, TRAIN_CORRESPONDENCE, TEST_CORRESPONDENCE
            # return overall_matrix, mixed_labels_matrix, TRAIN_CORRESPONDENCE, TEST_CORRESPONDENCE
        
        mixed_labels_matrix = np.empty((len(TRAIN_CORRESPONDENCE.keys()), len(TEST_CORRESPONDENCE.keys()))).tolist()
        
        acc_array = df_acc_percent.to_numpy().astype(float) if options[
                                                                   "mode"] == 'percent' else df_acc_numeric.to_numpy().astype(
            int)
        
        cup_array = df_cup.to_numpy()
        for r in range(len(acc_array)):
            for c in range(len(acc_array[0])):
                case = f"{acc_array[r][c]}%\nCUP={cup_array[r][c]}" if options[
                                                                           "mode"] == 'percent' else f"{acc_array[r][c]}\nCUP={cup_array[r][c]}"
                mixed_labels_matrix[r][c] = case
        plt.close()
        
        # plotting
        fig, ax = plt.subplots(1, 1, figsize=(7 / 4 * len(options['testing_targets']), 6 / 4 * len(training_targets)))
        
        fig.suptitle("")
        sns.heatmap(ax=ax, data=acc_array, annot=mixed_labels_matrix, fmt='', cmap="Blues", square=True, )
        ax.xaxis.tick_top()
        ax.xaxis.set_label_position('top')
        ax.set_ylabel("The input is classified as")
        ax.set_xlabel("The test input is")
        ax.set_xticks([TEST_CORRESPONDENCE[x] + 0.5 for x in options['testing_targets']], options['testing_targets'])
        ax.set_yticks([TRAIN_CORRESPONDENCE[x] + 0.5 for x in training_targets], training_targets)
        plt.tight_layout()
        
        if options['savepath']:
            plt.savefig(os.path.join(options['savepath'], options["title"] + ".png"))
        if options['show']:
            plt.show()
        plt.close()
    
    def confusion_number_of_tasks(self, df):
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
        
    def compute_confusion(self, ):
        if self.input_validation():
            plt.close()
            training_classes = tuple(list(set(list(self.model.clf.classes_))))
            all_testing_classes = {key: value for (key, value) in self.view.vars.items() if "test label " in key}

            checked_classes = {key: value for (key, value) in all_testing_classes.items() if value.get() == 1}
            checked_classes_names = {self.view.ckboxes[key].cget('text'): value for (key, value) in
                                     checked_classes.items()}.keys()
            testing_classes = tuple(checked_classes_names)

            self.model.training_classes = training_classes
            self.model.testing_classes = testing_classes

            df = self.model.dataset
            df = df[df[self.view.vars["label column"].get()].isin(testing_classes)]
            
            self.progress = ProgressBar("Confusion computation", app=self.view.app)
            self.progress.total_tasks = self.confusion_number_of_tasks(df)
            self.progress.start()
            
            overall_matrix_numeric, overall_matrix_percent, overall_matrix_cup, TRAIN_CORRESPONDENCE, TEST_CORRESPONDENCE \
                = self.test_clf_by_confusion(df, training_targets=training_classes,
                                           testing_targets=testing_classes, show=False,
                                           iterations=self.view.vars["iterations"].get(),
                                           return_data=True,
                                           mode=self.model.plot_specific_settings["annot mode"],
                                           progress_bar=self.progress)  # todo : update fiiireflyyy
            self.model.confusion_data["overall matrix numeric"] = overall_matrix_numeric
            self.model.confusion_data["overall matrix percent"] = overall_matrix_percent

            self.model.confusion_data["overall matrix cup"] = overall_matrix_cup
            self.model.confusion_data["train correspondence"] = TRAIN_CORRESPONDENCE
            self.model.confusion_data["test correspondence"] = TEST_CORRESPONDENCE

            self.update_figure()

    def update_figure(self):
        plt.close()
        overall_matrix = self.model.confusion_data["overall matrix percent"] \
            if self.model.plot_specific_settings["annot mode"] == 'percent' \
            else self.model.confusion_data["overall matrix numeric"]
        overall_matrix_cup = self.model.confusion_data["overall matrix cup"]
        TRAIN_CORRESPONDENCE = self.model.confusion_data["train correspondence"]
        TEST_CORRESPONDENCE = self.model.confusion_data["test correspondence"]
        
        acc_array = overall_matrix.to_numpy().astype(float) if self.model.plot_specific_settings["annot mode"] == 'percent' else overall_matrix.to_numpy().astype(
            int)
        cup_array = overall_matrix_cup.to_numpy()
        mixed_labels_matrix = np.empty((len(TRAIN_CORRESPONDENCE.keys()), len(TEST_CORRESPONDENCE.keys()))).tolist()
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
        
        sns.heatmap(ax=ax, data=overall_matrix, annot=mixed_labels_matrix, annot_kws={"font": self.model.plot_specific_settings["annot font"],
                                                                 "size": self.model.plot_specific_settings["annot size"]}, fmt='', cmap="Blues",
                    square=True, cbar_kws={'shrink': 0.5, 'location': 'right'})
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

        ax.set_xticks([TEST_CORRESPONDENCE[x] + 0.5 for x in self.model.testing_classes], self.model.testing_classes,
                      fontsize=self.model.plot_axes["x ticks size"],)
        ax.tick_params(axis='x', labelrotation=self.model.plot_axes["x ticks rotation"],
                       labelsize=self.model.plot_axes["x ticks size"],
                       labelfontfamily=self.model.plot_axes["axes font"])
        ax.tick_params(axis='y', labelrotation=self.model.plot_axes["y ticks rotation"],
                       labelsize=self.model.plot_axes["y ticks size"],
                       labelfontfamily=self.model.plot_axes["axes font"])
        
        ax.set_yticks([TRAIN_CORRESPONDENCE[x] + 0.5 for x in self.model.training_classes], self.model.training_classes, fontsize = self.model.plot_axes["y ticks size"])
        self.view.figures["confusion"] = (fig, ax)
        self.view.canvas["confusion"].draw()

    def input_validation(self):
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

    def save_figure(self, fig):

        filepath = filedialog.asksaveasfilename(title="Open file", filetypes=(("Image", "*.png"),))
        if filepath:
            if self.view.entries["dpi"]:
                fig.savefig(filepath, dpi=int(self.view.entries["dpi"].get()), bbox_inches='tight')

    def export_figure_data(self, ax):  # todo : export
        pass

    def save_config(self, ):
        if self.input_validation():
            f = filedialog.asksaveasfilename(defaultextension=".confcfg",
                                             filetypes=[("Analysis - Confusion", "*.confcfg"), ])
            if f:
                self.model.save_model(path=f, )

    def load_config(self, ):
        f = filedialog.askopenfilename(title="Open file", filetypes=(("Analysis - Confusion", "*.confcfg"),))
        if f:
            if self.model.load_model(path=f):
                if self.model.dataset_path:
                    self.load_clf(loaded=True)
                    self.load_dataset(loaded=True)

                self.update_view_from_model()

    def update_view_from_model(self, ):

        for key, value in self.model.plot_data.items():
            self.view.vars[key].set(value)
        for key, value in self.model.plot_legend.items():
            self.view.vars[key].set(value)
        for key, value in self.model.plot_axes.items():
            self.view.vars[key].set(value)
        for key, value in self.model.plot_general_settings.items():
            self.view.vars[key].set(value)

    def load_dataset(self, loaded=False):
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
        ckboxes = {key: value for (key, value) in self.view.vars.items() if "test label" in key}
        for key, widget in ckboxes.items():
            widget.set(0)

    def select_all_test_targets(self):
        ckboxes = {key: value for (key, value) in self.view.vars.items() if "test label" in key}
        for key, widget in ckboxes.items():
            widget.set(1)

    def trace_testing_labels(self, *args):
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
                    target_checkbox = ctk.CTkCheckBox(master=self.view.scrollable_frames["testing"],
                                                      variable=target_var,
                                                      text=possible_targets[t])
                    target_checkbox.grid(row=t, column=0, padx=10, pady=10, sticky='w')
                    self.view.vars[f"test label {t}"] = target_var
                    self.view.ckboxes[f"test label {t}"] = target_checkbox
                    self.model.plot_data[f"test label {t}"] = target_var.get()
                    target_var.trace("w", partial(self.trace_vars_to_model, f"test label {t}"))

    def trace_vars_to_model(self, key, *args):
        if key in self.model.plot_general_settings.keys():
            self.model.plot_general_settings[key] = self.view.vars[key].get()
        elif key in self.model.plot_axes.keys():
            self.model.plot_axes[key] = self.view.vars[key].get()
        elif key in self.model.plot_legend.keys():
            self.model.plot_legend[key] = self.view.vars[key].get()
        elif key in self.model.plot_specific_settings.keys():
            self.model.plot_specific_settings[key] = self.view.vars[key].get()

    def update_confusion_ticks(self, ):
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

    @staticmethod
    def rename_dict_key(d, old_key, new_key):
        if old_key in d:
            d[new_key] = d.pop(old_key)
