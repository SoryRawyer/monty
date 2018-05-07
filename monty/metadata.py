"""
metadata.py : get information about a file
"""

import os
from mutagen import mp3, flac

class Metadata(object):
    """
    Metadata : return information about a track
    """

    def __init__(self, file_path):
        self.file_path = file_path
        _, extension = os.path.splitext(file_path)
        if extension == '.mp3':
            self._metadata = mp3.EasyMP3(file_path)
        elif extension == '.flac':
            self._metadata = flac.FLAC(file_path)
        else:
            raise FormatNotImplemented('Extension {} not supported'.format(extension))

        self.artist = self._metadata['artist'][0]
        self.album = self._metadata['album'][0]
        self.track_title = self._metadata['title'][0]
        self.track_number = int(self._metadata['tracknumber'][0].split('/')[0])

class FormatNotImplemented(Exception):
    """
    FormatNotImplemented : exception for filetypes not supported by the Metadata class
    """
    pass
