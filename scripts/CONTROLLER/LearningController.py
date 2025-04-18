import datetime
import os
import pickle
import threading
import tkinter as tk
from itertools import product
from multiprocessing import Queue
import multiprocessing
from queue import Empty
from random import shuffle
from threading import Thread
from tkinter import ttk, filedialog, messagebox

import customtkinter as ctk
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score

from scripts.CONTROLLER import input_validation as ival
from scripts.CONTROLLER.ProgressBar import ProgressBar
from scripts.CONTROLLER.input_validation import convert_to_type
from scripts.MODEL.LearningModel import LearningModel
from scripts.CONTROLLER.MainController import MainController
from scripts.PROCESSES.LearningProcess import LearningProcess
from scripts.PROCESSES.WatchDog import WatchDog
from scripts.WIDGETS.ErrEntry import ErrEntry
from scripts.WIDGETS.Separator import Separator
from sklearn.model_selection import ParameterGrid

import logging
logger = logging.getLogger("__Learning__")

class LearningController:
    def __init__(self, view, ):
        self.model = LearningModel()
        self.view = view
        self.view.controller = self  # set controller

        self.params_combination_queue = None
        self.learning_progress = None
        self.progress_queue = None
        self.result_queue = None

        self.scoring = 'Relative K-Fold CV accuracy'  # todo : add option for optimization metric

        self.threads_alive = False
        self.cancelled = False

    @staticmethod
    def _label_encoding(y):
        """
        Encodes the labels in the input list to numeric values.

        Parameters
        ----------
        y : DataFrame
            Column containing the labels to be encoded.

        Returns
        -------
        y : DataFrame
            The encoded labels.
        """
        labels = list(set(list(y)))
        corr = {}
        for lab in range(len(labels)):
            corr[labels[lab]] = lab

        for key, value in corr.items():
            y.replace(key, value)

        return y

    def reload_rfc_params(self, rfc_params_string_var):
        """
        Reloads the parameters of a Random Forest Classifier and sets them to the provided string variables.

        Parameters
        ----------
        rfc_params_string_var : dict
            A dictionary containing string variables to store the parameter values of the Random Forest Classifier.

        Returns
        -------
        dict
            default random forest classifier parameters
        """
        default_params = self.view.get_fixed_default_clf_params()

        for name, value in default_params.items():
            value = str(value)
            if value != rfc_params_string_var[name].get():
                rfc_params_string_var[name].set(value)
        return rfc_params_string_var

    @staticmethod
    def _extract_rfc_params(rfc_params_string_var):
        """
        Extracts the parameters for the Random Forest Classifier from the provided string variables.

        Parameters
        ----------
        rfc_params_string_var : dict
            A dictionary of string variables containing the parameter values for the Random Forest Classifier.

        Returns
        -------
        rfc_params : dict
            A dictionary containing the extracted parameter values for the Random Forest Classifier.
        """

        rfc_params = {}
        for key, widget in rfc_params_string_var.items():
            if 'class_weight' not in key:
                if ival.isint(widget.get()):
                    rfc_params[key] = int(widget.get())
                elif ival.isfloat(widget.get()):
                    rfc_params[key] = float(widget.get())
                elif widget.get() == 'None':
                    rfc_params[key] = None
                else:
                    rfc_params[key] = widget.get()
        return rfc_params

    def load_train_dataset(self, autoload=''):
        """
        Loads the training dataset from a file and updates the target column options in the view.

        Parameters
        ----------
        autoload : str, optional
            A predefined file path to load the dataset from. If empty, the user will be prompted to select a file.
            (default is '')

        Returns
        -------
        None
        """
        if not autoload:
            filename = filedialog.askopenfilename(title="Open file",
                                                  filetypes=(("Tables", "*.txt *.xls *.xlsx *.csv"),))
        else:
            filename = autoload
        strvar = self.view.vars["load train dataset"]
        label_cbbox = self.view.cbboxes["target column"]

        if filename:
            strvar.set(filename)
            self.model.train_dataset_path = filename
            df = pd.read_csv(filename, index_col=False)
            self.model.train_dataset = df
            label_cbbox.configure(state='normal')
            label_cbbox.configure(values=[str(c) for c in df.columns])
            self.view.vars["target column"].set(str(df.columns[0]))
            label_cbbox.configure(state='readonly')

            self.view.vars['target column'].trace('w', self._trace_target_column)

    def load_test_dataset(self, autoload=''):
        """
        Loads the test dataset from a file.

        Parameters
        ----------
        autoload : str, optional
            A predefined file path to load the dataset from. If empty, the user will be prompted to select a file.
            (default is '')

        Returns
        -------
        None
        """
        if not autoload:
            filename = filedialog.askopenfilename(title="Open file",
                                                  filetypes=(("Tables", "*.txt *.xls *.xlsx *.csv"),))
        else:
            filename = autoload

        strvar = self.view.vars["load test dataset"]
        if filename:
            strvar.set(filename)
            self.model.test_dataset_path = filename
            df = pd.read_csv(filename, index_col=False)
            self.model.test_dataset = df

    def add_subtract_target(self, mode='add'):
        """
        Adds or subtracts a target from the model's list of targets based on the specified mode.

        Parameters
        ----------
        mode : str, optional
            The mode of operation, either 'add' or 'subtract'. (default is 'add')

        Returns
        -------
        None
        """
        key = self.view.vars["key target"].get()

        targets = self.model.targets
        if mode == 'add':
            if key:
                targets.append(key)
            else:
                messagebox.showerror("Missing Value", "You need to indicate the key and the value to add a target.")
        elif mode == 'subtract':
            if key:
                try:
                    if key in targets:
                        targets.remove(key)
                except KeyError:
                    pass
            else:
                messagebox.showerror("Missing Value", "You need to indicate at least the key to delete a target.")
        self.model.targets = targets

        MainController.update_textbox(self.view.textboxes["targets"], self.model.targets)

    def clear_targets(self):
        self.model.targets.clear()
        MainController.update_textbox(self.view.textboxes["targets"], self.model.targets)

    def savepath_rfc(self, strvar):
        """
        Opens a file dialog to select a location to save the Random Forest Classifier model.

        Parameters
        ----------
        strvar : tk.StringVar
            A string variable to store the path of the saved model.

        Returns
        -------
        None
        """
        filename = filedialog.asksaveasfilename(title="Save as",
                                                filetypes=(("Random Forest Classifier", "*.rfc"),))
        if filename:
            strvar.set(filename)
            self.model.save_rfc_directory = filename

    def load_rfc(self, rfc_params_string_var, strvars):
        """
        Loads a Random Forest Classifier model from a file and updates the relevant parameters and string variables.

        Parameters
        ----------
        rfc_params_string_var : dict
            A dictionary of string variables to update with the model parameters.
        strvars : dict
            A dictionary of string variables to update with the model file path and status.

        Returns
        -------
        None
        """
        filename = filedialog.askopenfilename(title="Open file",
                                              filetypes=(("AI model", "*.rfc"),))
        if filename:
            clf = pickle.load(open(filename, "rb"))
            self.model.rfc = clf

            for name, value in clf.get_params().items():
                rfc_params_string_var[name].set(value)

            strvars["rfc path"].set(os.path.dirname(filename))
            strvars["rfc name"].set(os.path.basename(filename))
            strvars["rfc status"].set("True")

    def _get_param_grid_search(self, ):
        """
        Extracts the parameter grid for performing a grid search by considering the checked hyperparameters and
        their corresponding values.

        Returns
        -------
        param_grid : dict
            A dictionary where the keys are the hyperparameters and the values are lists of values to be used in the grid search.
        """
        rfc_params = self._extract_rfc_params(self.view.rfc_params_stringvar)
        param_grid = {}

        checked_hyperparams = [key for key in self.model.hyperparameters_to_tune.keys() if
                               self.view.ckboxes[f"hyperparameter {key}"].get()]
        for param, values in [(param, self.view.entries[f"hyperparameter {param}"].get()) for param in
                              checked_hyperparams]:  # params to be optimized
            indiv_values = [val.strip() for val in values.split(',')]

            # check for 'None' values as string and replace them by actual None
            # indiv_values = self._convert_list_elements(indiv_values)
            converted_indiv_values = [ival.convert_to_type(value) for value in indiv_values]

            param_grid[param] = converted_indiv_values

        for k, v in rfc_params.items():  # params with a single value
            if k not in param_grid.keys():
                param_grid[k] = [v, ]
        return param_grid

    def update_total_tasks(self, num_combinations):
        loading = 1
        splitting = 3

        training = 3
        testing = 2
        params_done = 1
        k_fold = 1
        format_metrics = 1
        per_worker = training + testing + k_fold + format_metrics + params_done

        learning = num_combinations  # per_worker*num_combinations

        terminate_workers = 1
        best_perf = 1
        finishing_display = 1
        saving_model = 1 if self.view.vars["save rfc"].get() else 0
        post_learning = terminate_workers + best_perf + finishing_display + saving_model

        total_tasks = loading + splitting + learning + post_learning

        return total_tasks

    def _learning_process(self):
        self.learning_progress = ProgressBar("Learning", self.view.app, self)

        param_grid = self._get_param_grid_search()
        num_combinations = len(list(product(*param_grid.values())))


        self.learning_progress.total_tasks = self.update_total_tasks(num_combinations)
        self.learning_progress.start()
        self.learning_progress.update_task("Loading dataset")

        full_df = pd.read_csv(self.model.full_dataset_path, index_col=False)
        train_df = pd.read_csv(self.model.train_dataset_path, index_col=False)
        test_df = pd.read_csv(self.model.test_dataset_path, index_col=False)

        self.learning_progress.increment_progress(1)
        self.learning_progress.update_task("Splitting")

        target_column = self.model.cbboxes["target column"]
        full_df[target_column] = full_df[target_column].astype(str)
        full_df = full_df[full_df[target_column].isin(self.model.targets)]
        full_df.reset_index(inplace=True, drop=True)
        y_full = full_df[target_column]
        y_full = self._label_encoding(y_full)
        X_full = full_df.loc[:, full_df.columns != target_column]
        self.learning_progress.increment_progress(1)

        train_df[target_column] = train_df[target_column].astype(str)
        train_df = train_df[train_df[target_column].isin(self.model.targets)]
        train_df.reset_index(inplace=True, drop=True)
        y_train = train_df[target_column]
        y_train = self._label_encoding(y_train)
        X_train = train_df.loc[:, train_df.columns != target_column]
        self.learning_progress.increment_progress(1)

        test_df[target_column] = test_df[target_column].astype(str)
        test_df = test_df[test_df[target_column].isin(self.model.targets)]
        test_df.reset_index(inplace=True, drop=True)
        y_test = test_df[target_column]
        y_test = self._label_encoding(y_test)
        X_test = test_df.loc[:, test_df.columns != target_column]

        self.learning_progress.increment_progress(1)
        self.learning_progress.update_task("Distributed learning")

        all_params_grid = ParameterGrid(param_grid)
        converted_all_params_grid = []
        for p_grid in all_params_grid:
            converted_p_grid = ival.convert_dict_values_from_str(p_grid)
            converted_all_params_grid.append(converted_p_grid)

        all_params_grid_list = converted_all_params_grid
        n_cpu = multiprocessing.cpu_count()
        n_workers = 1
        if len(all_params_grid) > int(0.7 * n_cpu):
            n_workers = 1 if int(0.7 * n_cpu) == 0 else int(0.7 * n_cpu)
        elif len(all_params_grid) < int(0.7 * multiprocessing.cpu_count()):
            n_workers = len(all_params_grid)

        shuffle(all_params_grid_list)
        self.params_combination_queue = multiprocessing.Queue()
        self.progress_queue = multiprocessing.Queue()
        self.result_queue = multiprocessing.Queue()

        # populate the queue with parameters combinations to test
        for combination in all_params_grid_list:
            self.params_combination_queue.put(combination)

            # add sentinel values
        for _ in range(n_workers):
            self.params_combination_queue.put(None)
        lock = threading.Lock()
        all_prisoners = [LearningProcess(self.params_combination_queue,
                                         self.result_queue,
                                         self.progress_queue,
                                         X_train, y_train,
                                         X_test, y_test,
                                         X_full, y_full,
                                         self.model.enable_kfold,
                                         self.model.kfold,
                                         lock,
                                         )
                         for _ in range(1)
                         ]

        for p in all_prisoners:
            logger.info(p)
            p.start()

        watch_dog = WatchDog(all_prisoners)
        watch_dog.start()
        results = {}
        finished_prisoners = 0
        # while not self.progress_queue.empty():
        #     self.learning_progress.increment_progress(self.progress_queue.get_nowait())

        while watch_dog.watching() and finished_prisoners != len(
                all_prisoners) and self.learning_progress.progress_window.winfo_exists():
            self.learning_progress.update_task("Threaded learning...")

            try:
                while not self.progress_queue.empty():
                    self.learning_progress.increment_progress(self.progress_queue.get_nowait())
            except Empty:
                pass

            try:
                while not self.result_queue.empty():
                    self.learning_progress.update_task("Storing results...")
                    result = self.result_queue.get_nowait()  # Use get_nowait() to avoid blocking
                    if type(result) is str:  # A Worker finished ! joining it
                        finished_prisoners += 1
                        logger.info(f"Prisoner finishing {result} - finished prisoners: {finished_prisoners}")

                    else:
                        random_key, formatted_metrics = result
                        results[random_key] = formatted_metrics  # Store results dynamically
            except Empty:
                # No progress item was available; just continue looping.
                pass



        if self.cancelled:
            logger.info("Learning has been cancelled ! Cleaning threads and queues")
            watch_dog.stop()
            # emptying queues
            while not self.params_combination_queue.empty():
                self.params_combination_queue.get_nowait()

            while not self.progress_queue.empty():
                self.progress_queue.get_nowait()

            while not self.result_queue.empty():
                self.result_queue.get_nowait()  # Use get_nowait() to avoid blocking

        else:

            self.learning_progress.update_task("Finishing threaded learning...")
            if finished_prisoners == len(all_prisoners):
                watch_dog.stop()
            while not self.progress_queue.empty():
                self.learning_progress.increment_progress(self.progress_queue.get_nowait())

            while not self.result_queue.empty():
                processed_files_to_make_dataset, filename = self.result_queue.get_nowait()  # Use get_nowait() to avoid blocking
                results[filename] = processed_files_to_make_dataset  # Store results dynamically

            self.cancelled = True if any(
                [w.is_alive() for w in all_prisoners]) and not self.learning_progress.is_alive() else False

            self.learning_progress.update_task("Terminating threads...")
            for worker in all_prisoners:
                logger.info(f"joining {worker.name}")
                worker.join(timeout=5)
                if worker.is_alive():
                    logger.info("thread is alive, joining")
                    worker.join()
            watch_dog.join()
            logger.info("Watch dog is joined")

            self.learning_progress.increment_progress(1)

        for _ in range(1):
            if self.cancelled:
                break
            self.learning_progress.update_task("Getting best performing combination...")

            best_key = self._get_best_performing_combination(results)
            self.learning_progress.increment_progress(1)
            # MainController.update_textbox(self.model.textboxes)
            if self.cancelled:
                break

            metrics_text_elements = []
            metrics_text_elements = self._learning_display_computed_metrics(best_key,
                                                                            metrics_text_elements,
                                                                            results)
            if self.cancelled:
                break

            self._update_metrics_textbox(metrics_text_elements)
            if self.view.vars["save rfc"].get():
                self.learning_progress.update_task("Saving best performing model...")

                MainController.save_object(results[best_key][4], self.view.vars["save rfc"].get())
                self.learning_progress.increment_progress(1)
            self.learning_progress.increment_progress(1)
            self.threads_alive = False

        if self.cancelled:
            messagebox.showinfo("Cancel Learning", "All workers properly terminated.")
        else:
            logger.info("All workers properly terminated.")

        self.threads_alive = False
        self.cancelled = False

    def learning(self, ):
        """
        Main learning function that trains and tests the model, performs k-fold cross-validation (if enabled),
        and displays the computed metrics based on the chosen scoring method.

        Returns
        -------
        None
        """
        start_learning = datetime.datetime.now()
        if self._check_params_validity():
            for widgets in [self.view.ckboxes, self.view.entries, self.view.cbboxes, self.view.sliders, self.view.vars,
                            self.view.switches, self.view.textboxes, ]:
                self._update_params(widgets)
            self._update_rfc_params(self.view.rfc_params_stringvar)

            # thread = Thread(target=self._learning_process, daemon=True)
            # thread.start()
            self._learning_process()
            end_learning = datetime.datetime.now()
            logger.info(f"Learning time: {end_learning - start_learning}")

    @staticmethod
    def _compute_trust_score(train_score, test_score, all_cv_scores):
        kcv = np.mean(all_cv_scores)
        kcv_std = np.std(all_cv_scores)
        kfold_acc_diff = round(train_score - kcv, 3)
        kfold_acc_relative_diff = round(kfold_acc_diff / train_score * 100, 2)
        return (test_score * kfold_acc_relative_diff) / (1 + np.abs(train_score - test_score) + kcv_std)

    def _get_best_performing_combination(self, all_params_combination):
        """
        Identifies the key of the best performing model based on the selected scoring method.

        Parameters
        ----------
        all_params_combination : dict
            Contains all the tested combinations in the format
            {random_key: (combination, all_cv_scores, train_score, test_score, clf), ...}

        Returns
        -------
        best_key : str
            The key of the best performing model.
        """
        best_key = ''

        if self.scoring == "Trust score":
            best_trust = 0
            for random_key, metrics in all_params_combination.items():
                all_cv_scores = metrics[1]
                train_score = metrics[2]
                test_score = metrics[3]
                trust = self._compute_trust_score(train_score=train_score,
                                                  test_score=test_score,
                                                  all_cv_scores=all_cv_scores)

                best_key = random_key if trust > best_trust else best_key
                best_trust = max(trust, best_trust)

                logger.debug(f"{trust} {metrics}")

        if self.scoring == 'Relative K-Fold CV accuracy':
            best_rel_cv = 100
            for random_key, metrics in all_params_combination.items():
                all_cv_scores = metrics[1]
                train_score = metrics[2]

                kcv = np.mean(all_cv_scores)
                kfold_acc_diff = round(train_score - kcv, 3)
                kfold_acc_relative_diff = round(kfold_acc_diff / train_score * 100, 2)
                best_key = random_key if kfold_acc_relative_diff < best_rel_cv else best_key
                best_rel_cv = kfold_acc_relative_diff if kfold_acc_relative_diff < best_rel_cv else best_rel_cv

        if self.scoring == 'K-Fold CV accuracy':
            best_cv = 0
            for random_key, metrics in all_params_combination.items():
                all_cv_scores = metrics[1]
                kcv = np.mean(all_cv_scores)
                best_key = random_key if kcv > best_cv else best_key
                best_cv = kcv if kcv > best_cv else best_cv

        if self.scoring == 'Training accuracy':
            best_acc = 0
            for random_key, metrics in all_params_combination.items():
                train_score = metrics[2]
                best_key = random_key if train_score > best_acc else best_key
                best_acc = train_score if train_score > best_acc else best_acc
        if self.scoring == 'Testing accuracy':
            best_acc = 0
            for random_key, metrics in all_params_combination.items():
                test_score = metrics[3]
                best_key = random_key if test_score > best_acc else best_key
                best_acc = test_score if test_score > best_acc else best_acc

        return best_key

    def _learning_display_computed_metrics(self,
                                           best_key,
                                           metrics_text_elements,
                                           all_param_combinations):
        """
        Displays the computed classification metrics including accuracy, cross-validation score, and the
        parameter combination of the best performing model.

        Parameters
        ----------
        best_key : str
            The key of the best performing model.
        metrics_text_elements : list[str]
            A list of text elements to be displayed in the metrics section.
        all_param_combinations : dict
            All combinations of parameters alongside the computed metrics used during training.

        Returns
        -------
        metrics_text_elements : list
            Updated list of text elements with computed metrics to display.
        """
        metrics_text_elements.append("CLASSIFICATION METRICS")
        metrics_text_elements.append("---------------------------------------------------------------")
        metrics_text_elements.append("")

        pm = u"\u00B1"
        metrics_text_elements.append(f"Number of parameters combination : {len(all_param_combinations.keys())}", )

        metrics_text_elements.append("-" * 25)
        metrics_text_elements.append(f"Scoring function: {self.scoring}")
        metrics_text_elements.append("Best performing model metrics:")
        metrics_text_elements.append(f"Training accuracy: {all_param_combinations[best_key][2]}")
        metrics_text_elements.append(f"Testing accuracy: {all_param_combinations[best_key][3]}")
        if self.model.enable_kfold:
            acc = all_param_combinations[best_key][2]
            kcv = round(np.array(all_param_combinations[best_key][1]).mean(), 3)
            kcv_acc_diff = round(acc - kcv, 3)
            kcv_acc_relative_diff = round(kcv_acc_diff / acc * 100, 2)
            metrics_text_elements.append(f"{self.model.kfold}-fold Cross Validation: {kcv}")
            metrics_text_elements.append(f"KFold-Accuracy difference = {acc}-{kcv} = {kcv_acc_diff}\n")
            metrics_text_elements.append(f"KFold-Accuracy relative difference: {kcv_acc_relative_diff} %\n")

            all_cv_scores = all_param_combinations[best_key][1]
            train_score = all_param_combinations[best_key][2]
            test_score = all_param_combinations[best_key][3]
            trust_score = self._compute_trust_score(train_score=train_score, test_score=test_score,
                                                    all_cv_scores=all_cv_scores)
            metrics_text_elements.append(f"Trust score: {round(trust_score, 3)}")

        metrics_text_elements.append("")
        for param, value in all_param_combinations[best_key][0].items():
            metrics_text_elements.append(f"{param} : {value}")

        metrics_text_elements.append("")
        metrics_text_elements.append("-" * 30)
        metrics_text_elements.append("Average metrics across all iterations: ")
        all_train_scores = [all_param_combinations[key][2] for key in all_param_combinations.keys()]
        all_test_scores = [all_param_combinations[key][3] for key in all_param_combinations.keys()]
        all_cv_scores = [all_param_combinations[key][1] for key in all_param_combinations.keys()]
        mean_accuracy = np.mean(all_train_scores).round(3)
        metrics_text_elements.append(
            f"Training accuracy: {str(mean_accuracy)} {pm} {str(np.std(all_train_scores).round(3))}", )
        metrics_text_elements.append(
            f"Testing accuracy: {str(np.mean(all_test_scores).round(3))} {pm} {str(np.std(all_test_scores).round(3))}")

        if self.model.enable_kfold:
            mean_kfold = round(np.array(all_cv_scores).mean(), 3)
            std_kfold = round(np.array(all_cv_scores).std(), 3)
            kfold_acc_diff = round(mean_accuracy - mean_kfold, 3)
            kfold_acc_relative_diff = round(kfold_acc_diff / mean_accuracy * 100, 2)
            metrics_text_elements.append(
                f"{len(all_cv_scores[0])}-fold Cross Validation: {str(mean_kfold)} {pm} {str(std_kfold)}")
            metrics_text_elements.append(
                f"KFold-Accuracy difference = {mean_accuracy}-{mean_kfold} = {kfold_acc_diff}\n")
            metrics_text_elements.append(f"KFold-Accuracy relative difference: {kfold_acc_relative_diff} %\n")
        metrics_text_elements.append("")

        return metrics_text_elements

    def _update_metrics_textbox(self, elements):
        """
        Updates the metrics textbox with the given elements.

        Parameters
        ----------
        elements : list
            List of text elements to be displayed in the metrics textbox.

        Returns
        -------
        None
        """
        self.view.textboxes["metrics"].configure(state='normal')
        self.view.textboxes["metrics"].delete('1.0', tk.END)
        for elem in elements:
            elem = elem + "\n"
            self.view.textboxes["metrics"].insert(ctk.INSERT, elem)

        self.view.textboxes["metrics"].configure(state='disabled')

    def _check_params_validity(self, ):
        """
        Checks the validity of the parameters entered by the user.

        Returns
        -------
        bool
            True if parameters are valid, False otherwise.
        """
        if self.threads_alive:
            if self.cancelled:
                messagebox.showerror("Workers alive",
                                     "Workers from previous learning are still alive and being terminated."
                                     " Please wait a bit before starting a new learning")
                return False
            else:
                messagebox.showerror("Workers alive", "Workers are currently alive."
                                                      "To start a new learning, please either cancel the current one "
                                                      "or wait for it to finish.")
                return False

        if self.view.entries["save rfc"].get() == "":
            proceed = messagebox.askokcancel("No save directory", "You will run a training without"
                                                                  " saving the resulting model. Continue ?")
            if not proceed:
                return False
        elif not os.path.exists(os.path.dirname(self.view.entries["save rfc"].get())):
            messagebox.showerror("Value error", "Path to save the classifier does not exist.")
            return False

        if 'cv' in self.scoring and not self.view.vars["kfold ckbox"].get():
            messagebox.showerror('Value Error', 'You can not chose a scoring function involving Cross Validation if'
                                                ' K-Fold option is unchecked.')
            return False

        if not self.model.train_dataset_path:
            messagebox.showerror("Missing Value", "No dataset loaded.")
            return False
        else:
            if not os.path.isfile(self.model.train_dataset_path) or not os.path.exists(self.model.train_dataset_path):
                messagebox.showerror("Value error", "Invalid dataset path.")
                return False
        if not self.model.targets:
            messagebox.showerror("Missing value", "Targets are needed to train a Random Forest Classifier.")
            return False

        return True

    def _update_rfc_params(self, rfc_params):
        """
        Updates the RFC parameters in the model based on the provided values.

        Parameters
        ----------
        rfc_params : dict
            A dictionary of Random Forest Classifier parameters.

        Returns
        -------
        None
        """
        local_dict = {}
        for key, value in rfc_params.items():
            local_dict[key] = value.get()

        self.model.rfc_params_stringvar.update(local_dict)

    def _update_params(self, widgets: dict, ):
        """
        Updates the model parameters based on the values in the provided widgets.

        Parameters
        ----------
        widgets : dict
            A dictionary of widgets where the values need to be extracted and updated in the model.

        Returns
        -------
        None
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

    def _update_view_from_model(self, ):
        """
        Updates the view (UI) elements with the current model parameters.

        Returns
        -------
        None
        """
        for key, widget in self.view.vars.items():
            widget.set(self.model.vars[key])

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

    def _trace_target_column(self, *args):
        """
        Updates the target column combobox with the unique values from the selected column.

        Parameters
        ----------
        args : tuple
            Arguments passed from the view element.

        Returns
        -------
        None
        """
        values = list(set(list(self.model.train_dataset[self.view.vars["target column"].get()])))

        if len(values) <= 200:
            self.view.cbboxes['key target'].configure(values=values)
        else:
            messagebox.showerror('Too much values', 'The selected column has more than 200 different values.')

    def export(self, ):
        """
        Exports classification and advanced metrics as TXT files based on the metrics displayed in the textbox.

        Returns
        -------
        None
        """
        # filename = filedialog.asksaveasfilename(title="Save as",
        #                                         filetypes=(("Text", "*.txt"),))
        filename = ""
        text = self.view.textboxes["metrics"].get('1.0', tk.END)

        if not filename:
            if ".rfc" in self.view.vars["save rfc"].get():
                filename = self.view.vars["save rfc"].get().replace(".rfc", "_results.txt")
            else:
                filename = self.view.vars["save rfc"].get() + "_results.txt"

        with open(filename, 'w') as f:
            f.write(text)

        messagebox.showinfo("", f"Results saved under {filename}")

    def save_model(self, ):
        """
        Saves the model configuration and parameters to a specified file.

        Returns
        -------
        None
        """
        if self._check_params_validity():
            for widgets in [self.view.ckboxes, self.view.entries, self.view.cbboxes, self.view.sliders, self.view.vars,
                            self.view.switches, self.view.textboxes, self.view.labels, ]:
                self._update_params(widgets)
            self._update_rfc_params(self.view.rfc_params_stringvar)

            f = filedialog.asksaveasfilename(defaultextension=".lcfg",
                                             filetypes=[("Learning configuration", "*.lcfg"), ])
            if f:
                self.model.save_model(path=f, )

    def load_model(self, ):
        """
        Loads a saved model configuration and updates the view with the model parameters.

        Returns
        -------
        None
        """
        f = filedialog.askopenfilename(title="Open file", filetypes=(("Learning configuration", "*.lcfg"),))
        if f:
            if self.model.load_model(path=f):
                self.view.rfc_params_stringvar = self.reload_rfc_params(self.view.rfc_params_stringvar)
                self._update_view_from_model()

    def save_config(self, ):
        """
        Saves the current configuration and parameters to a specified file.

        Returns
        -------
        None
        """
        if self._check_params_validity():
            for widgets in [self.view.ckboxes, self.view.entries, self.view.cbboxes, self.view.sliders, self.view.vars,
                            self.view.switches, self.view.textboxes, ]:
                self._update_params(widgets)
            self._update_rfc_params(self.view.rfc_params_stringvar)

            f = filedialog.asksaveasfilename(defaultextension=".rfcfg",
                                             filetypes=[("Learning - Random forest", "*.rfcfg"), ])
            if f:
                self.model.save_model(path=f, )

    def load_config(self, ):
        """
        Loads a saved configuration and updates the view with the parameters.

        Returns
        -------
        None
        """
        f = filedialog.askopenfilename(title="Open file", filetypes=(("Learning - Random forest", "*.rfcfg"),))
        if f:
            if self.model.load_model(path=f):
                self._update_view_from_model()

    def split_dataset(self):
        """
        Splits the dataset into training and testing sets based on a specified ratio and saves them to new files.

        Returns
        -------
        None
        """
        ratio = self.view.vars["split dataset ratio"].get()
        path = self.view.vars["split dataset path"].get()

        if path:
            df = pd.read_csv(path)
            train_sets = []
            test_sets = []
            labels = list(set(list(df["label"])))
            for label in labels:
                dfl = df[df["label"] == label]
                dfl.reset_index(inplace=True, drop=True)
                y = dfl["label"]
                # y = self.label_encoding(y)
                X = dfl.loc[:, df.columns != "label"]
                X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=ratio)
                X_train["label"] = y_train
                X_test["label"] = y_test
                train_sets.append(X_train)
                test_sets.append(X_test)

            train_df = pd.concat(train_sets, ignore_index=True)
            train_df.reset_index(inplace=True, drop=True)
            test_df = pd.concat(test_sets, ignore_index=True)
            test_df.reset_index(inplace=True, drop=True)

            base_path = path.split(".")
            train_df.to_csv(base_path[0] + "_Xy_train." + base_path[1], index=False)
            test_df.to_csv(base_path[0] + "_Xy_test." + base_path[1], index=False)

            self.load_train_dataset(autoload=base_path[0] + "_Xy_train." + base_path[1])
            self.load_test_dataset(autoload=base_path[0] + "_Xy_test." + base_path[1])

            messagebox.showinfo("Splitting", "Splitting done")

    def trace_scoring(self, *args):
        """
        Updates the scoring method based on the selected option.

        Parameters
        ----------
        args : tuple
            Arguments passed from the view element.

        Returns
        -------
        None
        """
        self.scoring = self.view.vars["scoring"].get()

    def trace_kfold(self, *args):
        """
        Updates the k-fold cross-validation settings based on the selected option.

        Parameters
        ----------
        args : tuple
            Arguments passed from the view element.

        Returns
        -------
        None
        """
        self.model.kfold = self.view.vars["kfold"].get()
        self.model.enable_kfold = True if self.view.vars["kfold ckbox"].get() else False

    def trace_dataset(self, *args):
        """
        Updates the dataset path based on the selected option.

        Parameters
        ----------
        args : tuple
            Arguments passed from the view element.

        Returns
        -------
        None
        """
        self.model.full_dataset_path = self.view.vars["split dataset path"].get()

    def fill_hyperparameters_to_tune(self, frame):
        """
        Fills the UI with hyperparameters to tune and their possible values for the user to modify.

        Parameters
        ----------
        frame : tk.Frame
            The frame where the hyperparameter tuning elements will be added.

        Returns
        -------
        None
        """

        row_index = 0
        row_index_offset = 3
        params_to_tune_label = ctk.CTkLabel(master=frame, text="HYPERPARAMETERS TO TUNE", font=('', 14))
        possible_values_label = ctk.CTkLabel(master=frame, text="POSSIBLE VALUES (coma separated)", font=('', 14))
        general_params_separators_indices = [1, 2, ]

        for param, values in self.model.hyperparameters_to_tune.items():
            param_ckbox = ctk.CTkCheckBox(master=frame, text=param)
            value_entry = ctk.CTkEntry(master=frame, )
            value_entry.insert(0, values)

            param_ckbox.grid(row=row_index + row_index_offset, column=0, sticky='we')
            value_entry.grid(row=row_index + row_index_offset, column=2, sticky='we')

            general_params_separators_indices.append(row_index + row_index_offset + 1)

            self.view.entries[f"hyperparameter {param}"] = value_entry
            self.view.ckboxes[f"hyperparameter {param}"] = param_ckbox

            row_index += 2

        general_v_sep = Separator(master=frame, orient='v')
        general_v_sep.grid(row=row_index_offset, column=1, rowspan=row_index + 1, sticky='ns')

        params_to_tune_label.grid(row=0, column=0, )
        possible_values_label.grid(row=0, column=2, )

        for r in range(general_params_separators_indices[-1] + 2):
            if r in general_params_separators_indices:
                sep = Separator(master=frame, orient='h')
                sep.grid(row=r, column=0, columnspan=3, sticky='ew')
