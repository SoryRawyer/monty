"""
ingest.py : ingest data and file it away under the monty system

Arugments:
- music_location : full path to music to be ingested
- upload_bucket : google cloud bucket name to upload to

store track in upload_bucket based on the following convention (all "id"s are musicbrainz ids):
    {artist-id}/{album-id}/{recording-id}.{file_format}

recursively walk the input directory
get artist/album/song using mutagen
look up artist/album/song using musicbrainz
"""

import argparse
import json
import os
import shutil
from typing import List
from google.cloud import storage

from monty import config
from monty.index import generate_local_index

def main(arguments):
    """
    main : do something with the args
    look up metadata for each track
    """
    client = storage.Client()
    enriched_metadata = generate_local_index(arguments.music_location)
    bucket = client.get_bucket(arguments.upload_bucket)
    for track in enriched_metadata:
        _, ext = os.path.splitext(track.file_path)
        ext = ext.replace('.', '')
        upload_location = os.path.join(arguments.upload_prefix,
                                       track.artist_id,
                                       track.release_id,
                                       '{}.{}'.format(track.track_id, ext))
        print('Uploading {} to {}/{}'.format(track.file_path,
                                             arguments.upload_bucket,
                                             upload_location))
        blob = bucket.blob(upload_location)
        with open(track.file_path, 'rb') as audio:
            blob.upload_from_file(audio)
    # tracks uploaded. now let's make that index
    # first, check to see if it's already there
    index_location = os.path.join('index', 'audio.json')
    existing_blob = bucket.get_blob(index_location)
    index = {}
    for track in enriched_metadata:
        index[track.track_id] = {
            'artist' : track.artist,
            'album' : track.album,
            'track_name' : track.track_title,
            'position' : track.track_number,
            'path' : track.file_path,
            'artist_id' : track.artist_id,
            'release_id' : track.release_id,
            'track_id' : track.track_id,
            'file_format' : track.file_format,
        }
    if existing_blob:
        # blob exists
        beep = existing_blob.download_as_string()
        existing_index = json.loads(beep)
        # the next two lines are dumb and should be removed
        existing_index.update(index)
        index = existing_index
    # the next 5 lines are also dumb and should also be removed
    with open('audio_index.json', 'w') as tmp:
        json.dump(index, tmp)
    with open('audio_index.json', 'rb') as tmp:
        blob = bucket.blob(index_location)
        blob.upload_from_file(tmp)
    copy_to_media_directory(enriched_metadata)

def copy_to_media_directory(metadata: List[dict]):
    """
    copy_to_media_directory
    arugments:
    - list of files to copy (dict containing song IDs)
    """
    for metadatum in metadata:
        src = metadatum.file_path
        album_dir = os.path.join(config.MEDIA_DIR,
                                 metadatum.artist_id,
                                 metadatum.release_id)
        try:
            os.makedirs(album_dir)
        except FileExistsError:
            pass
        dest_shortname = '{}.{}'.format(metadatum.recording_id, metadatum.file_format)
        dest = os.path.join(album_dir, dest_shortname)
        shutil.copyfile(src, dest)


def parse():
    """
    parse : parse input arguments
    # TODO: add an --offline option to avoid network calls
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('music_location')
    parser.add_argument('upload_bucket')
    parser.add_argument('upload_prefix')
    return parser.parse_args()

if __name__ == '__main__':
    main(parse())
