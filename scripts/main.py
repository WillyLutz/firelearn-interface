import os
import time
from datetime import datetime
from functools import partial
from tkinter import PhotoImage
from PIL import Image

import customtkinter as ctk
import tkinter as tk
import tkinter.ttk as ttk

from matplotlib import pyplot as plt

from scripts import params
from scripts.params import resource_path
from scripts.VIEW.MainView import MainView


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f'FireLearn GUI v{params.version}')
        self.withdraw()
        loading_time_start = datetime.now()
        self.protocol('WM_DELETE_WINDOW', self.onClosure)
        
        splash = Splash(self)
        
        logo = PhotoImage(file=resource_path('data/firelearn_img/logo firelearn no text.png'))
        self.iconphoto(False, logo)
        self.iconname('FireLearn')
        view = MainView(self)
        splash.destroy()
        loading_time_end = datetime.now()
        # print("loading time:", loading_time_end - loading_time_start)
        self.deiconify()


    def onClosure(self):
        self.withdraw()
        plt.close('all')
        self.quit()
        self.destroy()
        exit()
        


    
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
        # self.protocol('WM_DELETE_WINDOW', self.onClosure)
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
    
