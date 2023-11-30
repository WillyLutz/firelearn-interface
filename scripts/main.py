import os
from functools import partial
from tkinter import PhotoImage

import customtkinter

from scripts import params
from scripts.params import resource_path
from scripts.VIEW.MainView import MainView


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


def main():
    customtkinter.set_default_color_theme(resource_path("data/theme.json"))
    
    app = App()
    logo = PhotoImage(file=resource_path('data/firelearn_img/logo firelearn no text.png'))
    app.iconphoto(False, logo)
    app.iconname('FireLearn')
    app.protocol('WM_DELETE_WINDOW', partial(onClosure, app))
    
    app.mainloop()
