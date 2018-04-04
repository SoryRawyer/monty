"""
playback.py : take 2 at trying to play audio, this time trying to divide the audio
parts from the cli parts
"""

import os
import pyaudio
from pydub import AudioSegment

class Player(object):
    """
    Player : play a file using pydub and pyaudio
    """

    def __init__(self, file_location):
        self.song = Player._open_audio_file(file_location)
        self.paudio = pyaudio.PyAudio()
        self.callback_position = 0
        self.stream = self.paudio.open(format=self.paudio.get_format_from_width(self.song.sample_width),
                                  channels=self.song.channels,
                                  rate=self.song.frame_rate,
                                  output=True,
                                  stream_callback=self._pyaudio_callback)

    def _pyaudio_callback(self, in_data, frame_count, time_info, status_flags):
        """
        return frame_count * channels * bytes-per-channel
        AudioSegments are slicable using milliseconds.
        |  for example:
        |      a = AudioSegment.from_mp3(mp3file)
        |      first_second = a[:1000] # get the first second of an mp3
        |      slice = a[5000:10000] # get a slice from 5 to 10 seconds of an mp3
        """
        data_len = frame_count * self.song.channels * self.song.sample_width
        flag = pyaudio.paContinue
        if self.callback_position + data_len >= len(self.song._data):
            data_len = len(self.song._data) - self.callback_position - 1
            flag = pyaudio.paComplete
        self.callback_position += data_len
        return self.song._data[self.callback_position:self.callback_position + data_len], flag
    
    def play(self):
        self.stream.start_stream()
    
    def pause(self):
        self.stream.stop_stream()
    
    def stop(self):
        self.stream.stop_stream()
        self.callback_position = 0
        self.stream.close()
    
    def change_song(self, new_song_location):
        was_playing = self.stream.is_active()
        self.song = Player._open_audio_file(new_song_location)
        self.stream.stop_stream()
        self.stream.close()
        self.stream = self.paudio.open(format=self.paudio.get_format_from_width(self.song.sample_width),
                                  channels=self.song.channels,
                                  rate=self.song.frame_rate,
                                  output=True,
                                  stream_callback=self._pyaudio_callback)
        self.callback_position = 0
        if was_playing:
            self.stream.start_stream()
        
    def is_playing(self):
        return self.stream.is_active()
    
    @staticmethod
    def _open_audio_file(file_location):
        _, extension = os.path.splitext(file_location)
        song = AudioSegment.from_file(file_location, format=extension.replace('.', ''))
        return song
