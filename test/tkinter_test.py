"""
tkinter_test.py : testing out some tkinter stuff
"""

import time
import tkinter as tk
import tkinter.scrolledtext as tkst
from tkinter import ttk

class TestPlayerGUI(tk.Frame):
    """
    TestPlayerGUI : test out some tkinter stuff
    """

    def __init__(self, master=None):
        super().__init__(master)
        self.mainframe = ttk.Frame(master, padding='3 3 12 12')
        self.mainframe.grid(column=0, row=0, sticky=(tk.N, tk.E, tk.S, tk.W))
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)
        self.populate_screen()
        for chil in self.mainframe.winfo_children():
            chil.grid_configure(padx=5, pady=5)

    def populate_screen(self):
        self.quit = ttk.Button(self.mainframe, text='QUIT', command=self.master.destroy)
        self.quit.grid(column=1, row=3)
        self.b1 = ttk.Button(self.mainframe, text='button 1')
        self.b1.grid(column=0, row=1)
        self.b2 = ttk.Button(self.mainframe, text='button 2')
        self.b2.grid(column=1, row=1)
        self.b3 = ttk.Button(self.mainframe, text='button 3')
        self.b3.grid(column=2, row=1)
        self.text = tk.Listbox(self.mainframe, height=5)
        for i in range(0, 40):
            self.text.insert('end', i)
        self.text.activate(5)


if __name__ == '__main__':
    root = tk.Tk()
    player = TestPlayerGUI(root)
    root.mainloop()
