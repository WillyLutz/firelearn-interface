# This is a sample Python script.
import traceback
from functools import partial
from tkinter import messagebox

import customtkinter

import params
from VIEW.MainView import MainView
import customtkinter as ctk
from PIL import Image, ImageTk
import tkinter as tk

import ctypes


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.title(f'FireLearn GUI v{params.version}')
        view = MainView(self)
        self.after(50, self.deiconify)


def onClosure(app):
    app.quit()
    exit()


if __name__ == '__main__':
    customtkinter.set_default_color_theme("theme.json")

    app = App()
    app.protocol('WM_DELETE_WINDOW', partial(onClosure, app))

    app.mainloop()
