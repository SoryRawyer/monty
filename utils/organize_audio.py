"""
organize_audio.py : take audio files from one directory and put it in another
base the destination location on artist and album
"""

import argparse
import logging
import os
import re
import shutil
import struct
import sys
from mp3_tagger import MP3File
from mp3_tagger.exceptions import MP3OpenFileError

sh = logging.StreamHandler(sys.stdout)
logger = logging.getLogger(__name__)
logger.addHandler(sh)

def main(args):
    if not os.path.exists(args.target_dir):
        os.mkdir(args.target_dir)
    if args.debug_level == 'DEBUG':
        logger.setLevel(logging.DEBUG)
    elif args.debug_level == 'INFO':
        logger.setLevel(logging.INFO)
    follow_dirs(args.input_dir, args.target_dir)
    return

def follow_dirs(input_dir, target_dir):
    for (dirpath, dirnames, filenames) in os.walk(input_dir):
        for dirname in dirnames:
            follow_dirs(dirname, target_dir)
        for filename in filenames:
            move_file(os.path.join(dirpath, filename), target_dir)
    return

def move_file(filename, target_dir):
    try:
        mp3 = MP3File(filename)
        tags = mp3.get_tags()
    except (MP3OpenFileError, struct.error) as err:
        logger.warn('received error {} for file {}'.format(err, filename))
        return
    logger.info('Tags: {}'.format(tags))
    artist = ''
    album = ''
    song = ''
    if mp3.album is None or mp3.artist is None or mp3.song is None:
        artist, album, song = get_track_info_from_user(filename, tags)
        if artist == '' or album == '' or song == '':
            return
    else:
        if isinstance(mp3.artist, list):
            artist = mp3.artist[0].value.lower()
        else:
            artist = mp3.artist.lower()
        if isinstance(mp3.album, list):
            album = mp3.album[0].value.lower()
        else:
            album = mp3.album.lower()
    song = clean_song_title(song)
    artist = artist.replace('\x00', '')
    album = album.replace('\x00', '')
    song = song.replace('\x00', '')

    mp3 = update_id3_tags(mp3, artist, album, song)

    artist_directory = os.path.join(target_dir, artist)
    if not os.path.exists(artist_directory):
        os.mkdir(artist_directory)
    album_directory = os.path.join(artist_directory, album)
    if not os.path.exists(album_directory):
        os.mkdir(album_directory)

    target_filename = os.path.join(target_dir, artist, album, '{}.mp3'.format(song))
    logger.info(filename)
    logger.info(target_filename)
    shutil.copyfile(filename, target_filename)
    return

def get_track_info_from_user(filename, tags):
    print('Either artist, album, or song information for file {} is missing. Below are the tags we do have:'.format(filename))
    for k, v in tags.items():
        print(k, v)
    print('Please enter in the artist, album, and song below. To skip this file (e.g. — not copy it over) simply leave each field blank')
    artist = input('Artist name:\n').strip().lower()
    album = input('Album name:\n').strip().lower()
    song = input('Song name:\n').strip()
    print('\n')
    return artist, album, song

def update_id3_tags(mp3: MP3File, artist: str, album: str, song: str) -> MP3File:
    mp3.artist = artist
    mp3.album = album
    mp3.song = song
    mp3.save()
    return mp3

def clean_song_title(song: str) -> str:
    m = re.findall('[0-9]{1,2} - *', song)
    if len(m) > 0:
        song = ' - '.join([x for x in song.split(' - ')[1:]])
    return song


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir', type=str, help='input directory to look for audio files')
    parser.add_argument('target_dir', type=str, help='target directory to copy files to from input_dir')
    parser.add_argument('--debug_level', type=str, default='INFO', help='level of debugging statements printed')
    main(parser.parse_args())
