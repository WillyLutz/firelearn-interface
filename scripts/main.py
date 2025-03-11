import os
import time
import sys
import tkinter
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
        del splash
        loading_time_end = datetime.now()
        print("Loading time:", loading_time_end - loading_time_start)
        
        global usage_start_time
        usage_start_time = datetime.now()
        self.deiconify()
        #

    def onClosure(self):
        usage_end_time = datetime.now()
        print("Usage time:", usage_end_time - usage_start_time)
        print("Closing app and cleaning...")
        start_closing = datetime.now()
        self.withdraw()
        plt.close('all')
        self.quit()
        self.destroy()
        end_closing = datetime.now()
        
        del self
        print("Closing time:", end_closing - start_closing)

        sys.exit()
        


    
class Splash(ctk.CTkToplevel):
    def __init__(self, parent):
        ctk.CTkToplevel.__init__(self, parent)
        try:
            self.wm_attributes('-type', 'splash')
        except tkinter.TclError: # we launch the app most likely on windows
            self.wm_attributes('-disabled', 1)
            self.wm_attributes('-topmost', 1)
            self.wm_attributes('-toolwindow', 1)

            self.title(f'FireLearn GUI v{params.version} - loading')

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
        
        
usage_start_time = datetime.now()

def main():
    ctk.set_default_color_theme(resource_path("data/theme.json"))
    
    app = App()
    
    app.mainloop()
    
    
