# This is a sample Python script.
from functools import partial

import customtkinter

import params
from VIEW.MainView import MainView

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.title(f'FireLearn GUI v{params.version}')
        view = MainView(self)
        self.after(50, self.deiconify)


def onClosure(app):
    app.quit()
    exit()


if __name__ == '__main__':
    app = App()
    app.protocol('WM_DELETE_WINDOW', partial(onClosure, app))  # root is your root window
    app.mainloop()

