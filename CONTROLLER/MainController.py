import os.path
import pickle
import random
import string
import time
import tkinter.filedialog
import webbrowser
from tkinter import filedialog
from tkinter import messagebox

import customtkinter as ctk
import fiiireflyyy.firefiles as ff
import fiiireflyyy.fireprocess as fp
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

import CONTROLLER.data_processing as dpr
import VIEW.graphic_params as gp
from CONTROLLER.ProgressBar import ProgressBar
from MODEL.MainModel import MainModel
from VIEW.MainView import MainView

import CONTROLLER.input_validation as ival

from data import params
import tkinter as tk
from tkinter import ttk

from CONTROLLER.ProcessingController import ProcessingController
from CONTROLLER.LearningController import LearningController


class MainController:
    def __init__(self, model: MainModel, view: MainView):
        self.view = view
        self.model = model
        self.processing_controller = ProcessingController(self, self.model.processing_model, self.view)
        self.learning_controller = LearningController(self, self.model.learning_model, self.view)

    # --------- STATIC METHODS ----------------
    @staticmethod
    def open_web(url):
        webbrowser.open(url, new=1)

    @staticmethod
    def save_object(obj, path):
        file = open(f'{path}', 'wb')
        pickle.dump(obj, file)
        file.close()

    @staticmethod
    def category_enabling_switch(switch, parent_widget):
        children = parent_widget.winfo_children()
        if switch.get() == 1:
            for child in children:
                if type(child) == ctk.CTkLabel:
                    child.configure(text_color=gp.enabled_label_color)
                elif type(child) == ctk.CTkEntry:
                    child.configure(state="normal")
                elif type(child) == ctk.CTkButton:
                    child.configure(state="normal")
                elif type(child) == tk.ttk.Combobox:
                    child.configure(state="readonly")
                elif type(child) == ctk.CTkSwitch and child != switch:
                    child.configure(state="normal")
        else:
            for child in children:
                if type(child) == ctk.CTkLabel:
                    child.configure(text_color=gp.disabled_label_color)
                elif type(child) == ctk.CTkEntry:
                    child.configure(state="disabled")
                elif type(child) == ctk.CTkButton:
                    child.configure(state="disabled")
                elif type(child) == tk.ttk.Combobox:
                    child.configure(state="disabled")
                elif type(child) == ctk.CTkSwitch and child != switch:
                    child.configure(state="disabled")

    @staticmethod
    def update_textbox(textbox, elements):
        textbox.configure(state="normal")
        textbox.delete(1.0, ctk.END)
        if type(elements) == list:
            for elem in elements:
                elem = elem + "\n"
                textbox.insert(ctk.INSERT, elem)
        elif type(elements) == dict:
            for key in elements:
                elem = key + " - " + elements[key] + "\n"
                textbox.insert(ctk.INSERT, elem)
        textbox.configure(state="disabled")

    @staticmethod
    def open_filedialog(mode='file'):
        if mode == 'file':
            filename = filedialog.askopenfilename(title="Open file",
                                                  filetypes=(("Tables", "*.txt *.xls *.xlsx *.csv"),))
            return filename
        elif mode == 'directory':
            dirname = filedialog.askdirectory(mustexist=True, title="select directory")
            return dirname
        elif mode == 'saveas':
            filename = filedialog.asksaveasfilename(title="Save as",
                                                    filetypes=(("Random Forest Classifier", "*.rfc"),))
            return filename
        elif mode == 'aimodel':
            filename = filedialog.askopenfilename(title="Open file",
                                                  filetypes=(("AI model", "*.rfc"),))
            return filename

    @staticmethod
    def modulate_entry_state_by_switch(switch, entry):
        if type(entry) == ctk.CTkEntry:
            if switch.get() == 1:
                entry.configure(state="normal")
            else:
                entry.configure(state="disabled")

    @staticmethod
    def generate_harmonics(freq, nth, mode):  # todo : to firesignal ?
        harmonics = []
        step = freq
        if mode == 'All':
            for i in range(nth):
                harmonics.append(freq)
                freq = freq + step
        if mode == "Even":
            for i in range(nth):
                if i % 2 == 0:
                    harmonics.append(freq)
                    freq = freq + step
        if mode == "Odd":
            for i in range(nth):
                if i % 2 == 1:
                    harmonics.append(freq)
                    freq = freq + step
        return harmonics



    def learning_reload_rfc_params(self, rfc_params_string_var):
        if self.learning_controller:
            self.learning_controller.reload_rfc_params(rfc_params_string_var)

    def learning_load_dataset(self, strvar, label_cbox):
        if self.learning_controller:
            self.learning_controller.load_dataset(strvar, label_cbox)

    def learning_savepath_rfc(self, strvar):
        if self.learning_controller:
            self.learning_controller.savepath_rfc(strvar)

    def learning_load_rfc(self, rfc_params_string_var, learning_strvars):
        if self.learning_controller:
            self.learning_controller.load_rfc(rfc_params_string_var, learning_strvars)

    def learning(self, entries, cboxes, rfc_params_string_var, learning_strvars):
        if self.learning_controller:
            self.learning_controller.learning(entries, cboxes, rfc_params_string_var, learning_strvars)

    def label_encoding(self, y):
        if self.learning_controller:
            self.learning_controller.label_encoding(y)

    def check_learning_params_validity(self, entries, cboxes):
        if self.learning_controller:
            self.learning_controller.check_learning_params_validity(entries, cboxes)

    def update_learning_params(self, widgets: dict, ):
        if self.learning_controller:
            self.learning_controller.update_learning_params(widgets)
