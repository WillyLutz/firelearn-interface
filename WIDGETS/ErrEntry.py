import customtkinter as ctk
from WIDGETS.ErrLabel import ErrLabel
class ErrEntry(ctk.CTkEntry):

    def __init__(self, master,  message='', error_anchor=ctk.NW, error_color='red', **kwargs):
        super().__init__(master=master, **kwargs)
        self.error_message = ctk.StringVar(value=message)

        self.error_label = ErrLabel(master=self.master, text_color=error_color, textvariable=self.error_message)
        self.winfo_toplevel().update()

    def place_error(self, **kwargs):
        self.error_label.place(**kwargs)

    def place_entry_err(self, padx=0, pady=-0.04, **kwargs):
        self.place(**kwargs)
        self.error_label.place(relx=kwargs['relx']+padx, rely=kwargs['rely']+pady)

    def set_error(self, message):
        self.error_message.set(message)

