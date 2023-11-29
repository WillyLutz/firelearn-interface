import customtkinter as ctk
import tkinter as tk


class ErrLabel(ctk.CTkLabel):

    def __init__(self, master, text='', **kwargs):
        super().__init__(master=master, **kwargs)
