"""
tracklist.py : a tracklist class for playing audio
"""

import os
from typing import List

from monty.cloud import CloudStorage
from monty.metadata import Metadata

class TrackList(object):
    """
    TrackList : a list of songs and their locations
    """
    def __init__(self, song_metadata: List[Metadata], position=0):
        if position < 0 or position > len(song_metadata):
            raise NoAvailableSongException('position in track list ' +
                                           'cannot be greater than the list of songs')
        self.song_metadata = song_metadata
        self.position = position
        self.cloud = CloudStorage()

    def enqueue_song(self, song):
        """
        enqueue_song : add a song file to the queue
        """
        self.song_metadata.append(song)

    def enqueue_song_at_front(self, song):
        """
        enqueue_song_at_front : add a song file to the queue such that it's the next
        song returned by get_next_song
        """
        self.song_metadata.insert(self.position, song)

    def get_next_song(self) -> str:
        """
        get_next_song : return the location of the next song file to play
        If there are no more songs to play, raise an exception
        update the current position to reflect the track change
        """
        song = self.skip_to_index(self.position + 1)
        return song

    def get_previous_song(self) -> str:
        """
        get_previous_song : return the location of the previous song in the track list
        If we're at the first track, rais an exception
        update the current position to reflect the track change
        """
        song = self.skip_to_index(self.position - 1)
        return song

    def get_current_song(self) -> str:
        """
        get_current_song : return the location of the song we're currently playing
        """
        return self.song_metadata[self.position].get_local_path()

    def skip_to_index(self, index: int) -> str:
        """
        skip_to_index : skip to a given index
        """
        if index < 0 or index >= len(self.song_metadata):
            raise NoAvailableSongException('cannot skip to index {}'.format(index))
        self.position = index
        current_track = self.song_metadata[self.position]
        try:
            os.stat(current_track.get_local_path())
        except FileNotFoundError:
            self.cloud.get_recording(current_track.artist_id,
                                     current_track.release_id,
                                     current_track.recording_id,
                                     current_track.file_format)
        return current_track.get_local_path()


class NoAvailableSongException(Exception):
    """
    NoAvailableSongException : generic exception to be raised when there is no song
    to return
    """
    pass
