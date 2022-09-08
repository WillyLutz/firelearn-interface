# This is a sample Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import tkinter as tk
from VIEW.MainView import MainView
from CONTROLLER.MainController import Controller
from MODEL.MainModel import Model
from data import params


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(f'FireLearn GUI v{params.version}')

        # create a model
        model = Model()

        # create a view and place it on the root window
        view = MainView(self)

        # create a controller
        controller = Controller(model, view)

        # set the controller to view
        view.set_controller(controller)


if __name__ == '__main__':
    app = App()

    app.mainloop()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
