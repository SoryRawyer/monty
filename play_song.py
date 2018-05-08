"""
play_song.py : try to play a song through vlc. try to handle play/pause keystrokes
"""

import argparse
import logging
import os
import signal
import sys
import trio

from monty.playback import Player
from monty.tracklist import TrackList
from monty.keyboard import MediaKeyListener
from monty.gui import PlayerGUI
import monty.config as config

sh = logging.StreamHandler(sys.stdout)
logger = logging.getLogger(__name__)
logger.addHandler(sh)

def make_track_queue_from_song(artist, album, song) -> TrackList:
    """
    make_track_queue_from_song : given an artist, album, and song, create a tracklist
    containing all the songs from the album
    """
    media_dir = config.media_dir
    search_dir = os.path.join(media_dir, artist, album)

    songs = []
    song_position = 0
    i = 0
    for filename in os.listdir(search_dir):
        # for filename in filenames:
        if filename.startswith(song):
            song_position = i
        songs.append(os.path.join(search_dir, filename))
        i += 1

    return TrackList(songs, song_position)

async def main(args):
    """
    main : play some songs
    """
    track_queue = make_track_queue_from_song(args.artist, args.album, args.song)

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
        player.change_song(track_queue.get_next_song())

    def on_previous_track(_):
        """
        on_previous_track : how to react when the previous track media key is pressed
        """
        player.change_song(track_queue.get_previous_song())

    def skip_to_arbitrary_song(song_position):
        """
        skip_to_arbitrary_song : given an index, skip to that position in the tracklist
        """
        player.change_song(track_queue.skip_to_index(song_position))


    def stop_everything(_, __):
        """
        stop_everything: shut everything down
        """
        player.stop()
        listener.stop()
        sys.exit(0)

    listener = MediaKeyListener()
    listener.on_action('play_pause', on_play_or_pause)
    listener.on_action('next_track', on_next_track)
    listener.on_action('previous_track', on_previous_track)
    listener.start()
    player = Player(track_queue.get_current_song())
    player.play()

    signal.signal(signal.SIGTERM, stop_everything)
    signal.signal(signal.SIGINT, stop_everything)

    gui_bindings = {
        'play_pause' : ('<Button-1>', on_play_or_pause),
        'next_track' : ('<Button-1>', on_next_track),
        'previous_track' : ('<Button-1>', on_previous_track),
        'text' : ('<Double-Button-1>', skip_to_arbitrary_song),
    }
    gui = PlayerGUI.new(gui_bindings)
    gui.add_tracks_to_listbox(track_queue.song_locations)

    async with trio.open_nursery() as nursery:
        nursery.start_soon(gui.launch_gui)

    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('artist', type=str)
    parser.add_argument('album', type=str)
    parser.add_argument('song', type=str)
    trio.run(main, parser.parse_args())
