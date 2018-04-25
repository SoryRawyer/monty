"""
playback.py : take 2 at trying to play audio, this time trying to divide the audio
parts from the cli parts
"""

import vlc

class Player(object):
    """
    Player : play a file using vlc
    """

    def __init__(self, file_location=''):
        self.vlc_instance = vlc.Instance()
        if file_location:
            self.media = self.vlc_instance.media_new_path(file_location)
            self.player = self.media.player_new_from_media()

    def play(self):
        """
        play: start the pyaudio stream

        TODO: should probably check if the stream's open first
        """
        if self.player:
            self.player.play()
        else:
            raise NoAvailableMediaException('Tried to play but you have no media player')

    def pause(self):
        """
        pause: stop the pyaudio stream

        TODO: should probably check if the stream's open first
        """
        if self.player:
            self.player.pause()
        else:
            raise NoAvailableMediaException('Tried to pause but you have no media player')

    def stop(self):
        """
        stop: stop the pyaudio stream and close it

        TODO: should probably check if the stream's open first
        """
        if self.player:
            self.player.stop()
        else:
            raise NoAvailableMediaException('Tried to stop but you have no media player')

    def change_song(self, new_song_location):
        """
        change_song: create a new vlc media player for this song
        """
        was_playing = False
        if self.is_playing():
            was_playing = True
        self.media = self.vlc_instance.media_new_path(new_song_location)
        self.player = self.media.player_new_from_media()
        if was_playing:
            self.play()

    def is_playing(self):
        """
        is_playing: check to see if the audio stream is playing music
        """
        return self.player.is_playing()

class NoAvailableMediaException(Exception):
    """
    NoAvailableMediaException : an exception for when there's just no more media to play
    """
    pass
