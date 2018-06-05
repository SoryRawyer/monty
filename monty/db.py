"""
db.py : do some database-y things with sqlite

This should keep track of what songs we have available, with a flag for local vs remote
"""

import json
import os
import sqlite3
from typing import List

import trio

import monty.config as config
from monty.cloud import CloudStorage
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
        pass

    def init_db(self):
        """
        init_db : go through self.media_dir and store metadata in sqlite
        """
        with self._conn:
            self._conn.execute("""
            create table audio_tracks 
                (artist varchar,
                 album varchar,
                 track_title varchar,
                 track_number int,
                 file_path varchar,
                 artist_id varchar,
                 release_id varchar,
                 track_id varchar,
                 file_format varchar)
            """)
        # iterate through self.media_dir
        #   get metadata for each track, then insert it into the database
        with self._conn:
            for metadatum in Database.get_tracks_from_index_file(config.AUDIO_INDEX_LOCATION):
                self._conn.execute("""
                insert into audio_tracks (
                    artist,
                    album,
                    track_title,
                    track_number,
                    file_path,
                    artist_id,
                    release_id,
                    track_id,
                    file_format)
                 values (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (metadatum.artist,
                      metadatum.album,
                      metadatum.track_title,
                      metadatum.track_number,
                      metadatum.file_path,
                      metadatum.artist_id,
                      metadatum.release_id,
                      metadatum.recording_id,
                      metadatum.file_format))

    def generate_all_track_info(self):
        """
        generate_all_track_info : create a generator for all track information
        """
        query = 'select * from audio_tracks order by artist, album, track_number'
        for i in self._conn.execute(query):
            metadatum = Metadata()
            metadatum.artist = i[0]
            metadatum.album = i[1]
            metadatum.track_title = i[2]
            metadatum.track_number = i[3]
            metadatum.file_path = i[4]
            metadatum.artist_id = i[5]
            metadatum.release_id = i[6]
            metadatum.recording_id = i[7]
            metadatum.file_format = i[8]
            yield metadatum

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
                    yield (Metadata(os.path.join(dirpath, filename)),
                           os.path.join(dirpath, filename))
                except FormatNotImplemented:
                    continue

    @staticmethod
    def get_tracks_from_index_file(index: str) -> List[Metadata]:
        """
        get_tracks_from_index_file : pretty self-explanatory
        """
        with open(index) as index_file:
            tracks = json.load(index_file)
        metadata = []
        for track_id in tracks:
            track = tracks[track_id]
            metadatum = Metadata()
            metadatum.artist = track['artist']
            metadatum.album = track['album']
            metadatum.track_title = track['track_name']
            metadatum.track_number = track['position']
            metadatum.file_path = track['path']
            metadatum.artist_id = track['artist_id']
            metadatum.release_id = track['release_id']
            metadatum.recording_id = track['track_id']
            try:
                metadatum.file_format = track['format']
            except KeyError:
                _, ext = os.path.splitext(track['path'])
                metadatum.file_format = ext.replace('.', '')
            metadata.append(metadatum)
        return metadata

    @staticmethod
    async def new():
        """
        new : asynchronously create a new instance of a database object
        """
        db = Database()
        db.media_dir = config.MEDIA_DIR
        db.db_location = config.DB_LOCATION
        if not os.path.isfile(db.db_location):
            # if the db doesn't exist, make it!
            db._conn = sqlite3.connect(db.db_location)
            storage = CloudStorage()
            await storage.get_audio_index()
            db.init_db()
        else:
            db._conn = sqlite3.connect(db.db_location)
        return db


if __name__ == '__main__':
    db = Database()
