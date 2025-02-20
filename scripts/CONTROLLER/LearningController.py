import os
import pickle
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import customtkinter as ctk
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score

from scripts.CONTROLLER import input_validation as ival
from scripts.CONTROLLER.ProgressBar import ProgressBar
from scripts.MODEL.ClfTester import ClfTester
from scripts.MODEL.LearningModel import LearningModel
from scripts.CONTROLLER.MainController import MainController
from scripts.WIDGETS.ErrEntry import ErrEntry


class LearningController:
    def __init__(self, view,):
        self.model = LearningModel()
        self.view = view
        self.view.controller = self  # set controller

        self.progress = None

    @staticmethod
    def reload_rfc_params(rfc_params_string_var):
        clf = RandomForestClassifier()
        for name, value in clf.get_params().items():
            rfc_params_string_var[name].set(value)

    def load_train_dataset(self):
        filename = filedialog.askopenfilename(title="Open file",
                                              filetypes=(("Tables", "*.txt *.xls *.xlsx *.csv"),))
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

            self.view.vars['target column'].trace('w', self.trace_target_column)
            
    def load_test_dataset(self):
        filename = filedialog.askopenfilename(title="Open file",
                                              filetypes=(("Tables", "*.txt *.xls *.xlsx *.csv"),))
        strvar = self.view.vars["load test dataset"]
        if filename:
            strvar.set(filename)
            self.model.test_dataset_path = filename
            df = pd.read_csv(filename, index_col=False)
            self.model.test_dataset = df


    def add_subtract_target(self, mode='add'):

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

    def savepath_rfc(self, strvar):
        filename = filedialog.asksaveasfilename(title="Save as",
                                                filetypes=(("Random Forest Classifier", "*.rfc"),))
        if filename:
            strvar.set(filename)
            self.model.save_rfc_directory = filename

    def load_rfc(self, rfc_params_string_var, strvars):
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

    def learning(self, ):
        if self.check_params_validity():
            for widgets in [self.view.ckboxes, self.view.entries, self.view.cbboxes, self.view.sliders, self.view.vars,
                            self.view.switches, self.view.textboxes, ]:
                self.update_params(widgets)
            self.update_rfc_params(self.view.rfc_params_stringvar)

            self.progress = ProgressBar("Learning", self.view.app)
            self.progress.daemon = True
            self.progress.total_tasks = 1 + 1 + 2 * int(self.view.vars["n iter"].get())
            self.progress.start()

            self.progress.update_task("Loading datatset")

            rfc_params = self.extract_rfc_params(self.view.rfc_params_stringvar)
            
            full_df = pd.read_csv(self.model.full_dataset_path, index_col=False)
            train_df = pd.read_csv(self.model.train_dataset_path, index_col=False)
            test_df = pd.read_csv(self.model.test_dataset_path, index_col=False)


            self.progress.increment_progress(1)
            self.progress.update_task("Splitting")
            target_column = self.model.cbboxes["target column"]
            
            full_df = full_df[full_df[target_column].isin(self.model.targets)]
            full_df.reset_index(inplace=True, drop=True)
            y_full = full_df[target_column]
            y_full = self.label_encoding(y_full)
            X_full = full_df.loc[:, full_df.columns != target_column]

            train_df = train_df[train_df[target_column].isin(self.model.targets)]
            train_df.reset_index(inplace=True, drop=True)
            y_train = train_df[target_column]
            y_train = self.label_encoding(y_train)
            X_train = train_df.loc[:, train_df.columns != target_column]

            test_df = test_df[test_df[target_column].isin(self.model.targets)]
            test_df.reset_index(inplace=True, drop=True)
            y_test = test_df[target_column]
            y_test = self.label_encoding(y_test)
            X_test = test_df.loc[:, test_df.columns != target_column]


            all_test_scores = []
            all_train_scores = []
            all_train_metrics = []
            all_test_metrics = []
            self.progress.increment_progress(1)

            rfc = RandomForestClassifier()
            rfc.set_params(**rfc_params)
            all_cv_scores = []
            for iteration in range(int(self.view.entries["n iter"].get())):
                self.progress.update_task(f"Training iteration {iteration + 1}")
                clf_tester = ClfTester(rfc)

                clf_tester.train(X_train, y_train)
                clf_tester.test(X_test, y_test)

                if not clf_tester.trained:
                    all_train_scores.append(clf_tester.train_acc)
                    all_train_metrics.append(clf_tester.train_metrics)
                all_test_scores.append(clf_tester.test_acc)
                all_test_metrics.append(clf_tester.test_metrics)

                self.progress.increment_progress(1)
                # kfold
                if self.model.enable_kfold:
                    cv_scores = cross_val_score(clf_tester.clf, X_full, y_full, cv=int(self.model.kfold))
                    all_cv_scores.append(cv_scores)
                
                self.progress.update_task(f"Testing iteration {iteration + 1}")
                self.progress.increment_progress(1)

            

            # MainController.update_textbox(self.model.textboxes)

            metrics_elements = []
            metrics_elements = self.learning_display_computed_metrics(metrics_elements, self.view.entries,
                                                                      all_train_metrics,
                                                                      all_test_metrics, all_train_scores,
                                                                      all_test_scores, all_cv_scores)

            self.update_metrics_textbox(metrics_elements)
            if self.view.vars["save rfc"].get():
                MainController.save_object(rfc, self.view.vars["save rfc"].get())

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
                                          all_train_scores, all_test_scores, all_cv_scores):

        metrics_elements.append("CLASSIFICATION METRICS")
        metrics_elements.append("---------------------------------------------------------------")
        metrics_elements.append("")

        pm = u"\u00B1"
        metrics_elements.append(f"Number of training iterations: {int(entries['n iter'].get())}", )
        metrics_elements.append(f"Number of testing iterations: {int(entries['n iter'].get())}", )

        mean_accuracy = np.mean(all_train_scores).round(3)
        metrics_elements.append(
                f"Training accuracy: {str(mean_accuracy)} {pm} {str(np.std(all_train_scores).round(3))}", )
        metrics_elements.append(
            f"Testing accuracy: {str(np.mean(all_test_scores).round(3))} {pm} {str(np.std(all_test_scores).round(3))}")

        if self.model.enable_kfold:
            mean_kfold = round(np.array(all_cv_scores).mean(), 3)
            std_kfold = round(np.array(all_cv_scores).std(), 3)
            kfold_acc_diff = round(mean_accuracy - mean_kfold, 3)
            kfold_acc_relative_diff = round(kfold_acc_diff / mean_accuracy * 100, 2)
            metrics_elements.append(f"{len(all_cv_scores[0])}-fold Cross Validation: {str(mean_kfold)} {pm} {str(std_kfold)}")
            metrics_elements.append(f"KFold-Accuracy difference = {mean_accuracy}-{mean_kfold} = {kfold_acc_diff}\n")
            metrics_elements.append(f"KFold-Accuracy relative difference: {kfold_acc_relative_diff} %\n")
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

        filename = filedialog.asksaveasfilename(title="Save as",
                                                filetypes=(("Coma Separated Value", "*.csv"),))
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

        advanced_metrics.to_csv(filename.split(".csv")[0], index=False)

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
        if not os.path.exists(os.path.dirname(self.view.entries["save rfc"].get())):
            messagebox.showerror("Value error", "Path to save the classifier does not exist.")
            return False


        if not ival.widget_value_is_positive_int_or_empty(self.view.entries["n iter"]) or \
                int(self.view.entries["n iter"].get()) == 0:
            messagebox.showerror("Value error", "Value for Train / test iterations needs to be a positive integer"
                                                " and superior to zero.")
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
    
    def update_rfc_params(self, rfc_params):
        local_dict = {}
        for key, value in rfc_params.items():
            local_dict[key] = value.get()
            
        self.model.rfc_params_stringvar.update(local_dict)
    
    def update_params(self, widgets: dict, ):
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

    def save_model(self, ):
        if self.check_params_validity():
            for widgets in [self.view.ckboxes, self.view.entries, self.view.cbboxes, self.view.sliders, self.view.vars,
                            self.view.switches, self.view.textboxes, self.view.labels, ]:
                self.update_params(widgets)
            self.update_rfc_params(self.view.rfc_params_stringvar)

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
    
    def save_config(self, ):
        if self.check_params_validity():
            for widgets in [self.view.ckboxes, self.view.entries, self.view.cbboxes, self.view.sliders, self.view.vars,
                            self.view.switches, self.view.textboxes, ]:
                self.update_params(widgets)
            self.update_rfc_params(self.view.rfc_params_stringvar)

            f = filedialog.asksaveasfilename(defaultextension=".rfcfg",
                                             filetypes=[("Learning - Random forest", "*.rfcfg"), ])
            if f:
                self.model.save_model(path=f, )

    def load_config(self, ):
        f = filedialog.askopenfilename(title="Open file", filetypes=(("Learning - Random forest", "*.rfcfg"),))
        if f:
            if self.model.load_model(path=f):
                self.update_view_from_model()

    def trace_target_column(self, *args):
        values = list(set(list(self.model.train_dataset[self.view.vars["target column"].get()])))

        if len(values) <= 200:
            self.view.cbboxes['key target'].configure(values=values)
        else:
            messagebox.showerror('Too much values', 'The selected column has more than 200 different values.')

    def split_dataset(self):
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
            train_df.to_csv(base_path[0]+"_Xy_train." + base_path[1], index=False)
            test_df.to_csv(base_path[0] + "_Xy_test." + base_path[1], index=False)

            messagebox.showinfo("Splitting", "Splitting done")

    def trace_kfold(self, *args):
        self.model.kfold = self.view.vars["kfold"].get()
        self.model.enable_kfold = True if self.view.vars["kfold ckbox"].get() else False
        
    def trace_dataset(self, *args):
        self.model.full_dataset_path = self.view.vars["split dataset path"].get()