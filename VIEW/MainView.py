import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image


class MainView(tk.Frame):
    def __init__(self, app):
        super().__init__()

        self.app = app
        self.app.geometry("550x400")

        ####################################################################
        "-----------------MENU BAR-----------------"

        self.menu_bar = tk.Menu()
        self.file_menu = tk.Menu(self.menu_bar)
        self.file_menu.add_command(label="Save data")
        self.file_menu.add_command(label="Load data")
        self.file_menu.add_command(label="Exit")

        self.help_menu = tk.Menu(self.menu_bar)
        self.help_menu.add_command(label="Getting Started")
        self.help_menu.add_command(label="Help ?")
        self.help_menu.add_command(label="About")

        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)

        self.app.config(menu=self.menu_bar)

        ####################################################################
        "-----------------MAIN FRAME------------------"

        self.main_frame = tk.Frame(self.app, height=300, width=300, background='yellow')
        self.main_frame.place(x=0, y=0)

        ####################################################################
        "-----------------TABS------------------"

        self.tab_control = ttk.Notebook(self.main_frame, height=200, width=250)
        self.home_tab = tk.Frame(self.tab_control, background='pink')
        self.models_tab = tk.Frame(self.tab_control)
        self.dataset_tab = tk.Frame(self.tab_control)
        self.training_tab = tk.Frame(self.tab_control)
        self.validation_tab = tk.Frame(self.tab_control)

        self.tab_control.add(self.home_tab, text="Home")
        self.tab_control.add(self.models_tab, text="Models")
        self.tab_control.add(self.dataset_tab, text="Dataset")
        self.tab_control.add(self.training_tab, text="Training")
        self.tab_control.add(self.validation_tab, text="Validation")
        self.tab_control.pack(side=tk.LEFT)

        self.manage_home_tab()

        self.controller = None

    def set_controller(self, controller):
        self.controller = controller

    def manage_home_tab(self):

        welcome_label = tk.Label(self.home_tab, text=f"Welcome to FireLearn", font=('Helvetica', 18, 'bold'))
        welcome_label.place(anchor=tk.CENTER, relx=0.2, rely=0.3)
        message = "FireLearn is an independent python library used\n" \
                  " to do machine learning and deep learning. This\n" \
                  " tool is especially made for a user friendly \n" \
                  "approach of the artificial intelligence applied\n" \
                  " in a biological context. \n\n" \
                  "FireLearn GUI has been developed by a third party\n" \
                  "and do not display any licence."
        welcome_message = tk.Label(self.home_tab, text=message, font=('Helvetica', 10))
       # welcome_message.place(anchor=tk.W, relx=0, rely=0.5)

        disclaimer_label = tk.Label(self.home_tab, text="In development, for personal use only")
        #disclaimer_label.place(anchor=tk.S, relx=0.5, rely=1)
        img = ImageTk.PhotoImage(file="data/logo firelearn temporary.png")

        # Create a Label Widget to display the text or Image
        logo = tk.Label(self.home_tab, image=img)

