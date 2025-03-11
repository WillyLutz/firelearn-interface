import time
import tkinter
import customtkinter as ctk
import threading


class ProgressBar(threading.Thread, ):
    """
    A class to display a progress bar in a separate thread while tracking task completion.

    The `ProgressBar` class creates a pop-up window with a progress bar and updates its progress
    as tasks are completed. It can also display the current task and the percentage of completion.
    The class runs in a separate thread to ensure the main application remains responsive.

    Parameters
    ----------
    name : str
        The name of the progress bar window.

    app : tkinter.Tk
        The parent Tkinter application that the progress bar window will belong to.
    """
    
    def __init__(self, name, app):
        super().__init__()
        self.daemon = True
        self.task = ""
        self.completed_tasks = 0
        self.total_tasks = 0
        self.progress_stringvar = tkinter.StringVar()
        self.name = name
        self.app = app
        self._stop_event = threading.Event()

        self.progress_window = ctk.CTkToplevel(master=self.app)
        self.progress_window.title(self.name)
        self.progress_window.geometry("400x200")
        self.progress_window.attributes("-topmost", 1)
        self.progress_bar = ctk.CTkProgressBar(self.progress_window, orientation='horizontal', mode='determinate')
        self.progress_bar.place(relx=0.05, rely=0.1, relwidth=0.9)
        self.update_progress_stringvar("Processing")
        self.progress_label = ctk.CTkLabel(self.progress_window, textvariable=self.progress_stringvar)
        self.progress_label.place(anchor=tkinter.CENTER, relx=0.5, rely=0.5)
        
        self.cancel_button = ctk.CTkButton(master=self.progress_window, text="Cancel", fg_color='tomato', command=self._on_cancel)
        self.cancel_button.place(anchor=tkinter.CENTER, rely=0.9, relx=0.5)
        self.progress_window.focus_force()
    
    def run(self):
        """ Keeps the progress window active and updates it periodically. """
        while not self.stopped():
            self.app.update_idletasks()  # Keeps the Tkinter app responsive
            time.sleep(0.1)
    
    def _on_cancel(self):
        """
        Cancel the processing, close the toplevel and stop the threads.
        
        Returns
        -------

        """
        self.stop()
        if self.stopped():
            self.progress_window.destroy()
        
    
    def stop(self):
        """
        Stops the progress bar and halts the thread that is running the progress bar.

        This method sets a stop event to signal that the progress bar thread should stop running.
        It can be used to terminate the progress bar operation when it is no longer needed.

        Returns
        -------
        None
        """
        self._stop_event.set()
    
    def stopped(self):
        """
        Checks whether the progress bar thread has been stopped.

        This method returns a boolean indicating whether the stop event has been set,
        signaling that the progress bar thread should no longer update.

        Returns
        -------
        bool
            True if the progress bar thread has been stopped, False otherwise.
        """
        return self._stop_event.is_set()
    
    def update_progress(self):
        """
        Updates the progress bar's visual representation and the associated task text.

        This method calculates the current progress based on the completed and total tasks,
        updates the progress bar's position, and updates the task's description text.

        Returns
        -------
        None
        """
        if self.progress_bar.get() <= 1:
            self.progress_bar.set((self.completed_tasks / self.total_tasks))
            self.update_progress_stringvar(self.task)
        self.app.update()
    
    def update_progress_stringvar(self, taskname):
        """
        Updates the displayed progress text with the current task and percentage of completion.

        This method updates the `progress_stringvar` with a message showing the current progress
        percentage, the task name, and the number of completed tasks relative to the total tasks.

        Parameters
        ----------
        taskname : str
            The name of the current task being displayed in the progress window.

        Returns
        -------
        None
        """
        percent = round(self.progress_bar.get() * 100, 2)
        if self.completed_tasks == self.total_tasks:
            self.progress_stringvar.set(f"Processing finished. {percent}% "
                                        f"({int(self.completed_tasks)}/{int(self.total_tasks)})\nYou can close this window.")
        else:
            self.progress_stringvar.set(f"Current Progress: {percent}%\n"
                                        f"{taskname}\n({int(self.completed_tasks)}/{int(self.total_tasks)})\n\nDo not close this window.")
    
    def increment_progress(self, n=1):
        """
        Increments the number of completed tasks and updates the progress bar.

        This method increments the `completed_tasks` by the specified number (default is 1)
        and updates the progress bar accordingly.

        Parameters
        ----------
        n : int, optional
            The number of tasks to increment (default is 1).

        Returns
        -------
        self : ProgressBar
            The updated instance of the `ProgressBar` class for chaining.
        """
        self.completed_tasks = self.completed_tasks + n
        self.update_progress()
        return self
    
    def update_task(self, task):
        """
        Updates the current task name displayed in the progress window.

        This method updates the `task` string with the given task name and triggers an update of the progress.

        Parameters
        ----------
        task : str
            The name of the task to display in the progress window.

        Returns
        -------
        self : ProgressBar
            The updated instance of the `ProgressBar` class for chaining.
        """
        self.task = task
        self.update_progress()
        return self

