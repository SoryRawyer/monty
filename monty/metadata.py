"""
metadata.py : get information about a file
"""

import os
from mutagen import mp3, flac
import monty.config as config

FORMAT_PARSERS = {
    'mp3' : mp3.EasyMP3,
    'flac' : flac.FLAC,
}

class Metadata(object):
    """
    Metadata : return information about a track
    """

    def __init__(self, file_path=None):
        if file_path:
            self.file_path = file_path
            self.set_metadata_from_file()

        # musicbrainz fields
        self.artist_id = None
        self.release_id = None
        self.recording_id = None

        self.display_format = '{} - {} - {}'
        self.basename_format = '{}.{}'

    def set_metadata_from_file(self):
        """
        set_metadata_from_file : fill out metadata fields based on input file path
        """
        _, extension = os.path.splitext(self.file_path)
        extension = extension.replace('.', '').lower()
        if extension not in FORMAT_PARSERS:
            raise FormatNotImplemented('Extension {} not supported'.format(extension))

        parser = FORMAT_PARSERS[extension.replace('.', '').lower()]
        self._metadata = parser(self.file_path)

        self.artist = self._metadata['artist'][0]
        self.album = self._metadata['album'][0]
        self.track_title = self._metadata['title'][0]
        if 'tracknumber' in self._metadata:
            self.track_number = int(self._metadata['tracknumber'][0].split('/')[0])
        else:
            self.track_number = 0
        self.file_format = extension.replace('.', '')

    def set_format(self, file_format):
        """
        set_format : validate format before setting it
        """
        if (file_format != 'mp3' and file_format != 'flac'):
            raise FormatNotImplemented('File format {} not supported'.format(file_format))
        self._file_format = file_format

    def get_format(self):
        """ get_format : simple getting for _file_format """
        return self._file_format

    file_format = property(fset=set_format, fget=get_format)

    def get_display_string(self):
        """
        get_display_string : return human-readable string of artist, album, and track names
        """
        return self.display_format.format(self.artist, self.album, self.track_title)

    def get_local_path(self):
        """
        get_local_path : return path to where this track should be on local disk
        """
        basename = self.basename_format.format(self.recording_id, self.file_format)
        return os.path.join(config.MEDIA_DIR, self.artist_id, self.release_id, basename)

    def get_remote_path(self):
        """
        get_remote_path : return path to where this track should be on network storage
        """
        basename = self.basename_format.format(self.recording_id, self.file_format)
        return os.path.join(config.CLOUD_STORAGE_PREFIX, self.artist_id, self.release_id, basename)

class FormatNotImplemented(Exception):
    """
    FormatNotImplemented : exception for filetypes not supported by the Metadata class
    """
    pass
