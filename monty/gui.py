"""
gui.py : gui for playing the music
"""

import tkinter as tk
from tkinter import ttk

class PlayerGUI(tk.Frame):
    """
    PlayerGUI : use tkinter to do gui stuff

    Attributes:
        mainframe: the main frame for tkinter
        bindings: function bindings for different gui elements
    """

    def __init__(self, master, bindings):
        super().__init__(master)
        self.mainframe = ttk.Frame(master, padding='3 3 12 12')
        self.mainframe.grid(column=0, row=0, sticky=(tk.N, tk.E, tk.S, tk.W))
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)
        self.populate_screen()
        self.bindings = bindings
        for chil in self.mainframe.winfo_children():
            chil.grid_configure(padx=10, pady=10)

    def populate_screen(self):
        """
        populate_screen : add buttons and stuff to the screen
        """
        self.quit = ttk.Button(self.mainframe, text='QUIT', command=self.master.destroy)
        self.quit.grid(column=1, row=2)
        self.previous_track = ttk.Button(self.mainframe, text='previous track')
        self.previous_track.grid(column=0, row=1)
        self.play_pause = ttk.Button(self.mainframe, text='play/pause')
        self.play_pause.grid(column=1, row=1)
        self.next_track = ttk.Button(self.mainframe, text='next track')
        self.next_track.grid(column=2, row=1)
        self.text = tk.Listbox(self.mainframe, height=10)

    async def launch_gui(self):
        """
        launch_gui : start the mainloop
        """
        self.master.mainloop()

    def add_tracks_to_listbox(self, tracklist: list):
        """
        add_tracks_to_listbox : take the list of tracks and add them to the listbox
        """
        for track in tracklist:
            self.text.insert('end', track)

    def bind_to(self, button, func, override=False):
        """
        bind : bind the given function to the given button
        """
        if button in self.bindings and not override:
            raise BindingAlreadyExistsException('A binding already exists for this button '
                                                + 'and you did not specify to override the handler')
        self.bindings[button] = func
        self.__getattribute__(button).bind('<Button-1>', func)

    @staticmethod
    def new():
        """
        new : create a new PlayerGUI
        """
        root = tk.Tk()
        bindings = {}
        return PlayerGUI(root, bindings)

class BindingAlreadyExistsException(Exception):
    """
    BindingAlreadyExistsException : a binding already exists
    """
    pass
