"""
app.py : toga GUI
"""

from typing import Optional

import toga
from toga.style import Pack
from toga.constants import COLUMN, ROW

from monty import Database, Player, TrackList, CloudStorage

class MontyPlayer(toga.App):
    """
    MontyPlayer : a toga GUI to work with briefcase and beeware
    """

    def get_selected_track_position(self) -> Optional[int]:
        """
        get_selected_track_position : return selected position if there is one
        """
        if self.table.selection:
            return self.table.selection.position
        return None

    def on_play_or_pause(self, _):
        """
        on_play_or_pause : how to react when the play/pause media key is pressed
        """
        if self.player.is_playing():
            self.player.pause()
        else:
            if self.table.selection and self.table.selection.position != self.track_list.position:
                next_song = self.track_list.skip_to_index(self.table.selection.position)
                self.player.change_song(next_song)
            self.player.play()

    def on_next_track(self, _):
        """
        on_next_track : how to react when the next track media key is pressed
        """
        self.player.change_song(self.track_list.get_next_song())

    def on_previous_track(self, _):
        """
        on_previous_track : how to react when the previous track media key is pressed
        """
        self.player.change_song(self.track_list.get_previous_song())

    def skip_to_arbitrary_song(self, song_position: int):
        """
        skip_to_arbitrary_song : given an index, skip to that position in the tracklist
        """
        self.player.change_song(self.track_list.skip_to_index(song_position))

    def download_track(self, _):
        """
        download_track : given an index, download the track at that position in the track list
        """
        song_position = self.get_selected_track_position()
        track = self.track_list.song_metadata[song_position]
        self.cloud.get_recording(track.artist_id,
                                  track.release_id,
                                  track.recording_id,
                                  track.file_format)

    def print_selection(self, _):
        """print_selection: for general debugging purposes"""
        try:
            if self.table.selection:
                print(self.table.selection.position)
        except AttributeError:
            print('there\'s no such thing as a table selection!')

    def startup(self):
        """
        startup : toga's way of initializing the GUI
        """
        # initialize db connection and get track list
        self.db = Database()
        self.tracks = list(self.db.generate_all_track_info())
        table_data = [{
            'position' : idx,
            'artist' : track.artist,
            'album' : track.album,
            'track' : track.track_title,
        }
                      for (idx, track)
                      in enumerate(self.tracks)]
        self.track_list = TrackList(self.tracks)
        self.player = Player(self.track_list.get_current_song())
        self.cloud = CloudStorage()

        # set a placeholder for "now playing" kind of info
        self.label = toga.Label('Welcome to Monty!')

        self.previous = toga.Button('previous', on_press=self.on_previous_track)
        self.play_pause = toga.Button('play_pause', on_press=self.on_play_or_pause)
        self.next = toga.Button('next', on_press=self.on_next_track)
        self.print_button = toga.Button('print', on_press=self.print_selection)
        self.download = toga.Button('download', on_press=self.download_track)
        audio_buttons = toga.Box(
            children=[self.previous, self.play_pause, self.next, self.print_button, self.download,],
            style=Pack(
                flex=1,
                direction=ROW,
                padding=10,
            ),
        )

        table_headings = ['artist', 'album', 'track']
        self.table = toga.Table(table_headings, data=table_data)
        self.outer_box = toga.Box(
            children=[self.label, audio_buttons, self.table,],
            style=Pack(
                flex=1,
                direction=COLUMN,
                padding=10,
            )
        )

        self.main_window = toga.MainWindow(title=self.name)
        self.main_window.content = self.outer_box
        self.main_window.show()

def main():
    """
    main : return a monty player
    """
    return MontyPlayer('Monty', 'biz.sory.monty')
