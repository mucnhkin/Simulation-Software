import tkinter as tk

class Frame1(tk.Frame):
    def __init__(self, parent, color):
        tk.Frame.__init__(self, parent, bg=f'{color}')
        self.parent = parent

