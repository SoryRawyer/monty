"""
db.py : do some database-y things with sqlite

This should keep track of what songs we have available, with a flag for local vs remote
"""

import os
import sqlite3
import monty.config as config
from monty.metadata import Metadata, FormatNotImplemented

class Database(object):
    """
    Database : maintain connections to sqlite

    db structure: just one table, I think

    if db file isn't there, initialize based on media dir

    Attributes:
        - media_dir : location to look for audio tracks
        - db_location : location of sqlite db file

    DB table attributes:
    - artist name
    - album name
    - song name
    - track number
    """

    def __init__(self):
        self.media_dir = config.media_dir
        self.db_location = config.db_location
        if not os.path.isfile(self.db_location):
            # if the db doesn't exist, make it!
            self._conn = sqlite3.connect(self.db_location)
            self.init_db()
        else:
            self._conn = sqlite3.connect(self.db_location)

    def init_db(self):
        """
        init_db : go through self.media_dir and store metadata in sqlite
        """
        with self._conn:
            self._conn.execute("""
            create table audio_tracks 
                (artist varchar,
                album varchar, 
                track_name varchar,
                album_position int)
            """)
        # iterate through self.media_dir
        #   get metadata for each track, then insert it into the database
        with self._conn:
            for metadata in Database.get_tracks_from_media_dir(self.media_dir):
                self._conn.execute("""
                insert into audio_tracks (artist, album, track_name, album_position) values
                                                (?, ?, ?, ?)
                """, (metadata.artist, metadata.album, metadata.track_title, metadata.track_number))

    def generate_all_track_info(self):
        """
        generate_all_track_info : create a generator for all track information
        """
        for i in self._conn.execute('select * from audio_tracks'):
            yield i

    @staticmethod
    def get_tracks_from_media_dir(input_dir):
        """
        get_tracks_from_media_dir : create a generator for files in media_dir
        """
        for (dirpath, dirnames, filenames) in os.walk(input_dir):
            for dirname in dirnames:
                Database.get_tracks_from_media_dir(dirname)
            for filename in filenames:
                try:
                    yield Metadata(os.path.join(dirpath, filename))
                except FormatNotImplemented:
                    continue

if __name__ == '__main__':
    db = Database()
