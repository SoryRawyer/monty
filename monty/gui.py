"""
gui.py : gui for playing the music
"""

import functools
import tkinter as tk
from tkinter import ttk

class PlayerGUI(tk.Frame):
    """
    PlayerGUI : use tkinter to do gui stuff

    Attributes:
        mainframe: the main frame for tkinter
        bindings: function bindings for different gui elements
    """

    def __init__(self, master):
        super().__init__(master)
        self.mainframe = ttk.Frame(master, padding='3 3 12 12')
        self.mainframe.grid(column=0, row=0, sticky=(tk.N, tk.E, tk.S, tk.W))
        self.mainframe.columnconfigure(0, weight=1)
        self.mainframe.rowconfigure(0, weight=1)
        self.bindings = {}
        self.populate_screen()
        for chil in self.mainframe.winfo_children():
            chil.grid_configure(padx=10, pady=10)

    def populate_screen(self):
        """
        populate_screen : add buttons and stuff to the screen
        """
        # buttons for quitting, moving forward/back one song, and playing/pausing current song
        self.quit = ttk.Button(self.mainframe, text='QUIT', command=self.master.destroy)
        self.quit.grid(column=1, row=2)
        self.download = ttk.Button(self.mainframe, text='download')
        self.download.grid(column=0, row=2)
        self.previous_track = ttk.Button(self.mainframe, text='previous track')
        self.previous_track.grid(column=0, row=1)
        self.play_pause = ttk.Button(self.mainframe, text='play/pause')
        self.play_pause.grid(column=1, row=1)
        self.next_track = ttk.Button(self.mainframe, text='next track')
        self.next_track.grid(column=2, row=1)
        # ListBox to show available songs
        self.text = tk.Listbox(self.mainframe, height=10, width=30)
        # if 'text' in self.bindings:
        #     self.text.bind('<Double-Button-1>', self.bindings['text'])
        self.selected_item = None

    def add_tracks_to_listbox(self, tracklist: list):
        """
        add_tracks_to_listbox : take the list of tracks and add them to the listbox
        """
        for track in tracklist:
            self.text.insert('end', track)

    def bind_to(self, button, event, func, override=False):
        """
        bind : bind the given function to the given button
        """
        if button in self.bindings and not override:
            error_msg = 'A binding already exists for {}'.format(button)
            raise BindingAlreadyExistsException(error_msg)
        elif ((button == 'text' and event == '<Double-Button-1>')
              or (button == 'download' and event == '<Button-1>')):
            # if this is the text button, then we need to pass the current selected
            # item to the callback
            func = functools.partial(self.on_text_double_click, func)
        self.bindings[button] = (event, func)
        self.__getattribute__(button).bind(event, func)

    def set_current_selection(self, index):
        """
        set_current_selection : set the current selected item in the list box
        """
        self.text.selection_set(index)

    def get_current_selection(self):
        """
        get_current_selection : get the current selected item in the list box
        """
        return self.text.selection_get()

    def on_text_double_click(self, func, _):
        """
        on_text_double_click : on text double click, call the function with the selected element
        """
        func(self.text.index(tk.ACTIVE))

    def show_error_message(self, message):
        """
        show_error_message : show a popup box with an error message
        """
        tkinter.messagebox.showinfo('bummer', message)

    @staticmethod
    def new(bindings=None):
        """
        new : create a new PlayerGUI
        """
        root = tk.Tk()
        if not bindings:
            bindings = {}
        gui = PlayerGUI(root)
        for button in bindings:
            event, func = bindings[button]
            gui.bind_to(button, event, func)
        return gui

class BindingAlreadyExistsException(Exception):
    """
    BindingAlreadyExistsException : a binding already exists
    """
    pass
