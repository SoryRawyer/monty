"""
play_song.py : try to play a song through vlc. try to handle play/pause keystrokes
"""

import argparse
import logging
import os
import signal
import sys
import time
from collections import namedtuple

from mp3_tagger import MP3File

from monty.playback import Player
from monty.tracklist import TrackList
from monty.keyboard import MediaKeyListener

MEDIA_DIR = '/Users/rorysawyer/media/audio'

sh = logging.StreamHandler(sys.stdout)
logger = logging.getLogger(__name__)
logger.addHandler(sh)

def make_track_queue_from_song(artist, album, song) -> TrackList:
    """
    make_track_queue_from_song : given an artist, album, and song, create a tracklist
    containing all the songs from the album
    """
    song_and_position = namedtuple('song_location', 'track_number')
    search_dir = os.path.join(MEDIA_DIR, artist, album)

    songs = []
    song_position = 0
    for filenames in os.listdir(os.path.join(MEDIA_DIR, artist, album)):
        for filename in filenames:
            mp3 = MP3File(os.path.join(search_dir, filename))
            track_number = mp3.get_tags()['ID3TagV1']['track']
            if filename.startswith(song):
                song_position = track_number
            songs.append(song_and_position(filename, track_number))

    songs.sort(lambda x: x.track_number)
    song_locations = [x.song_location for x in songs]

    return TrackList(song_locations, song_position)

def main(args):
    """
    main : play some songs
    """
    # track_queue = make_track_queue_from_song(args.artist, args.album, args.song)
    song_location = os.path.join(MEDIA_DIR, args.artist, args.album, args.song)
    track_queue = TrackList([song_location])
    player = Player(track_queue.get_current_song())
    player.play()

    def on_play_or_pause():
        """
        on_play_or_pause : how to react when the play/pause media key is pressed
        """
        if player.is_playing():
            player.pause()
        else:
            player.play()
        
    def on_next_track():
        """
        on_next_track : how to react when the next track media key is pressed
        """
        player.change_song(track_queue.get_next_song())

    def on_previous_track():
        """
        on_previous_track : how to react when the previous track media key is pressed
        """
        player.change_song(track_queue.get_previous_song())
    
    def stop_everything(signum, frame):
        player.stop()
        listener.stop()
        sys.exit(0)

    listener = MediaKeyListener()
    listener.on('play_pause', on_play_or_pause)
    listener.on('next_track', on_next_track)
    listener.on('prev_track', on_previous_track)
    listener.start()

    signal.signal(signal.SIGTERM, stop_everything)
    signal.signal(signal.SIGINT, stop_everything)

    while True:
        time.sleep(5)
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('artist', type=str)
    parser.add_argument('album', type=str)
    parser.add_argument('song', type=str)
    main(parser.parse_args())
