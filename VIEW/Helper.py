import tkinter as tk
import tkinter.ttk as ttk
from functools import partial

import customtkinter as ctk
from PIL import ImageTk, Image
from PIL.ImageTk import PhotoImage
from VIEW.HelperTopLevels import ProcessingHelper, LearningHelper


class Helper(ctk.CTkLabel):

    def __init__(self, event_key, **kwargs):
        img = ctk.CTkImage(dark_image=Image.open("data/question-button.png"), size=(20, 20))
        super().__init__(image=img, text="", **kwargs)
        self.bind('<Button-1>', partial(self.on_click, event_key))

    def on_click(self, event_key, event=None, ):
        if event_key == "sorting":
            ProcessingHelper.sorting()
        elif event_key == "single file":
            ProcessingHelper.single_file()
        elif event_key == "raw mea":
            ProcessingHelper.raw_mea()
        elif event_key == "select electrodes":
            ProcessingHelper.select_electrodes()
        elif event_key == "sampling":
            ProcessingHelper.sampling()
        elif event_key == "filter":
            ProcessingHelper.filter()
        elif event_key == "fft":
            ProcessingHelper.fft()
        elif event_key == "exec":
            ProcessingHelper.exec()

        elif event_key == "clf params":
            LearningHelper.clf_params()
        elif event_key == "load dataset":
            LearningHelper.load_dataset()
        elif event_key == "select targets":
            LearningHelper.select_targets()
        elif event_key == "training targets":
            LearningHelper.training_targets()
        elif event_key == "get advanced metrics":
            LearningHelper.get_advanced_metrics()
        elif event_key == "load clf":
            LearningHelper.load_clf()
        elif event_key == "save clf":
            LearningHelper.save_clf()
        elif event_key == "advanced metrics":
            LearningHelper.advanced_metrics()

