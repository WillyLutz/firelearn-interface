import tkinter as tk
from functools import partial

import customtkinter
import customtkinter as ctk
from PIL import Image

from VIEW.AnalysisView import AnalysisView
from VIEW.LearningView import LearningView
from VIEW.ProcessingView import ProcessingView


class MainView(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(master=app)

        self.app = app
        self.app.geometry("1920x1080")
        self.app.resizable(1, 1)
        self.app.configure(height=720, width=1080)

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
        self.learning_view = None
        self.processing_view = None
        self.analysis_view = None
        self.helper_view = None

        self.controller = None
        self.terminal = None



    def open_web(self, url):
        if self.controller:
            self.controller.open_web(url)

    def set_controller(self, controller):
        self.controller = controller
        self.set_subviews()

    def set_subviews(self):
        self.learning_view = LearningView(self.app, self.tabs_view.tab("Learning"), self.controller.learning_controller)
        self.processing_view = ProcessingView(self.app, self.tabs_view.tab("Processing"),
                                              self.controller.processing_controller)

        self.analysis_view = AnalysisView(self.app, self.tabs_view.tab("Analysis"),
                                          self.controller.analysis_controller)
        self.controller.set_subviews(self.processing_view, self.learning_view, self.analysis_view)
        # self.analysis_view = AnalysisView(self.app, self.tabs_view.tab("Analysis"), self.controller.analysis_controller)

        # self.analysis_view.set_controller(self.controller.analysis_controller)

    def manage_terminal_tab(self):
        term_frame = ctk.CTkFrame(master=self.tabs_view.tab("Terminal"), )
        term_frame.place(relwidth=1, relheight=1)
        # self.terminal = Terminal(parent=self.tabs_view.tab("Terminal"))
        # self.terminal.place(relwidth=1, relheight=1, anchor=ctk.NW)

    def manage_home_tab(self):
        welcome_label = ctk.CTkLabel(self.tabs_view.tab("Home"), text=f"Welcome to FireLearn", font=('', 18, 'bold'))
        welcome_label.place(relwidth=0.5, relheight=0.1)
        message = "FireLearn is an independent python library used\n" \
                  " to do machine learning and deep learning. This\n" \
                  " tool is especially made for a user friendly \n" \
                  "approach of the artificial intelligence applied\n" \
                  " in a biological context. \n\n" \
                  "FireLearn GUI has been developed by a third party\n" \
                  "and do not display any licence."
        welcome_message = ctk.CTkLabel(self.tabs_view.tab("Home"), text=message, font=('', 15))
        welcome_message.place(anchor=ctk.W, rely=0.3, relwidth=0.5, )

        disclaimer_label = ctk.CTkLabel(self.tabs_view.tab("Home"), text="In development, for personal use only - "
                                                                         "LUTZ W. 2023")
        disclaimer_label.place(anchor=ctk.S, relwidth=1, rely=0.95, relx=0.5)

        fl_logo = ctk.CTkImage(dark_image=Image.open("data/logo firelearn temporary.png"), size=(500, 500))
        fl_label = ctk.CTkLabel(master=self.tabs_view.tab("Home"), image=fl_logo, text="")
        fl_label.place(relx=0.5, rely=0)

        github_image = customtkinter.CTkImage(dark_image=Image.open("data/github_logo.png"),
                                              size=(60, 60))
        github_button = ctk.CTkButton(master=self.tabs_view.tab("Home"), image=github_image, text="",
                                      width=70, height=70, corner_radius=10,
                                      command=partial(self.open_web,
                                                      "https://github.com/WillyLutz/firelearn-interface"))
        github_button.place(relx=0.1, rely=0.6)

    def manage_help_processing(self, sframe):
        # todo : create the helpers sections
        pass

