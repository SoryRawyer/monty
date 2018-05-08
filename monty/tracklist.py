"""
tracklist.py : a tracklist class for playing audio
"""

class TrackList(object):
    """
    TrackList : a list of songs and their locations
    """
    def __init__(self, song_locations, position=0):
        if position < 0 or position > len(song_locations):
            raise NoAvailableSongException('position in track list ' +
                                           'cannot be greater than the list of songs')
        self.song_locations = song_locations
        self.position = position

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
        update the current position to reflect the track change
        """
        if self.position == len(self.song_locations):
            raise NoAvailableSongException('no more songs')
        self.position += 1
        return self.song_locations[self.position]

    def get_previous_song(self) -> str:
        """
        get_previous_song : return the location of the previous song in the track list
        If we're at the first track, rais an exception
        update the current position to reflect the track change
        """
        if self.position == 0:
            raise NoAvailableSongException('no more songs')
        self.position -= 1
        return self.song_locations[self.position]

    def get_current_song(self) -> str:
        """
        get_current_song : return the location of the song we're currently playing
        """
        return self.song_locations[self.position]

    def skip_to_index(self, index: int):
        """
        skip_to_index : skip to a given index
        """
        if index < 0 or index >= len(self.song_locations):
            raise NoAvailableSongException('cannot skip to index {}'.format(index))
        self.position = index
        return self.song_locations[self.position]


class NoAvailableSongException(Exception):
    """
    NoAvailableSongException : generic exception to be raised when there is no song
    to return
    """
    pass
