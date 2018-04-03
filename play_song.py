"""
play_song.py : try to play a song through vlc. try to handle play/pause keystrokes
"""

import argparse
import logging
import os
import select
import sys
import time
import vlc
from collections import namedtuple
from mp3_tagger import MP3File
from pynput import keyboard

MEDIA_DIR = '/Users/rorysawyer/media/audio'

sh = logging.StreamHandler(sys.stdout)
logger = logging.getLogger(__name__)
logger.addHandler(sh)

class Player:
    """
    Player : a list of songs and their locations
    """
    def __init__(self, song_locations=[], position=0):
        self.song_locations = song_locations
        self.position = position
        self.vlc_intance = vlc.Instance()
        self.media_player = self.vlc_intance.media_player_new()
    
    def enqueue_song(self, song):
        """
        enqueue_song : add a song file to the queue
        """
        self.song_locations.append(song)
    
    def enqueue_song_at_front(self, song):
        """
        enqueue_song_at_front : add a song file to the queue such that it's the next
        song returned by get_next_song
        """
        self.song_locations.insert(self.position, song)
    
    def get_next_song(self) -> str:
        """
        get_next_song : return the location of the next song file to play
        If there are no more songs to play, raise an exception
        """
        if self.position == len(self.song_locations):
            raise Exception('no more songs')
        self.position += 1
        return self.song_locations[self.position]
    
    def get_previous_song(self) -> str:
        if self.position == 0:
            raise Exception('no more songs')
        self.position -= 1
        return self.song_locations[self.position]
    
    def play(self):
        if self.media_player.is_playing() == 0:
            self.media_player.play()
        return

    def pause(self):
        if self.media_player.is_playing() == 1:
            self.media_player.pause()
        return
    
    def is_playing(self):
        if self.media_player.is_playing() == 1:
            return True
        return False
    
    def play_previous_song(self):
        location = self.get_previous_song()
        self.media_player = vlc.MediaPlayer(location)
        self.media_player.play()
        return
    
    def play_next_song(self):
        location = self.get_next_song()
        self.media_player = vlc.MediaPlayer(location)
        self.media_player.play()
        return

def make_track_queue_from_song(artist, album, song) -> Player:
    SongAndPosition = namedtuple('song_location', 'track_number')
    search_dir = os.path.join(MEDIA_DIR, artist, album)

    songs = []
    song_position = 0
    for filenames in os.listdir(os.path.join(MEDIA_DIR, artist, album)):
        for filename in filenames:
            mp3 = MP3File(os.path.join(search_dir, filename))
            track_number = mp3.get_tags()['ID3TagV1']['track']
            if filename.startswith(song):
                song_position = track_number
            songs.append(SongAndPosition(filename, track_number))

    songs.sort(lambda x: x.track_number)
    song_locations = [x.song_location for x in songs]

    return Player(song_locations, song_position)

def main(args):
    tq = make_track_queue_from_song(args.artist, args.album, args.song)
    tq.play()
    def on_press(key):
        logger.info(key)
        if key == keyboard.Key.space:
            if tq.is_playing() == 1:
                tq.pause()
            else:
                tq.play()
        if key == keyboard.Key.left:
            # if at first track, do nothing
            # if position is < 1%:
            #   return to the previous song
            # if position is >= 1%:
            #   restart the current song
            try:
                tq.play_previous_song()
            except Exception:
                print('You\'re already at the beginning!')
        if key == keyboard.Key.right:
            try:
                tq.play_next_song()
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
