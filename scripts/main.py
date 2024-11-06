import os
import time
from functools import partial
from tkinter import PhotoImage
from PIL import Image

import customtkinter as ctk
import tkinter as tk
import tkinter.ttk as ttk
from scripts import params
from scripts.params import resource_path
from scripts.VIEW.MainView import MainView


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f'FireLearn GUI v{params.version}')
        self.withdraw()
        splash = Splash(self)
        
        logo = PhotoImage(file=resource_path('data/firelearn_img/logo firelearn no text.png'))
        self.iconphoto(False, logo)
        self.iconname('FireLearn')
        self.protocol('WM_DELETE_WINDOW', partial(onClosure, self))
        
        
        view = MainView(self)
        splash.destroy()
        self.deiconify()


def onClosure(app):
    app.quit()
    exit()


def loading(app):
    loading_screen  = ctk.CTkToplevel()
    
    
class Splash(ctk.CTkToplevel):
    def __init__(self, parent):
        ctk.CTkToplevel.__init__(self, parent)
        self.wm_attributes('-type', 'splash')
        self.geometry("500x316")
        self.resizable(False, False)
        
        loading_frame = ctk.CTkFrame(master=self)
        loading_frame.place(relheight=1, relwidth=1)
        
        logo = PhotoImage(file=resource_path('data/firelearn_img/logo firelearn no text.png'))
        self.iconphoto(False, logo)
        self.iconname('FireLearn')
        self.protocol('WM_DELETE_WINDOW', partial(onClosure, self))
        fl_logo = ctk.CTkImage(dark_image=Image.open(resource_path("data/firelearn_img/logo firelearn light text.png")),
                                size=(500, 316))
        fl_label = ctk.CTkLabel(master=loading_frame, image=fl_logo, text="")
        fl_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        ## required to make window show before the program gets to the mainloop
        self.update()

def main():
    ctk.set_default_color_theme(resource_path("data/theme.json"))
    
    app = App()
    
    app.mainloop()
