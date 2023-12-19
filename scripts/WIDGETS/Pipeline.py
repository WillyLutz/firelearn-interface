import tkinter as tk
import customtkinter as ctk
from numpy import ceil


class Pipeline():
    def __init__(self, master: ctk.CTkCanvas,
                 x=0,
                 y=0,
                 width=100,
                 height=200,
                 outline='black',
                 background='gray',
                 corner_radius=60,
                 linewidth=10,
                 **kwargs):
        self.master = master
        
        self.x = x + ceil(linewidth/2) if linewidth else x
        self.y = y + ceil(linewidth/2) if linewidth else y
        self.width = width
        self.height = height
        self.xf = x + width - ceil(linewidth/2) if linewidth else x + width
        self.yf = y + height - ceil(linewidth/2) if linewidth else y + width
        self.outline = outline
        self.background = background
        self.corner_radius = corner_radius
        self.linewidth = linewidth
        
        self.draw()
        
        self.text = []
        self.strvar = tk.StringVar(value="This is the\ndefault text")
        self.label = ctk.CTkLabel(self.master, textvariable=self.strvar, fg_color="transparent")
        self.label.place(relx=0.5, rely=0.5, anchor=ctk.CENTER, )
    def draw(self):
        # fill with color
        c = 2 * self.corner_radius
        # angles
        self.master.create_arc(self.xf - c, self.y,
                               self.xf, self.y + c,
                               width=0, style='pieslice', fill=self.background,
                               start=0, extent=90)  # top right corner
        self.master.create_arc(self.x, self.y,
                               self.x + c, self.y + c,
                               width=0, style='pieslice', fill=self.background,
                               start=90, extent=90)  # top left corner
        self.master.create_arc(self.x, self.yf - c,
                               self.x + c, self.yf,
                               width=0, style='pieslice', fill=self.background,
                               start=180, extent=90)  # bottom left corner
        self.master.create_arc(self.xf - c, self.yf - c,
                               self.xf, self.yf,
                               width=0, style='pieslice', fill=self.background,
                               start=270, extent=90)  # bottom right corner
        # center
        self.master.create_polygon((self.x, self.y+self.corner_radius,
                                    self.x+self.corner_radius, self.y,
                                    self.xf-self.corner_radius, self.y,
                                    self.xf, self.y+self.corner_radius,
                                    self.xf, self.yf-self.corner_radius,
                                    self.xf-self.corner_radius, self.yf,
                                    self.x+self.corner_radius, self.yf,
                                    self.x, self.yf-self.corner_radius,),
                                   width=0,
                                   fill=self.background,
                                   )
        
        # manage borders
        self.master.create_line(self.x + self.corner_radius, self.y,
                                self.xf - self.corner_radius, self.y,
                                fill=self.outline, width=self.linewidth)  # h1
        self.master.create_line(self.x + self.corner_radius, self.yf,
                                self.xf - self.corner_radius, self.yf,
                                fill=self.outline, width=self.linewidth)  # h2
        self.master.create_line(self.x, self.y + self.corner_radius,
                                self.x, self.yf - self.corner_radius,
                                fill=self.outline, width=self.linewidth)  # v1
        self.master.create_line(self.xf, self.y + self.corner_radius,
                                self.xf, self.yf - self.corner_radius,
                                fill=self.outline, width=self.linewidth)  # v2
        
        self.master.create_arc(self.xf-2*self.corner_radius, self.y,
                               self.xf, self.y+2*self.corner_radius,
                               width=self.linewidth, style='arc', outline=self.outline,
                               start=0, extent=90)  # top right corner
        self.master.create_arc(self.x, self.y,
                               self.x+2*self.corner_radius, self.y + c,
                               width=self.linewidth, style='arc', outline=self.outline,
                               start=90, extent=90)  # top left corner
        self.master.create_arc(self.x, self.yf-2*self.corner_radius,
                               self.x + c, self.yf,
                               width=self.linewidth, style='arc', outline=self.outline,
                               start=180, extent=90)  # bottom left corner
        self.master.create_arc(self.xf-2*self.corner_radius, self.yf - c,
                               self.xf, self.yf,
                               width=self.linewidth, style='arc', outline=self.outline,
                               start=270, extent=90)  # bottom right corner
        
        
        
