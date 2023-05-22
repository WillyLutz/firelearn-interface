import tkinter as tk
from tkinter import filedialog as fd, messagebox

import pandastable

from VIEW.MainView import MainView
from MODEL.MainModel import MainModel
import pandas as pd
from pandastable import Table, TableModel
import data.params as p
import io
import webbrowser
import VIEW.graphic_params as gp
import customtkinter as ctk
from tkinter import filedialog


class Controller:
    def __init__(self, model: MainModel, view: MainView):
        self.view = view
        self.model = model

    def open_web(self, url):
        webbrowser.open(url, new=1)

    def category_enabling_switch(self, switch, parent_widget):
        children = parent_widget.winfo_children()
        if switch.get() == 1:
            for child in children:
                if type(child) == ctk.CTkLabel:
                    child.configure(text_color=gp.enabled_label_color)
                elif type(child) == ctk.CTkEntry:
                    child.configure(state="normal")
                elif type(child) == ctk.CTkButton:
                    child.configure(state="normal")
                elif type(child) == ctk.CTkOptionMenu:
                    child.configure(state="normal")
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
                elif type(child) == ctk.CTkOptionMenu:
                    child.configure(state="disabled")
                elif type(child) == ctk.CTkSwitch and child != switch:
                    child.configure(state="disabled")

    def select_parent_directory(self, display_in):
        dirname = self.open_filedialog(mode='directory')
        if type(display_in) == ctk.StringVar:
            display_in.set(dirname)
            self.model.parent_directory = dirname

    def add_subtract_to_include_for_processing(self, entry, textbox, mode='add'):
        to_include = entry.get()
        local_include = self.model.to_include
        if mode == 'add':
            local_include.append(to_include)
        elif mode == 'subtract':
            local_include = [x for x in self.model.to_include if x != to_include]
        self.model.to_include = local_include
        self.update_textbox(textbox, self.model.to_include)
        entry.delete(0, ctk.END)

    def add_subtract_to_exclude_for_processing(self, entry, textbox, mode='add'):
        to_exclude = entry.get()
        local_exclude = self.model.to_exclude
        if mode == 'add':
            local_exclude.append(to_exclude)
        elif mode == 'subtract':
            local_exclude = [x for x in self.model.to_exclude if x != to_exclude]
        self.model.to_exclude = local_exclude
        self.update_textbox(textbox, self.model.to_exclude)
        entry.delete(0, ctk.END)


    def update_textbox(self, textbox, elements):
        textbox.configure(state="normal")
        textbox.delete(1.0, ctk.END)
        for elem in elements:
            elem = elem+"\n"
            textbox.insert(ctk.INSERT, elem)
        textbox.configure(state="disabled")

    def open_filedialog(self, mode='file'):
        if mode == 'file':
            filename = filedialog.askopenfilename(title="Open file",
                                              filetypes=(("Text files", "*.txt"), ("CSV files", "*.csv"),
                                                         ("Excel files", "*.xls *.xlsx")))
            return filename
        elif mode == 'directory':
            dirname = filedialog.askdirectory(mustexist=True, title="select directory")

            return dirname




    def add_keyword_filename(self, switch, entry):
        if type(entry) == ctk.CTkEntry:
            if switch.get() == 1:
                entry.configure(state="normal")
            else:
                entry.configure(state="disabled")
