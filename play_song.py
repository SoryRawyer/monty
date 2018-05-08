"""
play_song.py : try to play a song through vlc. try to handle play/pause keystrokes
"""

import logging
import os
import signal
import sys
import trio

from monty.db import Database
from monty.playback import Player
from monty.tracklist import TrackList
from monty.keyboard import MediaKeyListener
from monty.gui import PlayerGUI
import monty.config as config

sh = logging.StreamHandler(sys.stdout)
logger = logging.getLogger(__name__)
logger.addHandler(sh)

async def main(args=None):
    """
    main : play some songs
    """

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

    def skip_to_arbitrary_song(song_position):
        """
        skip_to_arbitrary_song : given an index, skip to that position in the tracklist
        """
        player.change_song(track_list.skip_to_index(song_position))


    def stop_everything(_, __):
        """
        stop_everything: shut everything down
        """
        player.stop()
        listener.stop()
        sys.exit(0)

    db = Database()
    tracks = list(db.generate_all_track_info())
    track_list = TrackList([x[4] for x in tracks])
    track_display_format = '{} - {} - {}'

    listener = MediaKeyListener()
    listener.on_action('play_pause', on_play_or_pause)
    listener.on_action('next_track', on_next_track)
    listener.on_action('previous_track', on_previous_track)
    listener.start()
    player = Player(track_list.get_current_song())

    signal.signal(signal.SIGTERM, stop_everything)
    signal.signal(signal.SIGINT, stop_everything)

    gui_bindings = {
        'play_pause' : ('<Button-1>', on_play_or_pause),
        'next_track' : ('<Button-1>', on_next_track),
        'previous_track' : ('<Button-1>', on_previous_track),
        'text' : ('<Double-Button-1>', skip_to_arbitrary_song),
    }
    gui = PlayerGUI.new(gui_bindings)
    gui.add_tracks_to_listbox([track_display_format.format(x[0], x[1], x[2]) for x in tracks])

    async with trio.open_nursery() as nursery:
        nursery.start_soon(gui.launch_gui)

    return

if __name__ == '__main__':
    trio.run(main)
