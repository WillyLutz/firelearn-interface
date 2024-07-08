import pickle
from functools import partial

import seaborn as sns

import pandas as pd
from matplotlib import pyplot as plt

from scripts.MODEL.ConfusionModel import ConfusionModel
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from scripts import params as p

import fiiireflyyy.learn as fl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
            i, j = 0, 0
            for t in range(len(training_classes)):
                target_radio = ctk.CTkRadioButton(master=self.view.scrollable_frames["training"],
                                                  text=training_classes[t],
                                                  state='disabled', text_color_disabled='white'
                                                  )
                target_radio.select()
                target_radio.grid(row=i, column=j, padx=10, pady=10)
                j += 1
                if j > 2:
                    j = 0
                    i += 1
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
                i, j = 0, 0
                for t in range(len(training_classes)):
                    target_radio = ctk.CTkRadioButton(master=self.view.scrollable_frames["training"],
                                                      text=training_classes[t],
                                                      state='disabled', text_color_disabled='white'
                                                      )
                    target_radio.select()
                    target_radio.grid(row=i, column=j, padx=10, pady=10)
                    j += 1
                    if j > 2:
                        j = 0
                        i += 1

    def draw_figure(self, ):
        if self.input_validation():
            plt.close()
            training_classes = tuple(list(set(list(self.model.clf.classes_))))
            all_testing_classes = {key: value for (key, value) in self.view.vars.items() if "test label " in key}

            checked_classes = {key: value for (key, value) in all_testing_classes.items() if value.get() == 1}
            checked_classes_names = {self.view.checkboxes[key].cget('text'): value for (key, value) in
                                     checked_classes.items()}.keys()
            testing_classes = tuple(checked_classes_names)

            self.model.training_classes = training_classes
            self.model.testing_classes = testing_classes

            df = self.model.dataset
            df = df[df[self.view.vars["label column"].get()].isin(testing_classes)]

            overall_matrix, mixed_labels_matrix, TRAIN_CORRESPONDENCE, TEST_CORRESPONDENCE \
                = fl.test_clf_by_confusion(self.model.clf, df, training_targets=training_classes,
                                           testing_targets=testing_classes, show=False,
                                           iterations=self.view.vars["iterations"].get(),
                                           return_data=True,
                                           mode='percent')  # todo : update fiiireflyyy
            self.model.confusion_data["overall matrix"] = overall_matrix
            self.model.confusion_data["mixed labels matrix"] = mixed_labels_matrix
            self.model.confusion_data["train correspondence"] = TRAIN_CORRESPONDENCE
            self.model.confusion_data["test correspondence"] = TEST_CORRESPONDENCE

            self.update_figure()

    def update_figure(self):
        plt.close()
        overall_matrix = self.model.confusion_data["overall matrix"]
        mixed_labels_matrix = self.model.confusion_data["mixed labels matrix"]
        TRAIN_CORRESPONDENCE = self.model.confusion_data["train correspondence"]
        TEST_CORRESPONDENCE = self.model.confusion_data["test correspondence"]

        # plot
        fig, ax = plt.subplots(figsize=(p.DEFAULT_FIGUREWIDTH, p.DEFAULT_FIGUREHEIGHT))
        # self.view.canvas["confusion"] = FigureCanvasTkAgg(fig, master=self.view.frames["plot frame"])
        # self.view.canvas["confusion"].get_tk_widget().place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.96)
        # self.view.figures["confusion"] = (fig, ax)

        sns.heatmap(ax=ax, data=overall_matrix, annot=mixed_labels_matrix, annot_kws={"font": self.model.plot_axes["axes font"],
                                                                 "size": self.model.plot_axes["y ticks size"]}, fmt='', cmap="Blues",
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

        ax.set_xticks([TEST_CORRESPONDENCE[x] + 0.5 for x in self.model.testing_classes], self.model.testing_classes, fontsize=self.model.plot_axes["x ticks size"])
        ax.set_yticks([TRAIN_CORRESPONDENCE[x] + 0.5 for x in self.model.training_classes], self.model.training_classes, fontsize = self.model.plot_axes["y ticks size"])

        plt.tight_layout()
        plt.show()
        # self.view.figures["confusion"] = (fig, ax)
        # self.view.canvas["confusion"].draw()

        # self.view.buttons["save figure"].configure(command=partial(self.save_figure, self.view.figures["confusion"][0]))

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
                del self.view.checkboxes[key]
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
                    del self.view.checkboxes[key]
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
        checkboxes = {key: value for (key, value) in self.view.vars.items() if "test label" in key}
        for key, widget in checkboxes.items():
            widget.set(0)

    def select_all_test_targets(self):
        checkboxes = {key: value for (key, value) in self.view.vars.items() if "test label" in key}
        for key, widget in checkboxes.items():
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

                i, j = 0, 0
                for t in range(len(possible_targets)):
                    target_var = tk.IntVar(value=1)
                    target_checkbox = ctk.CTkCheckBox(master=self.view.scrollable_frames["testing"],
                                                      variable=target_var,
                                                      text=possible_targets[t])
                    target_checkbox.grid(row=i, column=j, padx=10, pady=10)
                    self.view.vars[f"test label {t}"] = target_var
                    self.view.checkboxes[f"test label {t}"] = target_checkbox
                    self.model.plot_data[f"test label {t}"] = target_var.get()
                    target_var.trace("w", partial(self.trace_vars_to_model, f"test label {t}"))
                    j += 1
                    if j > 2:
                        j = 0
                        i += 1

    def trace_vars_to_model(self, key, *args):
        if key in self.model.plot_general_settings.keys():
            self.model.plot_general_settings[key] = self.view.vars[key].get()
        elif key in self.model.plot_axes.keys():
            self.model.plot_axes[key] = self.view.vars[key].get()
        elif key in self.model.plot_legend.keys():
            self.model.plot_legend[key] = self.view.vars[key].get()

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
            checked_classes_names = {self.view.checkboxes[key].cget('text'): value for (key, value) in
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
