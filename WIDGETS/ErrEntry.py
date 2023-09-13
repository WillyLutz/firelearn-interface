import customtkinter as ctk

class ErrEntry(ctk.CTkEntry):

    def __init__(self, master,  error_message='', error_anchor=ctk.NW, error_color='red', **kwargs):
        super().__init__(master=master, **kwargs)
        self.error_message = ctk.StringVar(value=error_message)
        self.error_label = ctk.CTkLabel(master=self.master, text_color=error_color, textvariable=self.error_message)
        self.error_label.pack(anchor=error_anchor,side='right')
        self.winfo_toplevel().update()
        print(self.winfo_rootx(), self.winfo_rooty())
