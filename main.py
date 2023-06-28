# This is a sample Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import tkinter as tk

import matplotlib

from VIEW.MainView import MainView
from CONTROLLER.MainController import MainController
from MODEL.MainModel import MainModel
from data import params
import customtkinter

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title(f'FireLearn GUI v{params.version}')

        # create a model
        model = MainModel()

        # create a view and place it on the master window
        view = MainView(self)

        # create a controller
        controller = MainController(model, view)

        # set the controller to view
        view.set_controller(controller)


if __name__ == '__main__':
    import warnings
    warnings.simplefilter('ignore')
    import matplotlib.font_manager

    app = App()

    app.mainloop()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/

