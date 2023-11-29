import pickle
import tkinter as tk
import webbrowser
from tkinter import ttk

import customtkinter as ctk

import scripts.VIEW.graphic_params as gp
from scripts.MODEL.MainModel import MainModel


class MainController:
    def __init__(self, view):
        self.view = view
        self.model = MainModel()  # set model
        self.view.controller = self  # set controller to view

        # self.view.analysis_view.set_controller(self.analysis_controller)

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
    def modulate_entry_state_by_switch(switch, entry):
        if type(entry) == ctk.CTkEntry:
            if switch.get() == 1:
                entry.configure(state="normal")
            else:
                entry.configure(state="disabled")

    @staticmethod
    def generate_harmonics(freq, nth, mode):
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
