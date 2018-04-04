"""
play_song.py : try to play a song through vlc. try to handle play/pause keystrokes
"""

import argparse
import logging
import os
import sys
from collections import namedtuple

import vlc
from mp3_tagger import MP3File
from pynput import keyboard

from monty.playback import Player
from monty.tracklist import TrackList

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
    def on_press(key):
        """
        on_press : define what happens when certain keys are pressed
        """
        logger.info(key)
        if key == keyboard.Key.space:
            if player.is_playing():
                player.pause()
            else:
                player.play()
        if key == keyboard.Key.left:
            # if at first track, do nothing
            # if position is < 1%:
            #   return to the previous song
            # if position is >= 1%:
            #   restart the current song
            try:
                player.change_song(track_queue.get_previous_song())
            except Exception:
                print('You\'re already at the beginning!')
        if key == keyboard.Key.right:
            try:
                player.change_song(track_queue.get_next_song())
            except Exception:
                print('No more songs to play!')
    with keyboard.Listener(on_press=on_press) as listener:
        print('Now playing: {} by {}, from the album {}'.format(args.song, args.artist, args.album))
        listener.join()
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('artist', type=str)
    parser.add_argument('album', type=str)
    parser.add_argument('song', type=str)
    main(parser.parse_args())
