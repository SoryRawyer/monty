"""
index.py : functions to get musicbrainz data for files and then do something with that

recursively walk the input directory
get artist/album/song using mutagen
look up artist/album/song using musicbrainz
"""

import os
from typing import Callable, List

import musicbrainzngs as mb
from mutagen import mp3, flac

from monty.metadata import Metadata

mb.set_useragent("application", "0.01", "http://example.com")

def generate_local_index(directory: str) -> List[Metadata]:
    """
    generate_local_index : generate an index (list of dicts) of music data
    arguments:
    - directory : full path to root of media for which we want to generate index

    returns list of dict with musicbrainz ids and names and file format
    """
    metadata = get_metadata_for_directory(directory)
    get_track_data = get_musicbrainz_data()
    enriched_metadata = [get_track_data(i) for i in metadata]
    return enriched_metadata

def get_musicbrainz_data() -> Callable[[dict], dict]:
    """
    get_musicbrainz_data : memoization closure for musicbrainz data
    reduce calls to the musicbrainz api by saving track lists

    returns a closure, get_mb_data_for_track
    """

    # releases_with_tracks : key is release ID, value is a track list sorted by track number
    releases_with_tracks = {}

    def get_mb_data_for_track(metadata: Metadata) -> Metadata:
        """
        get_mb_data_for_track
        arguments:
            metadata : Metadata object containing artist, album, and track names
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
            track = releases_with_tracks[release['id']][metadata.track_number - 1]
        else:
            release_with_tracks = mb.get_release_by_id(release['id'], includes=['recordings'])
            tracks = release_with_tracks['release']['medium-list'][0]['track-list']
            tracks.sort(key=lambda x: int(x['position']))
            releases_with_tracks[release['id']] = tracks
            track = tracks[metadata.track_number - 1]

        metadata.artist_id = artist['id']
        metadata.release_id = release['id']
        metadata.track_id = track['recording']['id']

        return metadata

    return get_mb_data_for_track

def get_metadata_for_directory(directory: str) -> List[dict]:
    """
    get_metadata_for_directory
    arguments:
        directory: full path to directory of audio files
    returns:
        listof metadata dicts (with paths!)
    """
    metadata = []
    for (dirpath, dirnames, filenames) in os.walk(directory):
        for dirname in dirnames:
            get_metadata_for_directory(dirname)
        metadata += [Metadata(os.path.join(dirpath, filename))
                     for filename in filenames]
    return metadata

def get_artist_album_track_name(path: str) -> dict:
    """
    get_artist_album_track_name : read metadata from file and return certain fields
    argument: full path to audio file
    return artist, album, and track name
    """
    metadata = Metadata(path)
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
