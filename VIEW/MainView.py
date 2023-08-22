import tkinter as tk
from functools import partial

import customtkinter
import customtkinter as ctk
from PIL import Image

import params
from CONTROLLER.MainController import MainController
from VIEW.AnalysisView import AnalysisView
from VIEW.LearningView import LearningView
from VIEW.ProcessingView import ProcessingView

import params as p


class MainView(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(master=app)

        self.app = app
        self.app.geometry("1920x1080")
        self.app.resizable(1, 1)
        #self.app.configure(height=720, width=1080)
        self.app.minsize(height=900, width=1440)

        self.master_frame = ctk.CTkFrame(master=self.app, )
        self.master_frame.place(relwidth=1.0, relheight=1.0)

        # ------------ MENU BAR ------------------------
        self.menu_bar = tk.Menu()
        self.file_menu = tk.Menu(self.menu_bar)
        self.file_menu.add_command(label="Save software state", command='')
        self.file_menu.add_command(label="Load software state", command='')
        self.file_menu.add_command(label="Exit", command=self.quit)

        self.help_menu = tk.Menu(self.menu_bar)
        self.help_menu.add_command(label="Getting Started", command='')
        self.help_menu.add_command(label="Help ?", command='')
        self.help_menu.add_command(label="About", command='')

        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)

        self.app.config(menu=self.menu_bar)

        # ------------- TABS MENU ----------------------
        self.tabs_view = ctk.CTkTabview(master=self.master_frame, border_color='red', corner_radius=10)
        self.tabs_view.place(relwidth=1.0, relheight=1.0)
        self.tabs_view.add("Home")
        self.tabs_view.add("Processing")
        self.tabs_view.add("Learning")
        self.tabs_view.add("Analysis")

        self.tabs_view.add("Terminal")

        # ------------- MANAGING PARENT TABS -----------
        self.manage_home_tab()
        self.manage_terminal_tab()

        # ------------- SETTING CONTROLLER -------------
        self.controller = MainController(self)
        self.learning_view = LearningView(app=self.app, master=self.tabs_view.tab("Learning"),
                                          parent_view=self)
        self.processing_view = ProcessingView(app=self.app, master=self.tabs_view.tab("Processing"),
                                              parent_view=self)
        self.analysis_view = AnalysisView(app=self.app, master=self.tabs_view.tab("Analysis"),
                                          parent_view=self)

        self.terminal = None

    def open_web(self, url):
        if self.controller:
            self.controller.open_web(url)

    # def set_subviews(self):
    #     self.learning_view = LearningView(self.app, self.tabs_view.tab("Learning"), self.controller.learning_controller)
    #     self.processing_view = ProcessingView(self.app, self.tabs_view.tab("Processing"),
    #                                           self.controller.processing_controller)
    #
    #
    #     self.analysis_view = AnalysisView(self.app, self.tabs_view.tab("Analysis"),)
    #
    #     self.controller.set_subviews(self.processing_view, self.learning_view, self.analysis_view)
    #     # self.analysis_view = AnalysisView(self.app, self.tabs_view.tab("Analysis"), self.main_controller.analysis_controller)
    #
    #     # self.analysis_view.set_controller(self.main_controller.analysis_controller)

    def manage_terminal_tab(self):
        term_frame = ctk.CTkFrame(master=self.tabs_view.tab("Terminal"), )
        term_frame.place(relwidth=1, relheight=1)
        # self.terminal = Terminal(parent=self.tabs_view.tab("Terminal"))
        # self.terminal.place(relwidth=1, relheight=1, anchor=ctk.NW)

    def manage_home_tab(self):
        message = "FireLearn GUI (Graphical User Interface) is an independent software using 'fiiireflyyy', "\
                  "a third party python library developed by the same author. \n\n" \
                  "It aims to provide machine learning and deep learning solutions in a user-friendly manner for biologists."\
                  "This tool is especially made for an approach of artificial intelligence applied to biology data " \
                  "such as electrical recordings, or any kind of temporal data for instance. "\
                  "It provides several tools for processing, learning and "\
                  "analysis that can be used independently and on a variety of data within certain boundaries. \n\n" \
                  "Help is available for each section of the software by clicking the small '?' icons next to each section. "\
                  "FireLearn GUI is destined to be improved (bug tracking, more AI models, more analysis...). "
        bug_title_message = "There is a bug ? do you have a suggestion ?"
        bug_message = " You can help with the development of the project " \
                      "by reporting any issue or request using the 'issues' section of the github below, or by e-mail at " \
                      "'wlutz@irim.cnrs.fr' by specifying 'FireLearn GUI issue' (or suggestion) in the object." \
                      "\n\nFireLearn GUI has been developed by a third party and displays a basic MIT Licence."
        disclaimer_message = f"In development, for personal use only - LUTZ W. 2023\nv{params.version}"

        disclaimer_label = ctk.CTkLabel(self.tabs_view.tab("Home"), text=disclaimer_message)
        welcome_label = ctk.CTkLabel(self.tabs_view.tab("Home"), text=f"Welcome to FireLearn GUI", font=('', 18, 'bold'))
        welcome_message_label = ctk.CTkLabel(self.tabs_view.tab("Home"), text=message, font=('', 15), wraplength=500)
        bug_title_label = ctk.CTkLabel(self.tabs_view.tab("Home"), text=bug_title_message, font=('', 18, 'bold'))
        bug_label = ctk.CTkLabel(self.tabs_view.tab("Home"), text=bug_message, font=('', 15), wraplength=500)

        welcome_label.place(relx=0.16, rely=0.15, )
        welcome_message_label.place(relx=0.1, rely=0.2, )
        bug_title_label.place(relx=0.1, rely=0.6)
        bug_label.place(relx=0.1, rely=0.65)
        disclaimer_label.place(anchor=ctk.S, relwidth=1, rely=0.95, relx=0.5)

        fl_logo = ctk.CTkImage(dark_image=Image.open("data/logo firelearn temporary.png"), size=(500, 500))
        fl_label = ctk.CTkLabel(master=self.tabs_view.tab("Home"), image=fl_logo, text="")
        fl_label.place(relx=0.5, rely=0, relwidth=0.5, relheight=0.5)

        github_image = customtkinter.CTkImage(dark_image=Image.open("data/github_logo.png"),
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
