import os
import pickle

import fiiireflyyy.firelearn
import numpy as np
import pandas as pd
import sklearn.preprocessing
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from VIEW.LearningView import LearningView
from MODEL.LearningModel import LearningModel
import customtkinter as ctk
from CONTROLLER import input_validation as ival
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from CONTROLLER.ProgressBar import ProgressBar
from MODEL.ClfTester import ClfTester


class LearningController:
    def __init__(self, main_controller, model: LearningModel, view: LearningView, ):
        self.model = model
        self.view = view
        self.main_controller = main_controller
        self.progress = None

    @staticmethod
    def reload_rfc_params(rfc_params_string_var):
        clf = RandomForestClassifier()
        for name, value in clf.get_params().items():
            rfc_params_string_var[name].set(value)

    def load_dataset(self):
        filename = self.main_controller.open_filedialog(mode='file')
        strvar = self.view.strvars["load dataset"]
        label_cbbox = self.view.cbboxes["target column"]
        if filename:
            strvar.set(filename)
            self.model.dataset_path = filename

            df = pd.read_csv(filename, index_col=False)
            label_cbbox.configure(state='normal')
            label_cbbox.configure(values=[str(c) for c in df.columns])
            label_cbbox.set(str(df.columns[0]))
            label_cbbox.configure(state='readonly')

    def add_subtract_target(self, mode='add'):

        if ival.widget_value_has_forbidden_character(self.view.entries["key target"]) is False:
            self.view.entries["key target"].delete(0, ctk.END)
            return False

        key = self.view.entries["key target"].get()

        targets = self.model.targets
        if mode == 'add':
            if key:
                targets.append(key)
            else:
                messagebox.showerror("Missing Value", "You need to indicate the key and the value to add a target.")
        elif mode == 'subtract':
            if key:
                try:
                    targets.remove(key)
                except KeyError:
                    pass
            else:
                messagebox.showerror("Missing Value", "You need to indicate at least the key to delete a target.")
        self.model.targets = targets

        self.main_controller.update_textbox(self.view.textboxes["targets"], self.model.targets)
        self.view.entries["key target"].delete(0, ctk.END)

    def savepath_rfc(self, strvar):
        filename = self.main_controller.open_filedialog(mode='saveas')
        if filename:
            strvar.set(filename)
            self.model.save_rfc_directory = filename

    def load_rfc(self, rfc_params_string_var, strvars):
        filename = self.main_controller.open_filedialog(mode="aimodel")
        if filename:
            clf = pickle.load(open(filename, "rb"))
            self.model.rfc = clf

            for name, value in clf.get_params().items():
                rfc_params_string_var[name].set(value)

            strvars["rfc path"].set(os.path.dirname(filename))
            strvars["rfc name"].set(os.path.basename(filename))
            strvars["rfc status"].set("True")

    def learning(self, entries, cbboxes, switches, rfc_params_string_var, strvars):
        if self.check_params_validity():
            self.update_params(entries)
            self.update_params(cbboxes)
            self.update_params(switches)

            self.progress = ProgressBar("Learning", self.view.app)
            self.progress.daemon = True
            self.progress.total_tasks = 1 + 1 + 2 * int(strvars["n iter"].get())
            self.progress.start()

            self.progress.update_task("Loading datatset")

            rfc_params = self.extract_rfc_params(rfc_params_string_var)

            df = pd.read_csv(self.model.dataset_path, index_col=False)

            self.progress.increment_progress(1)
            self.progress.update_task("Splitting")
            target_column = self.model.cbboxes["target column"]

            y = df[target_column]
            y = self.label_encoding(y)
            X = df.loc[:, df.columns != target_column]

            all_test_scores = []
            all_train_scores = []
            all_train_metrics = []
            all_test_metrics = []
            self.progress.increment_progress(1)

            if self.model.switches["load rfc"]:
                rfc = self.model.rfc
            else:
                rfc = RandomForestClassifier()
                rfc.set_params(**rfc_params)

            for iteration in range(int(entries["n iter"].get())):
                self.progress.update_task(f"Training iteration {iteration + 1}")
                clf_tester = ClfTester(rfc)
                if self.model.switches["load rfc"]:
                    clf_tester.trained = True

                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

                clf_tester.train(X_train, y_train)
                clf_tester.test(X_test, y_test)

                if not clf_tester.trained:
                    all_train_scores.append(clf_tester.train_acc)
                    all_train_metrics.append(clf_tester.train_metrics)
                all_test_scores.append(clf_tester.test_acc)
                all_test_metrics.append(clf_tester.test_metrics)

                self.progress.increment_progress(1)

                self.progress.update_task(f"Testing iteration {iteration + 1}")
                self.progress.increment_progress(1)

            # accuracies computation

            # self.main_controller.update_textbox(self.model.textboxes)

            metrics_elements = []
            metrics_elements = self.learning_display_computed_metrics(metrics_elements, entries,
                                                                      all_train_metrics,
                                                                      all_test_metrics, all_train_scores,
                                                                      all_test_scores)

            self.update_metrics_textbox(metrics_elements)
            if switches["save rfc"].get():
                self.main_controller.save_object(rfc, entries["save rfc"].get())  # todo : save rfc not functional

    @staticmethod
    def extract_rfc_params(rfc_params_string_var):
        rfc_params = {}
        for key, widget in rfc_params_string_var.items():
            if ival.isint(widget.get()):
                rfc_params[key] = int(widget.get())
            elif ival.isfloat(widget.get()):
                rfc_params[key] = float(widget.get())
            elif widget.get() == 'None':
                rfc_params[key] = None
            else:
                rfc_params[key] = widget.get()
        return rfc_params

    def learning_display_computed_metrics(self, metrics_elements, entries, all_train_metrics,
                                          all_test_metrics,
                                          all_train_scores, all_test_scores, ):

        metrics_elements.append("CLASSIFICATION METRICS")
        metrics_elements.append("---------------------------------------------------------------")
        metrics_elements.append("")

        pm = u"\u00B1"
        if self.model.rfc:  # ALREADY TRAINED
            metrics_elements.append(f"Number of training iterations: None (pre-trained classifier)")
        else:
            metrics_elements.append(f"Number of training iterations: {int(entries['n iter'].get())}", )
        metrics_elements.append(f"Number of testing iterations: {int(entries['n iter'].get())}", )

        if self.model.rfc:  # ALREADY TRAINED
            metrics_elements.append(f"Training accuracy: None (pre-trained classifier)")
        else:
            metrics_elements.append(
                f"Training accuracy: {str(np.mean(all_train_scores).round(3))} {pm} {str(np.std(all_train_scores).round(3))}", )
        metrics_elements.append(
            f"Testing accuracy: {str(np.mean(all_test_scores).round(3))} {pm} {str(np.std(all_test_scores).round(3))}")

        if self.model.switches["get metrics"]:

            metrics_elements.append("")
            metrics_elements.append("TRAINING------------------------")
            if not self.model.rfc:  # not pre-trained:
                for t in self.model.targets:
                    t_metrics = {t: [[], []]}  # {class1 : [[true probas],[false probas]] }

                    for train_metrics in all_train_metrics:
                        for target, target_metric in train_metrics.items():
                            if t == target:
                                t_metrics[t][0] = t_metrics[t][0] + target_metric[0]
                                t_metrics[t][1] = t_metrics[t][1] + target_metric[1]

                    true_preds = t_metrics[t][0]
                    false_preds = t_metrics[t][1]
                    if not true_preds:
                        true_preds.append(0)
                    if not false_preds:
                        false_preds.append(0)
                    metrics_elements.append("---")
                    metrics_elements.append(f"Target: {t}")
                    metrics_elements.append(f"Number of true predictions: {len(true_preds)}")
                    metrics_elements.append(f"Number of false predictions: {len(false_preds)}")
                    metrics_elements.append(
                        f"CUP for true predictions: {np.mean(true_preds).round(3)} {pm} {np.std(true_preds).round(3)}")
                    metrics_elements.append(
                        f"CUP for false predictions: {np.mean(false_preds).round(3)} {pm} {np.std(false_preds).round(3)}")
                    metrics_elements.append(f"")
            else:
                metrics_elements.append("No data available - Classifier were pre-trained.")

            metrics_elements.append("")
            metrics_elements.append("TESTING------------------------")
            for t in self.model.targets:
                t_metrics = {t: [[], []]}  # {class1 : [[true probas],[false probas]] }

                for test_metrics in all_test_metrics:
                    for target, target_metric in test_metrics.items():
                        if t == target:
                            t_metrics[t][0] = t_metrics[t][0] + target_metric[0]
                            t_metrics[t][1] = t_metrics[t][1] + target_metric[1]

                true_preds = t_metrics[t][0]
                false_preds = t_metrics[t][1]
                if not true_preds:
                    true_preds.append(0)
                if not false_preds:
                    false_preds.append(0)
                metrics_elements.append("---")
                metrics_elements.append(f"Target: {t}")
                metrics_elements.append(f"Number of true predictions: {len(true_preds)}")
                metrics_elements.append(f"Number of false predictions: {len(false_preds)}")
                metrics_elements.append(
                    f"CUP for true predictions: {np.mean(true_preds).round(3)} {pm} {np.std(true_preds).round(3)}")
                metrics_elements.append(
                    f"CUP for false predictions: {np.mean(false_preds).round(3)} {pm} {np.std(false_preds).round(3)}")
                metrics_elements.append(f"")
        else:
            metrics_elements.append("-------------")
            metrics_elements.append("No additional metrics computed.")

        return metrics_elements

    def update_metrics_textbox(self, elements):
        self.view.textboxes["metrics"].configure(state='normal')
        self.view.textboxes["metrics"].delete('1.0', tk.END)
        for elem in elements:
            elem = elem + "\n"
            self.view.textboxes["metrics"].insert(ctk.INSERT, elem)

        self.view.textboxes["metrics"].configure(state='disabled')

    def export(self, ):
        classification_metrics = pd.DataFrame(columns=["Phase", "Iterations", "Accuracy", "Std"])
        advanced_metrics = pd.DataFrame(columns=["Phase", "Target", "N true", "Mean CUP true", "Std CUP true",
                                                 "N false", "Mean CUP false", "Std CUP false"])

        filename = self.main_controller.open_filedialog(mode='saveascsv')
        text = self.view.textboxes["metrics"].get('1.0', tk.END)
        classification_text = text.split("TRAINING")[0]
        classification_lines = classification_text.split("\n")
        training_iter = classification_lines[3].split(":")[1].strip()
        testing_iter = classification_lines[4].split(":")[1].strip()
        training_acc = classification_lines[5].split(":")[1].split(" ")[0].strip()
        training_std = classification_lines[5].split(":")[1].split(" ")[2].strip()
        testing_acc = classification_lines[6].split(":")[1].split(" ")[0].strip()
        testing_std = classification_lines[6].split(":")[1].split(" ")[2].strip()
        classification_metrics.loc[len(classification_metrics)] = ["training", training_iter, training_acc,
                                                                   training_std]
        classification_metrics.loc[len(classification_metrics)] = ["testing", testing_iter, testing_acc, testing_std]

        classification_metrics.to_csv(filename.split(".csv")[0] + " general metrics.csv", index=False)

        training_metrics = text.split("TRAINING")[1].split("TESTING")[0]
        training_targets = training_metrics.split("Target:")
        for target_metric in training_targets[1:]:
            target_lines = target_metric.split("\n")
            phase = 'training'
            target = target_lines[0]
            n_true = target_lines[1].split(":")[1].strip()
            n_false = target_lines[2].split(":")[1].strip()
            cup_true = target_lines[3].split(":")[1].strip().split(" ")[0].strip()
            cup_true_std = target_lines[3].split(":")[1].strip().split(" ")[2].strip()
            cup_false = target_lines[4].split(":")[1].strip().split(" ")[0].strip()
            cup_false_std = target_lines[4].split(":")[1].strip().split(" ")[2].strip()

            advanced_metrics.loc[len(advanced_metrics)] = [phase, target, n_true, cup_true, cup_true_std,
                                                           n_false, cup_false, cup_false_std]

        testing_metrics = text.split("TESTING")[1]
        testing_targets = testing_metrics.split("Target:")
        for target_metric in testing_targets[1:]:
            target_lines = target_metric.split("\n")
            phase = 'testing'
            target = target_lines[0]
            n_true = target_lines[1].split(":")[1].strip()
            n_false = target_lines[2].split(":")[1].strip()
            cup_true = target_lines[3].split(":")[1].strip().split(" ")[0].strip()
            cup_true_std = target_lines[3].split(":")[1].strip().split(" ")[2].strip()
            cup_false = target_lines[4].split(":")[1].strip().split(" ")[0].strip()
            cup_false_std = target_lines[4].split(":")[1].strip().split(" ")[2].strip()

            advanced_metrics.loc[len(advanced_metrics)] = [phase, target, n_true, cup_true, cup_true_std,
                                                           n_false, cup_false, cup_false_std]

        advanced_metrics.to_csv(filename.split(".csv")[0] + " advanced metrics.csv", index=False)

    @staticmethod
    def label_encoding(y):
        labels = list(set(list(y)))
        corr = {}
        for lab in range(len(labels)):
            corr[labels[lab]] = lab

        for key, value in corr.items():
            y.replace(key, value)

        return y

    def check_params_validity(self, ):
        if self.view.switches["load rfc"].get() and not self.model.rfc:
            messagebox.showerror("X Doubt", "Invalid Loaded classifier")
            return False
        if self.view.switches["save rfc"].get():
            if not os.path.exists(os.path.dirname(self.view.entries["save rfc"].get())):
                messagebox.showerror("Value error", "Path to save the classifier does not exist.")
                return False
            if not os.path.isfile(os.path.isfile(self.view.entries["save rfc"].get())):
                messagebox.showerror("Value error", "Path to save the classifier is not valid.")
                return False

        if not ival.widget_value_is_positive_int_or_empty(self.view.entries["n iter"]) or \
                int(self.view.entries["n iter"].get()) == 0:
            messagebox.showerror("Value error", "Value for Train / test iterations needs to be a positive integer"
                                                " and superior to zero.")
            return False
        if not self.model.dataset_path:
            messagebox.showerror("Missing Value", "No dataset loaded.")
            return False
        else:
            if not os.path.isfile(self.model.dataset_path) or not os.path.exists(self.model.dataset_path):
                messagebox.showerror("Value error", "Invalid dataset path.")
                return False
        if not self.model.targets:
            messagebox.showerror("Missing value", "Targets are needed to train a Random Forest Classifier.")
            return False
        return True

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

    def save_model(self, ):
        if self.check_params_validity():
            self.update_params(self.view.entries)
            self.update_params(self.view.cbboxes)
            self.update_params(self.view.switches)
            self.update_params(self.view.textboxes)

            f = filedialog.asksaveasfilename(defaultextension=".lcfg",
                                             filetypes=[("Learning configuration", "*.lcfg"), ])
            if f:
                self.model.save_model(path=f, )

    def load_model(self, ):
        f = filedialog.askopenfilename(title="Open file", filetypes=(("Learning configuration", "*.lcfg"),))
        if f:
            if self.model.load_model(path=f):
                self.reload_rfc_params(self.view.rfc_params_stringvar)
                self.update_view_from_model()

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

        for key, widget in self.view.textboxes.items():
            self.main_controller.update_textbox(widget, self.model.textboxes[key].split("\n"))
