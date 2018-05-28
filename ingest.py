"""
ingest.py : ingest data and file it away under the monty system

Arugments:
- music_location : full path to music to be ingested
- upload_bucket : backblaze bucket name to upload to

store track in upload_bucket based on the following convention (all "id"s are musicbrainz ids):
    {artist-id}/{album-id}/{recording-id}.{file_format}

recursively walk the input directory
get artist/album/song using mutagen
look up artist/album/song using musicbrainz
"""

import argparse
import json
import os
from google.cloud import storage

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
        _, ext = os.path.splitext(track['path'])
        ext = ext.replace('.', '')
        upload_location = os.path.join(arguments.upload_prefix,
                                       track['artist_id'],
                                       track['release_id'],
                                       '{}.{}'.format(track['track_id'], ext))
        print('Uploading {} to {}/{}'.format(track['path'],
                                             arguments.upload_bucket,
                                             upload_location))
        blob = bucket.blob(upload_location)
        with open(track['path'], 'rb') as audio:
            blob.upload_from_file(audio)
    # tracks uploaded. now let's make that index
    # first, check to see if it's already there
    index_location = os.path.join('index', 'audio.json')
    existing_blob = bucket.get_blob(index_location)
    index = {}
    for track in enriched_metadata:
        index[track['track_id']] = track
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('music_location')
    parser.add_argument('upload_bucket')
    parser.add_argument('upload_prefix')
    args = parser.parse_args()
    main(args)
