"""
play_song.py : try to play a song through vlc. try to handle play/pause keystrokes
"""

import logging
import signal
import sys

import google

from gui import PlayerGUI
from monty import Database, Player, TrackList
from monty.cloud import get_remote_storage, NoStorageConnectionException

SH = logging.StreamHandler(sys.stdout)
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(SH)

def main():
    """
    main : play some songs
    """
    client = get_remote_storage()

    # A bunch of callback functions for keyboard/gui events
    def on_play_or_pause(_):
        """
        on_play_or_pause : how to react when the play/pause media key is pressed
        """
        if player.is_playing():
            player.pause()
        else:
            player.play()

    def on_next_track(_):
        """
        on_next_track : how to react when the next track media key is pressed
        """
        player.change_song(track_list.get_next_song())

    def on_previous_track(_):
        """
        on_previous_track : how to react when the previous track media key is pressed
        """
        player.change_song(track_list.get_previous_song())

    def skip_to_arbitrary_song(song_position: int):
        """
        skip_to_arbitrary_song : given an index, skip to that position in the tracklist
        """
        player.change_song(track_list.skip_to_index(song_position))

    def download_track(song_position):
        """
        download_track : given an index, download the track at that position in the track list
        """
        # TODO: use threading to avoid blocking the gui on long-running background tasks

        try:
            track = track_list.song_metadata[song_position]
        except IndexError:
            gui.show_error_message('No song selected')
            return

        try:
            client.get_recording(track.artist_id,
                                track.release_id,
                                track.recording_id,
                                track.file_format)
        except NoStorageConnectionException:
            gui.show_error_message('Unable to connect to the remote tunes. Sorry')

    def stop_everything(_, __):
        """
        stop_everything: shut everything down
        """
        player.stop()
        sys.exit(0)

    db = Database()
    # how should this work? db returns metadata objects?
    tracks = list(db.generate_all_track_info())
    track_list = TrackList(tracks)

    player = Player()

    signal.signal(signal.SIGTERM, stop_everything)
    signal.signal(signal.SIGINT, stop_everything)

    gui_bindings = {
        'play_pause' : ('<Button-1>', on_play_or_pause),
        'next_track' : ('<Button-1>', on_next_track),
        'previous_track' : ('<Button-1>', on_previous_track),
        'text' : ('<Double-Button-1>', skip_to_arbitrary_song),
        'download' : ('<Button-1>', download_track),
    }
    gui = PlayerGUI.new(gui_bindings)
    gui.add_tracks_to_listbox([track.get_display_string() for track in tracks])
    gui.master.mainloop()

    return

if __name__ == '__main__':
    main()
