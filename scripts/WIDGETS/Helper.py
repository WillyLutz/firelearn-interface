import webbrowser
from functools import partial

import customtkinter as ctk
from PIL import Image

from scripts.params import  resource_path


class Helper(ctk.CTkLabel):

    def __init__(self, event_key, **kwargs):
        img = ctk.CTkImage(dark_image=Image.open(resource_path("data/firelearn_img/question-button.png")), size=(20, 20))
        super().__init__(image=img, text="", **kwargs)
        self.bind('<Button-1>', partial(self.on_click, event_key))

    def on_click(self, event_key, event=None, ):
        base = 'https://github.com/WillyLutz/firelearn-interface/blob/main/README.md'
        webbrowser.open(base+event_key, new=1)

