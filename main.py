# This is a sample Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from VIEW.MainView import MainView
from CONTROLLER.MainController import MainController
from MODEL.MainModel import MainModel
import params
import customtkinter


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()

        self.title(f'FireLearn GUI v{params.version}')

        # create a model

        # create a view and place it on the master window
        view = MainView(self)

        # create a main_controller

        # set the main_controller to view
        # view.set_controller(controller)
        self.after(0, self.deiconify)

if __name__ == '__main__':
    import warnings
    warnings.simplefilter('ignore')

    app = App()

    app.mainloop()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/

