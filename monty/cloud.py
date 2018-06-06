"""
cloud.py : interactions with the cloud
"""

import os
from google.cloud import storage

import monty.config as config

class CloudStorage(object):
    """
    CloudStorage : class for interacting with cloud storage
    """

    def __init__(self):
        self.client = storage.Client()
        self.bucket = self.client.get_bucket(config.CLOUD_STORAGE_BUCKET)

    def get_recording(self, artist_id, release_id, recording_id, file_format):
        """
        get_recording : download a recording from cloud storage
        """
        # make sure artist/album directory exists locally
        album_dir = os.path.join(config.MEDIA_DIR, artist_id, release_id)
        try:
            os.mkdir(album_dir)
        except FileExistsError:
            pass

        # now download the thing
        recording_shortname = '{}.{}'.format(recording_id, file_format)
        recording_path = os.path.join(album_dir, recording_shortname)
        blob_name = os.path.join(config.CLOUD_STORAGE_PREFIX,
                                 artist_id,
                                 release_id,
                                 recording_shortname)
        storage.Blob(name=blob_name, bucket=self.bucket).download_to_filename(recording_path)

    def get_audio_index(self):
        """
        get_audio_index : pretty self-explanatory
        """
        blob_name = '/index/audio.json'
        storage.Blob(name=blob_name, bucket=self.bucket).download_to_filename(config.AUDIO_INDEX_LOCATION)
