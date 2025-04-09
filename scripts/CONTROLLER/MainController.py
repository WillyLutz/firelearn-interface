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
        """
        Opens a given URL in the default web browser.

        Parameters
        ----------
        url : str
            The URL to open.

        Returns
        -------
        None
        """
        webbrowser.open(url, new=1)

    @staticmethod
    def save_object(obj, path):
        """
        Saves a Python object to a file using pickle serialization.

        Parameters
        ----------
        obj : object
            The object to be saved.
        path : str
            The file path where the object should be saved.

        Returns
        -------
        None
        """
        file = open(f'{path}', 'wb')
        pickle.dump(obj, file)
        file.close()

    @staticmethod
    def update_textbox(textbox, elements):
        """
        Updates a textbox widget with a list or dictionary of elements.
        
        Parameters
        ----------
        textbox : ctk.CTkTextbox
            The textbox widget to update.
        elements : list or dict
            The content to insert into the textbox. If a list, each element is added as a new line.
            If a dictionary, keys and values are formatted as "key - value".
        
        Returns
        -------
        None
        """
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
        """
        Enables or disables an entry field based on the state of a switch.

        Parameters
        ----------
        switch : ctk.CTkSwitch
            The switch controlling the state of the entry field.
        entry : ctk.CTkEntry
            The entry field whose state is being modified.

        Returns
        -------
        None
        """
        if type(entry) == ctk.CTkEntry:
            if switch.get() == 1:
                entry.configure(state="normal")
            else:
                entry.configure(state="disabled")

    @staticmethod
    def generate_harmonics(freq, nth, mode):
        """
        Generates a list of harmonic frequencies based on the given frequency, count, and mode.

        Parameters
        ----------
        freq : float
            The base frequency.
        nth : int
            The number of harmonics to generate.
        mode : str
            The mode of harmonics to generate. Options:
            - "All": Generates all harmonics.
            - "Even": Generates even harmonics only.
            - "Odd": Generates odd harmonics only.

        Returns
        -------
        list
            A list of harmonic frequencies.
        """
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
