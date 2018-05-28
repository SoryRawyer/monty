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
        self._file_format = extension.replace('.', '')

        # musicbrainz fields
        self.artist_id = None
        self.release_id = None
        self.recording_id = None

    def set_format(self, file_format):
        """
        set_format : validate format before setting it
        """
        if (file_format != 'mp3' and file_format != 'flac'):
            raise FormatNotImplemented('File format {} not supported'.format(file_format))
        self._file_format = file_format

    file_format = property(fset=set_format)

class FormatNotImplemented(Exception):
    """
    FormatNotImplemented : exception for filetypes not supported by the Metadata class
    """
    pass
