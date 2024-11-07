import tkinter as tk
import tkinter.ttk as ttk
from functools import partial

import customtkinter as ctk
from PIL import ImageTk, Image
from PIL.ImageTk import PhotoImage


class ImageButton(ctk.CTkLabel):

    def __init__(self, img, command=None, **kwargs):
        self.command = command
        self.img = img
        super().__init__(image=self.img, text="", **kwargs)

        if self.command is not None:
            self.set_command(command)

    def set_command(self, command):
        self.command = command
        self.bind('<Button-1>', command=self.command)
        
    def get_image_size(self):
        return self.img.cget("size")
    
    def set_image_size(self, size):
        self.img.configure(size=size)




