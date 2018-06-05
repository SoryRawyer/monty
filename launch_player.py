"""
play_song.py : try to play a song through vlc. try to handle play/pause keystrokes
"""

import logging
import signal
import sys
import trio

from monty import Database, Player, PlayerGUI, TrackList

SH = logging.StreamHandler(sys.stdout)
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(SH)

async def main():
    """
    main : play some songs
    """

    # A bunch of callback functions for keyboard/gui events
    async def on_play_or_pause():
        """
        on_play_or_pause : how to react when the play/pause media key is pressed
        """
        while True:
            await play_pause_queue.get()
            print('hi')
            if player.is_playing():
                player.pause()
            else:
                player.play()

    async def on_next_track():
        """
        on_next_track : how to react when the next track media key is pressed
        """
        while True:
            await next_track_queue.get()
            player.change_song(track_list.get_next_song())

    async def on_previous_track():
        """
        on_previous_track : how to react when the previous track media key is pressed
        """
        while True:
            await previous_track_queue.get()
            player.change_song(track_list.get_previous_song())

    async def skip_to_arbitrary_song():
        """
        skip_to_arbitrary_song : given an index, skip to that position in the tracklist
        """
        while True:
            song_position = await seek_queue.get()
            song_location = await track_list.skip_to_index(song_position)
            player.change_song(song_location)

    def stop_everything(_, __):
        """
        stop_everything: shut everything down
        """
        player.stop()
        sys.exit(0)

    db = await Database.new()
    # how should this work? db returns metadata objects?
    tracks = list(db.generate_all_track_info())
    track_list = TrackList(tracks)

    player = Player(track_list.get_current_song())

    signal.signal(signal.SIGTERM, stop_everything)
    signal.signal(signal.SIGINT, stop_everything)

    play_pause_queue = trio.Queue(1)
    next_track_queue = trio.Queue(1)
    previous_track_queue = trio.Queue(1)
    seek_queue = trio.Queue(1)

    gui_bindings = {
        'play_pause' : ('<Button-1>', play_pause_queue),
        'next_track' : ('<Button-1>', next_track_queue),
        'previous_track' : ('<Button-1>', previous_track_queue),
        'text' : ('<Double-Button-1>', seek_queue),
    }
    gui = PlayerGUI.new(gui_bindings)
    gui.add_tracks_to_listbox([track.get_display_string() for track in tracks])

    async with trio.open_nursery() as nursery:
        nursery.start_soon(gui.launch_gui)
        nursery.start_soon(skip_to_arbitrary_song)
        nursery.start_soon(on_play_or_pause)
        nursery.start_soon(on_next_track)
        nursery.start_soon(on_previous_track)

    return

if __name__ == '__main__':
    trio.run(main)
