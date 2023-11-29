import customtkinter as ctk


def clf_params():
    help_window = ctk.CTkToplevel()
    help_window.title("Learning: classifier parameters")

    help_window.geometry("600x900")
    help_window.resizable(width=False, height=False)

    help_master_frame = ctk.CTkFrame(master=help_window, )
    help_master_frame.place(relwidth=1.0, relheight=1.0)


def load_dataset():
    help_window = ctk.CTkToplevel()
    help_window.title("Learning: load dataset")

    help_window.geometry("600x900")
    help_window.resizable(width=False, height=False)

    help_master_frame = ctk.CTkFrame(master=help_window, )
    help_master_frame.place(relwidth=1.0, relheight=1.0)


def select_targets():
    help_window = ctk.CTkToplevel()
    help_window.title("Learning: select targets")

    help_window.geometry("600x900")
    help_window.resizable(width=False, height=False)

    help_master_frame = ctk.CTkFrame(master=help_window, )
    help_master_frame.place(relwidth=1.0, relheight=1.0)


def training_targets():
    help_window = ctk.CTkToplevel()
    help_window.title("Learning: training targets")

    help_window.geometry("600x900")
    help_window.resizable(width=False, height=False)

    help_master_frame = ctk.CTkFrame(master=help_window, )
    help_master_frame.place(relwidth=1.0, relheight=1.0)


def get_advanced_metrics():
    help_window = ctk.CTkToplevel()
    help_window.title("Learning: get advanced metrics")

    help_window.geometry("600x900")
    help_window.resizable(width=False, height=False)

    help_master_frame = ctk.CTkFrame(master=help_window, )
    help_master_frame.place(relwidth=1.0, relheight=1.0)


def load_clf():
    help_window = ctk.CTkToplevel()
    help_window.title("Learning: load clf")

    help_window.geometry("600x900")
    help_window.resizable(width=False, height=False)

    help_master_frame = ctk.CTkFrame(master=help_window, )
    help_master_frame.place(relwidth=1.0, relheight=1.0)


def save_clf():
    help_window = ctk.CTkToplevel()
    help_window.title("Learning: save classifier")

    help_window.geometry("600x900")
    help_window.resizable(width=False, height=False)

    help_master_frame = ctk.CTkFrame(master=help_window, )
    help_master_frame.place(relwidth=1.0, relheight=1.0)


def advanced_metrics():
    help_window = ctk.CTkToplevel()
    help_window.title("Learning: advanced metrics")

    help_window.geometry("600x900")
    help_window.resizable(width=False, height=False)

    help_master_frame = ctk.CTkFrame(master=help_window, )
    help_master_frame.place(relwidth=1.0, relheight=1.0)
