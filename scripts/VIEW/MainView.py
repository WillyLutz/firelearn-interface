import json
from doctest import master
from functools import partial

import customtkinter
import customtkinter as ctk
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.colorchooser import askcolor
from PIL import Image

from scripts import params, params as p
from scripts.CONTROLLER.MainController import MainController
from scripts.VIEW.AnalysisView import AnalysisView
from scripts.VIEW.LearningView import LearningView
from scripts.VIEW.ProcessingView import ProcessingView

import pathlib
from scripts.params import  resource_path

class MainView(ttk.Frame):
    def __init__(self, app):
        super().__init__(master=app)

        self.app = app
        self.app.geometry("1440x900")
        self.app.resizable(1, 1)
        # self.app.configure(height=720, width=1080)
        self.app.minsize(height=450, width=800)

        

        # ------------ MENU ----------------------------
        self.menu_bar = tk.Menu(self.app)
        self.load_config_menu = tk.Menu(self.app, tearoff=0)
        self.save_config_menu = tk.Menu(self.app, tearoff=0)

        self.load_learning_menu = tk.Menu(self.app, tearoff=0)
        self.load_analysis_menu = tk.Menu(self.app, tearoff=0)
        self.save_learning_menu = tk.Menu(self.app, tearoff=0)
        self.save_analysis_menu = tk.Menu(self.app, tearoff=0)
        
        self.menu_file = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_file.add_cascade(label="Open configuration", menu=self.load_config_menu)
        self.menu_file.add_cascade(label="Save configuration", menu=self.save_config_menu)
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Exit", command=self.quit)
        
        # --- load config menu
        self.load_config_menu.add_command(label="Processing (.pcfg)...", command=self.load_processing_config)
        self.load_config_menu.add_cascade(label="Learning", menu=self.load_learning_menu)
        self.load_config_menu.add_cascade(label="Analysis", menu=self.load_analysis_menu)
        
        self.load_learning_menu.add_command(label="RFC (.rfcfg)...", command=self.load_rfc_config)

        self.load_analysis_menu.add_command(label="Plot (.pltcfg)...", command=self.load_plot_config)
        self.load_analysis_menu.add_command(label="Feature importance (.ficfg)...", command=self.load_importance_config)
        self.load_analysis_menu.add_command(label="PCA (.pcacfg)...", command=self.load_pca_config)
        self.load_analysis_menu.add_command(label="Confusion matrix (.confcfg)...", command=self.load_confusion_config)
        self.load_analysis_menu.add_command(label="Spike detection (.skcfg)...", command=self.load_spike_config)

        # --- save config menu
        self.save_config_menu.add_command(label="Processing (.pcfg)...", command=self.save_processing_config)
        self.save_config_menu.add_cascade(label="Learning", menu=self.save_learning_menu)
        self.save_config_menu.add_cascade(label="Analysis", menu=self.save_analysis_menu)
        
        self.save_learning_menu.add_command(label="RFC (.rfcfg)...", command=self.save_rfc_config)
        
        self.save_analysis_menu.add_command(label="Plot (.pltcfg)...", command=self.save_plot_config)
        self.save_analysis_menu.add_command(label="Feature importance (.ficfg)...", command=self.save_importance_config)
        self.save_analysis_menu.add_command(label="PCA (.pcacfg)...", command=self.save_pca_config)
        self.save_analysis_menu.add_command(label="Confusion matrix (.confcfg)...", command=self.save_confusion_config)
        self.save_analysis_menu.add_command(label="Spike detection (.skcfg)...", command=self.save_spike_config)

        
        self.menu_help = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_help.add_command(label="Help")
        
        self.menu_about = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_about.add_command(label="Github...", command=partial(self.open_web,
                                                      "https://github.com/WillyLutz/firelearn-interface"))
        self.menu_about.add_command(label="About Us", command=self.about_us)
        self.menu_about.add_separator()
        
        self.menu_bar.add_cascade(label="File", menu=self.menu_file)
        self.menu_bar.add_cascade(label="Help", menu=self.menu_help)
        self.menu_bar.add_cascade(label="About", menu=self.menu_about)
        self.app.config(menu=self.menu_bar)

        
        # ------------- MASTER FRAME -------------------
        self.master_frame = ctk.CTkFrame(master=self.app, )
        self.master_frame.place(relwidth=1.0, relheight=1)
        # ------------- TABS MENU ----------------------
        self.tabs_view = ctk.CTkTabview(master=self.master_frame, border_color='red', corner_radius=10)
        self.tabs_view.place(relwidth=1.0, relheight=1.0)
        self.tabs_view.add("Processing")
        self.tabs_view.add("Learning")
        self.tabs_view.add("Analysis")

        # ------------- MANAGING PARENT TABS -----------

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
    def about_us(self):
        top_level = ctk.CTkToplevel(master=self.app)
        top_level.geometry("500x800")
        
        top_level.title(f'FireLearn GUI v{params.version} - About us')
        
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
                      "by reporting any issue or request using the 'issues' section of the github (About > Github), or by e-mail at " \
                      "'willy.lutz@irim.cnrs.fr' by specifying 'FireLearn GUI issue' (or suggestion) in the object." \
                      "\n\nFireLearn GUI has been developed by a third party and displays a basic MIT Licence."
        disclaimer_message = f"In development, for personal use only - LUTZ W. 2023\nv{params.version}"
        
        disclaimer_label = ctk.CTkLabel(top_level, text=disclaimer_message)
        welcome_label = ctk.CTkLabel(top_level, text=f"Welcome to FireLearn GUI",
                                     font=('', 18, 'bold'))
        welcome_message_label = ctk.CTkLabel(top_level, text=message, font=('', 15), wraplength=400)
        bug_title_label = ctk.CTkLabel(top_level, text=bug_title_message, font=('', 18, 'bold'))
        bug_label = ctk.CTkLabel(top_level, text=bug_message, font=('', 15), wraplength=400)
        
        welcome_label.place(relx=0.2, rely=0.05)
        welcome_message_label.place(relx=0.1, rely=0.12, )
        bug_title_label.place(relx=0.05, rely=0.6)
        bug_label.place(relx=0.1, rely=0.65)
        disclaimer_label.place(anchor=ctk.S, relwidth=1, rely=0.95, relx=0.5)
        
        


    @staticmethod
    def update_slider_value(value, var):
        var.set(str(round(value, 2)))

    def select_color(self, view, selection_button_name):
        color = askcolor(color='green')
        if color:
            view.buttons[selection_button_name].configure(fg_color=color[1])
            view.vars[selection_button_name].set(color[1])


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
        if value != '':
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



    def load_processing_config(self):
        self.processing_view.load_model()
    
    def load_rfc_config(self):
        self.learning_view.load_model() # todo : migrate to an RfcView, for when adding other ML algorithms
        
    def load_plot_config(self):
        pass # todo : implement plot load model
    
    def load_importance_config(self):
        pass # todo : implement plot load model
    
    def load_pca_config(self):
        pass # todo : implement plot load model
    
    def load_confusion_config(self):
        pass # todo : implement plot load model
    
    def load_spike_config(self):
        self.analysis_view.spike_view.load_config()
    
    def save_processing_config(self):
        self.processing_view.save_config()
    
    def save_rfc_config(self):
        self.learning_view.save_config()  # todo : migrate to an RfcView, for when adding other ML algorithms
    
    def save_plot_config(self):
        pass  # todo : implement plot save model
    
    def save_importance_config(self):
        pass  # todo : implement plot save model
    
    def save_pca_config(self):
        pass  # todo : implement plot save model
    
    def save_confusion_config(self):
        pass  # todo : implement plot save model
    
    def save_spike_config(self):
        self.analysis_view.spike_view.save_config()