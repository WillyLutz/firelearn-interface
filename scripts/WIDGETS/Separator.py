# import customtkinter as ctk
# import tkinter as tk
# import tkinter.ttk as ttk
# from scripts.WIDGETS.ErrLabel import ErrLabel
# class Separator(ttk.Separator):
#     def __init__(self, master, **kwargs):
#         super().__init__(master=master, **kwargs)
import json
import os
import sys

import customtkinter as ctk
import tkinter as tk
import tkinter.ttk as ttk

from scripts import params
from scripts.WIDGETS.ErrLabel import ErrLabel

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class Separator(ctk.CTkFrame):
    def __init__(self, master, orient="h", length=100, width=4,  **kwargs): # fg_color='gray28', bg_color='gray5',
        self.sep_width = width
        self.length = length
        if orient == 'h':
            frame_height = self.sep_width
            frame_width = self.length
        else:
            frame_height = self.length
            frame_width = self.sep_width

        theme_path = resource_path(f'data/theme-{params.theme}.json')
        with open(theme_path, 'r') as file:
            theme_file = json.load(file)
        
        super().__init__(master=master, height=frame_height, width=frame_width,
                         fg_color=theme_file["Separator"]["fg_color"], border_width=1,
                         border_color=theme_file["Separator"]["border_color"], **kwargs)
        file.close()
        # second_frame = ctk.CTkFrame(master=self, fg_color=bg_color)
        #
        # relx, rely, relwidth, relheight = (0, 0.5, 1, 0.5) if orient == 'h' else (0.5, 0, 0.5, 1)
        # second_frame.place(relx=relx, rely=rely, relwidth=relwidth, relheight=relheight)
