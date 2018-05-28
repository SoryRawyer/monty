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
import tempfile

import musicbrainzngs as mb
from mutagen import mp3, flac

from google.cloud import storage

mb.set_useragent("application", "0.01", "http://example.com")

def main(arguments):
    """
    main : do something with the args
    look up metadata for each track
    """
    client = storage.Client()
    metadata = get_metadata_for_directory(arguments.music_location)
    get_track_data = get_musicbrainz_data()
    enriched_metadata = [get_track_data(i) for i in metadata]
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


def get_musicbrainz_data():
    """
    get_musicbrainz_data : memoization closure for musicbrainz data
    reduce calls to the musicbrainz api by saving track lists
    """

    # releases_with_tracks : key is release ID, value is a track list sorted by track number
    releases_with_tracks = {}

    def get_mb_data_for_track(metadata: dict):
        """
        get_mb_data_for_track
        arguments:
            metadata : dict containing artist, album, and track names
        returns:
            musicbrainz ids for artist, album, and track names
        """
        # get artist and album id by searching for release groups with both artist and album name?
        # search for recording: filter results based on release and artist
        search_string = '{} {}'.format(metadata['artist'], metadata['album'])
        try:
            release_group = mb.search_release_groups(search_string)
        except mb.musicbrainz.ResponseError:
            search_string = metadata['album']
            release_group = mb.search_release_groups(search_string)

        artist = release_group['release-group-list'][0]['artist-credit'][0]['artist']
        release = release_group['release-group-list'][0]['release-list'][0]

        if release['id'] in releases_with_tracks:
            track = releases_with_tracks[release['id']][metadata['position'] - 1]
        else:
            release_with_tracks = mb.get_release_by_id(release['id'], includes=['recordings'])
            tracks = release_with_tracks['release']['medium-list'][0]['track-list']
            tracks.sort(key=lambda x: int(x['position']))
            releases_with_tracks[release['id']] = tracks
            track = tracks[metadata['position'] - 1]

        ids = {
            'artist_id' : artist['id'],
            'release_id' : release['id'],
            'track_id' : track['recording']['id'],
        }

        metadata.update(ids)
        return metadata

    return get_mb_data_for_track

def get_metadata_for_directory(music_location) -> (list, list):
    """
    get_metadata_for_directory
    arguments:
        music_location: full path to directory of audio files
    returns:
        listof metadata dicts (with paths!)
    """
    metadata = []
    for (dirpath, dirnames, filenames) in os.walk(music_location):
        for dirname in dirnames:
            get_metadata_for_directory(dirname)
        metadata += [get_artist_album_track_name(os.path.join(dirpath, filename))
                     for filename in filenames]
    return metadata

def get_artist_album_track_name(path: str) -> dict:
    """
    get_artist_album_track_name :
    argument: full path to audio file
    return artist, album, and track name
    """
    _, extension = os.path.splitext(path)
    metadata = None
    if extension == '.mp3':
        metadata = mp3.EasyMP3(path)
    elif extension == '.flac':
        metadata = flac.FLAC(path)
    return {
        'artist' : metadata['artist'][0],
        'album' : metadata['album'][0],
        'track_name' : metadata['title'][0],
        'position' : int(metadata['tracknumber'][0].split('/')[0]),
        'path' : path,
        'format' : extension.replace('.', '')
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('music_location')
    parser.add_argument('upload_bucket')
    parser.add_argument('upload_prefix')
    args = parser.parse_args()
    main(args)
