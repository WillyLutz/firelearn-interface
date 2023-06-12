import pandas as pd
import tkinter as tk


class CustomTable:
    def __init__(self, data: pd.DataFrame, parent: tk.Frame, **kwargs):
        self.options = {}
        self.options.update(**kwargs)
        self.data = data
        self.parent = parent
        self.canvas = tk.Canvas(master=self.parent)

        self.canvas.place(anchor=tk.NW, relx=0, rely=0, relwidth=0.95, relheight=0.95)

        self.data_frame = tk.Frame(master=self.canvas)
        self.data_frame.place(anchor=tk.NW, relx=0, rely=0, relwidth=1, relheight=1)

        self.y_scroll = tk.Scrollbar(master=self.parent, orient='vertical', )
        self.y_scroll.place(anchor=tk.NE, relx=1, rely=0, relwidth=0.05, relheight=0.95)
        self.x_scroll = tk.Scrollbar(master=self.parent, orient='horizontal', )
        self.x_scroll.place(anchor=tk.SW, relx=0, rely=1, relwidth=0.95, relheight=0.05)

        self.canvas.configure(yscrollcommand=self.y_scroll.set, xscrollcommand=self.x_scroll.set)
        self.y_scroll.configure(command=self.canvas.yview)
        self.x_scroll.configure(command=self.canvas.xview)

        # todo : make it so the default position of the scroll bars are top left corner

        self.canvas.create_window(10, 10, window=self.data_frame)
        self.data_frame.bind("<Configure>", self.on_configure)

        self.fill_table()

    def fill_table(self, ):

        columns = self.data.columns
        values = self.data.values
        if len(columns) > 10:
            columns = columns[:10]
        if len(values) > 10:
            values = values[:, :10]
        for c in range(len(columns)):
            label = tk.Label(master=self.data_frame, text=columns[c])
            label.grid(row=0, column=c)

        for r in range(len(values)):
            for c in range(len(columns)):
                label = tk.Label(master=self.data_frame, text=self.data[columns[c]].iloc[r], )
                label.grid(row=r + 1, column=c)

        # todo : test if it is better to display each value as label, or each line as label, or all as single label etc.
        # todo : make it fancy

    def get(self):
        return self.data

    def on_configure(self, event):
        """Set the scroll region to encompass the scrolled frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def update_df(self, dataframe):
        self.data = dataframe
        self.fill_table()
