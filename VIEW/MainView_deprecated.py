import tkinter as tk
from tkinter import ttk

import pandastable
from PIL import ImageTk, Image
from functools import partial
from pandastable import Table, TableModel
import pandas as pd
import data.params as p


class MainView(tk.Frame):
    def __init__(self, app):
        super().__init__()

        self.app = app
        self.app.geometry("1080x720")
        self.app.resizable(0, 0)
        self.app.configure(height=720, width=1080)

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
        self.main_frame = tk.Frame(self.app, height=self.app.winfo_reqheight(), width=self.app.winfo_reqwidth(),
                                   background='yellow')
        self.main_frame.place(x=0, y=0)

        #######################################################################
        "----------------------ELEMENTS TO UPDATE-----------------------"
        self.dataset_label_text = tk.StringVar()
        self.dataset_label_text.set(p.default_dataset_path)
        self.dataset_info = tk.StringVar()

        self.datatable = pandastable.Table

        self.target_box = tk.ttk.Combobox
        self.current_target = tk.StringVar()
        self.current_target.set(p.default_targets[0])


        ####################################################################
        "-----------------TABS------------------"

        self.tab_control = ttk.Notebook(self.main_frame, height=self.main_frame.winfo_reqheight(),
                                        width=self.main_frame.winfo_reqwidth())
        self.home_tab = tk.Frame(self.tab_control, background='pink')
        self.models_tab = tk.Frame(self.tab_control)
        self.dataset_tab = tk.Frame(self.tab_control, background='yellow')
        self.training_tab = tk.Frame(self.tab_control)
        self.validation_tab = tk.Frame(self.tab_control)

        self.tab_control.add(self.home_tab, text="Home")
        self.tab_control.add(self.models_tab, text="Models")
        self.tab_control.add(self.dataset_tab, text="Dataset")
        self.tab_control.add(self.training_tab, text="Training")
        self.tab_control.add(self.validation_tab, text="Validation")
        self.tab_control.pack(side=tk.LEFT)

        self.manage_home_tab()
        self.manage_dataset_tab()

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
        welcome_message.place(anchor=tk.CENTER, relx=0.2, rely=0.5)

        disclaimer_label = tk.Label(self.home_tab, text="In development, for personal use only")
        disclaimer_label.place(anchor=tk.S, relx=0.5, rely=0.95)

        logo_canvas = tk.Canvas(self.home_tab, bg='green', height=500, width=500, borderwidth=0, highlightthickness=0)
        logo_canvas.place(anchor=tk.E, relx=1, rely=0.5)

        logo = Image.open("data/logo firelearn temporary.png")
        logo_canvas.image = ImageTk.PhotoImage(logo.resize((logo_canvas.winfo_reqheight(),
                                                            logo_canvas.winfo_reqheight()), Image.ANTIALIAS))
        logo_canvas.create_image(0, 0, image=logo_canvas.image, anchor='nw')

    def manage_dataset_tab(self):
        # --------------------LOADING------------------
        loading_size = (int(self.main_frame.winfo_reqheight() / 5), int(self.main_frame.winfo_reqwidth() / 2))
        loading_frame = tk.Frame(self.dataset_tab, height=loading_size[0], width=loading_size[1], background='pink')
        loading_frame.place(anchor=tk.NW, relx=0, rely=0)

        load_btn = tk.Button(loading_frame, text='Load', command=self.open_file)
        load_btn.place(relx=0, rely=0, anchor=tk.NW)

        discard_btn = tk.Button(loading_frame, text='discard', command=self.reset_loaded_file)
        discard_btn.place(relx=0, rely=0.3)

        dataset_label = tk.Label(loading_frame, textvariable=self.dataset_label_text)
        dataset_label.place(relx=0.2, rely=0.04)

        dataset_info = tk.Label(loading_frame, textvariable=self.dataset_info)
        dataset_info.place(relx=0.2, rely=0.3)
        # --------------------OPERATIONS-------------------
        operations_size = (int(self.main_frame.winfo_reqheight() / 5 * 3), int(self.main_frame.winfo_reqwidth() / 2))
        operations_frame = tk.Frame(self.dataset_tab, height=operations_size[0], width=operations_size[1],
                                    background='blue')
        operations_frame.place(anchor=tk.NW, relx=0, rely=0.2)

        delete_rows_btn = tk.Button(operations_frame, text='Delete selected rows', command=self.delete_dataframe_rows)
        delete_rows_btn.place(relx=0, rely=0)
        delete_cols_btn = tk.Button(operations_frame, text='Delete selected columns', command=self.delete_dataframe_columns)
        delete_cols_btn.place(relx=0.34, rely=0)

        self.target_box = tk.ttk.Combobox(operations_frame, values=p.default_targets, state='readonly')
        self.target_box.place(relx=0, rely=0.3)
        self.target_box.current(0)

        immu_target_label = tk.Label(operations_frame, text="Selected target: ")
        immu_target_label.place(relx=0.35, rely=0.3)

        target_label = tk.Label(operations_frame, textvariable=self.current_target)
        target_label.place(relx=0.58, rely=0.3)

        target_btn = tk.Button(operations_frame, text="Select target", command=self.select_target)
        target_btn.place(relx=0, rely=0.2)
        # todo: coloring the target column

        # todo: preprocessing (nan, threshold mean max, mean...)
        # todo: automatic preprocessing ? detection of abnormal lines etc...

        # ---------------------VALIDATION---------------------
        validation_size = (int(self.main_frame.winfo_reqheight() / 5), int(self.main_frame.winfo_reqwidth() / 2))
        validation_frame = tk.Frame(self.dataset_tab, height=validation_size[0], width=validation_size[1],
                                    background='green')
        validation_frame.place(anchor=tk.NW, relx=0, rely=0.8)

        # todo: save dataset under, validate dataset

        # ----------------------OVERVIEW-----------------------
        overview_size = (int(self.main_frame.winfo_reqheight()), int(self.main_frame.winfo_reqwidth() / 2))
        overview_frame = tk.Frame(self.dataset_tab, height=overview_size[0], width=overview_size[1],
                                  background='purple')
        overview_frame.place(anchor=tk.NW, relx=0.5, rely=0)

        # datatable = pandastable.Table(overview_frame,dataframe=pd.read_csv("data/emptycsv.csv"), showtoolbar=True,
        #                                    showstatusbar=True)
        self.datatable = pandastable.Table(overview_frame, showtoolbar=True,
                                           showstatusbar=True)
        self.datatable.place(relx=0, rely=0)
        self.datatable.show()

    def open_file(self):
        if self.controller:
            self.controller.load_dataset()

    def reset_loaded_file(self):
        if self.controller:
            self.controller.reset_loaded_dataset()

    def delete_dataframe_rows(self):
        if self.controller:
            self.controller.delete_dataframe_rows()

    def delete_dataframe_columns(self):
        if self.controller:
            self.controller.delete_dataframe_columns()

    def select_target(self):
        if self.controller:
            self.controller.select_target()