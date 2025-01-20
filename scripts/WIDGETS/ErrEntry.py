import customtkinter as ctk
from scripts.WIDGETS.ErrLabel import ErrLabel
class ErrEntry(ctk.CTkEntry):

    def __init__(self, master,  message='', error_anchor=ctk.NW, error_color='tomato', **kwargs):
        super().__init__(master=master, **kwargs)
        self.error_message = ctk.StringVar(value=message)

        self.error_label = ErrLabel(master=self.master, text_color=error_color, textvariable=self.error_message)
        self.winfo_toplevel().update()

    def place_error(self, **kwargs):
        self.error_label.place(**kwargs)

    def place_errentry(self, relpadx=0, relpady=-0.04, padx=0, pady=30,  **kwargs):
        self.place(**kwargs)
        if 'relx' in kwargs.keys() or 'rely' in kwargs.keys():
            self.error_label.place(relx=kwargs['relx'] + relpadx, rely=kwargs['rely'] + relpady)
        elif 'x' in kwargs.keys() or 'y' in kwargs.keys():
            self.error_label.place(x=kwargs['x'] + padx, y=kwargs['y'] + pady)


    def set_error(self, message):
        self.error_message.set(message)

    def clean_error(self):
        self.error_message.set("")