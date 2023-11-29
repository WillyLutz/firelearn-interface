import json
from functools import partial

import customtkinter
import customtkinter as ctk
from PIL import Image

from scripts import params, params as p
from scripts.CONTROLLER.MainController import MainController
from scripts.VIEW.AnalysisView import AnalysisView
from scripts.VIEW.LearningView import LearningView
from scripts.VIEW.ProcessingView import ProcessingView

import pathlib
from scripts.params import  resource_path

class MainView(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(master=app)

        self.app = app
        self.app.geometry("1440x900")
        self.app.resizable(1, 1)
        # self.app.configure(height=720, width=1080)
        self.app.minsize(height=900, width=1440)

        self.master_frame = ctk.CTkFrame(master=self.app, )
        self.master_frame.place(relwidth=1.0, relheight=1.0)

        # ------------- TABS MENU ----------------------
        self.tabs_view = ctk.CTkTabview(master=self.master_frame, border_color='red', corner_radius=10)
        self.tabs_view.place(relwidth=1.0, relheight=1.0)
        self.tabs_view.add("Home")
        self.tabs_view.add("Processing")
        self.tabs_view.add("Learning")
        self.tabs_view.add("Analysis")

        # ------------- MANAGING PARENT TABS -----------
        self.manage_home_tab()

        # ------------- SETTING CONTROLLER -------------
        self.controller = MainController(self)
        self.learning_view = LearningView(app=self.app, master=self.tabs_view.tab("Learning"),
                                          parent_view=self)
        self.processing_view = ProcessingView(app=self.app, master=self.tabs_view.tab("Processing"),
                                              parent_view=self)
        self.analysis_view = AnalysisView(app=self.app, master=self.tabs_view.tab("Analysis"),
                                          parent_view=self)

        self.terminal = None

        self.theme = json.load(open(resource_path("data/theme.json")))

    def open_web(self, url):
        if self.controller:
            self.controller.open_web(url)

    def manage_home_tab(self):
        message = "FireLearn GUI (Graphical User Interface) is an independent software using 'fiiireflyyy', " \
                  "a third party python library developed by the same author. \n\n" \
                  "It aims to provide machine learning and deep learning solutions in a user-friendly manner for biologists." \
                  "This tool is especially made for an approach of artificial intelligence applied to biology data " \
                  "such as electrical recordings, or any kind of temporal data for instance. " \
                  "It provides several tools for processing, learning and " \
                  "analysis that can be used independently and on a variety of data within certain boundaries. \n\n" \
                  "Help is available for each section of the software by clicking the small '?' icons next to each section. " \
                  "FireLearn GUI is destined to be improved (bug tracking, more AI models, more analysis...). "
        bug_title_message = "There is a bug ? do you have a suggestion ?"
        bug_message = " You can help with the development of the project " \
                      "by reporting any issue or request using the 'issues' section of the github below, or by e-mail at " \
                      "'willy.lutz@irim.cnrs.fr' by specifying 'FireLearn GUI issue' (or suggestion) in the object." \
                      "\n\nFireLearn GUI has been developed by a third party and displays a basic MIT Licence."
        disclaimer_message = f"In development, for personal use only - LUTZ W. 2023\nv{params.version}"

        disclaimer_label = ctk.CTkLabel(self.tabs_view.tab("Home"), text=disclaimer_message)
        welcome_label = ctk.CTkLabel(self.tabs_view.tab("Home"), text=f"Welcome to FireLearn GUI",
                                     font=('', 18, 'bold'))
        welcome_message_label = ctk.CTkLabel(self.tabs_view.tab("Home"), text=message, font=('', 15), wraplength=500)
        bug_title_label = ctk.CTkLabel(self.tabs_view.tab("Home"), text=bug_title_message, font=('', 18, 'bold'))
        bug_label = ctk.CTkLabel(self.tabs_view.tab("Home"), text=bug_message, font=('', 15), wraplength=500)

        welcome_label.place(relx=0.16, rely=0.15, )
        welcome_message_label.place(relx=0.1, rely=0.2, )
        bug_title_label.place(relx=0.1, rely=0.6)
        bug_label.place(relx=0.1, rely=0.65)
        disclaimer_label.place(anchor=ctk.S, relwidth=1, rely=0.95, relx=0.5)

        fl_logo = ctk.CTkImage(dark_image=Image.open(resource_path("data/firelearn_img/logo firelearn light text.png")), size=(700, 500))
        fl_label = ctk.CTkLabel(master=self.tabs_view.tab("Home"), image=fl_logo, text="")
        fl_label.place(relx=0.5, rely=0.2, relwidth=0.5)

        github_image = customtkinter.CTkImage(dark_image=Image.open(resource_path("data/firelearn_img/github_logo.png")),
                                              size=(60, 60))
        github_button = ctk.CTkButton(master=self.tabs_view.tab("Home"), image=github_image, text="",
                                      width=70, height=70, corner_radius=10,
                                      command=partial(self.open_web,
                                                      "https://github.com/WillyLutz/firelearn-interface"))
        github_button.place(relx=0.1, rely=0.85)

    @staticmethod
    def update_slider_value(value, var):
        var.set(str(round(value, 2)))

    def select_color(self, view, selection_button_name):
        color_window = ctk.CTkToplevel()
        color_window.title("Color Selection")
        max_col = 8
        col = 0
        row = 0
        for c in p.COLORS:
            color_button = ctk.CTkButton(master=color_window, text=c, text_color="black",
                                         height=30, width=130, fg_color=c,
                                         )
            color_button.grid(row=row, column=col, padx=3, pady=3)
            color_button.configure(command=partial(self.chose_color, view=view, color_button=color_button,
                                                   selection_button_name=selection_button_name))

            if col >= max_col:
                col = 0
                row += 1
            else:
                col += 1

    @staticmethod
    def chose_color(view, color_button, selection_button_name):
        view.buttons[selection_button_name].configure(fg_color=color_button.cget('fg_color'))
        view.vars[selection_button_name].set(color_button.cget('text'))

    @staticmethod
    def deiconify_toplevel(toplevel: ctk.CTkToplevel):
        if toplevel.state() == 'withdrawn':
            toplevel.deiconify()


    def is_empty_or_int(self, widget, *args):
        try:
            value = widget.get()
            if value == "":
                return True
            int(value)
            self.change_entry_color(widget, self.theme["CTkEntry"]["text_color"])
            widget.set_error('')
            return True
        except ValueError:
            self.change_entry_color(widget, 'tomato')
            widget.set_error('Value must be integer or empty')
            return False

    def is_positive_int_or_emtpy(self, widget, *args):
        try:
            value = widget.get()
            if value == "":
                self.change_entry_color(widget, self.theme["CTkEntry"]["text_color"])
                widget.set_error('')
                return True

            if int(value) >= 0:
                self.change_entry_color(widget, self.theme["CTkEntry"]["text_color"])
                widget.set_error('')
                return True
        except ValueError:
            self.change_entry_color(widget, 'tomato')
            widget.set_error('Value must be positive integer or empty')
            return False

    def is_positive_int(self, widget, *args):
        try:
            value = widget.get()
            if int(value) >= 0:
                self.change_entry_color(widget, self.theme["CTkEntry"]["text_color"])
                widget.set_error('')
                return True
            else:
                self.change_entry_color(widget, 'tomato')
                widget.set_error('Value must be positive integer')
                return False
        except Exception:
            self.change_entry_color(widget, 'tomato')
            widget.set_error('Value must be positive integer')
            return False

    def has_forbidden_characters(self, widget, *args):
        forbidden_characters = "<>:\"|?*[]\\/§"
        found_forbidden = []
        value = widget.get()
        for fc in forbidden_characters:
            if fc in value:
                found_forbidden.append(fc)
        if found_forbidden:
            self.change_entry_color(widget, 'tomato')
            widget.set_error(f'Value can not contain forbidden characters {forbidden_characters}')
            return False
        else:
            self.change_entry_color(widget, self.theme["CTkEntry"]["text_color"])
            widget.set_error('')
            return True

    def is_valid_directory(self, widget, *args):
        value = widget.get()

        if pathlib.Path.exists(pathlib.Path(value)):
            self.change_entry_color(widget, self.theme["CTkEntry"]["text_color"])
            widget.set_error('')
            return True

        else:
            self.change_entry_color(widget, 'tomato')
            widget.set_error('Directory does not exist')
            return False

    def change_entry_color(self, widget, color, *args):
        widget.configure(text_color=color)




