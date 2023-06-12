import tkinter
from tkinter import messagebox
import customtkinter as ctk
import threading
import time


class ProgressBar(threading.Thread):
    def __init__(self, name, app):
        super().__init__()
        self.completed_tasks = 0
        self.total_tasks = 0
        self.progress_stringvar = tkinter.StringVar()
        self.name = name
        self.app = app

        progress_window = ctk.CTkToplevel(master=self.app)
        progress_window.title(self.name)
        progress_window.geometry("400x200")
        self.progress_bar = ctk.CTkProgressBar(progress_window, orientation='horizontal', mode='determinate')
        self.progress_bar.place(relx=0.05, rely=0.3, relwidth=0.9)
        self.update_progress_stringvar("Processing")
        self.progress_label = ctk.CTkLabel(progress_window, textvariable=self.progress_stringvar)
        self.progress_label.place(anchor=tkinter.CENTER, relx=0.5, rely=0.7)

    def update_progress(self, taskname):
        if self.progress_bar.get() < 1:
            self.progress_bar.set((self.completed_tasks / self.total_tasks))
            self.update_progress_stringvar(taskname)
        self.app.update()

    def update_progress_stringvar(self, taskname):
        percent = round(self.progress_bar.get() * 100, 1)
        if percent >= 100:
            self.progress_stringvar.set(f"Processing finished. {percent}% "
                                        f"({int(self.completed_tasks)}/{int(self.total_tasks)})\nYou can close this window.")
        else:
            self.progress_stringvar.set(f"Current Progress: {percent}%\n"
                                        f"{taskname}\n({int(self.completed_tasks)}/{int(self.total_tasks)})\n\nDo not close this window.")
            # self.progress_stringvar.set(f"Current Progress: {round(self.progress_bar.get() * 100, 1)}%\n"
            #                            f"({int(self.completed_tasks)}/{int(self.total_tasks)})\n\nDo not close this window.")

    def increment_progress(self, n=1):
        self.completed_tasks = self.completed_tasks + n

    # todo : for the HEAVY PROCESSING TEST, completed tasks > total tasks
    # todo : after processing when closing the windows, 'while executing --- ("after" script) probably due to daemon threading
