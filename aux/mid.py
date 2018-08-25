"""
mid.py — get or create a uuid for a song

"mid" is supposed to stand for "Monty ID", but we'll see if that sticks
"""

import hashlib
import os
import sys
import uuid

from mutagen import mp3, flac


def create_uuid_from_file(file_obj) -> str:
    """
    create_uuid_from_file - read from a file-like object, return a uuid string
    created from the md5 hash of the contents
    """
    md5 = hashlib.md5()
    md5.update(file_obj.read())
    return str(uuid.UUID(bytes=md5.digest()))


def strip_metadata_and_create_uuid(filename: str) -> str:
    """
    strip_metadata_and_create_uuid - discard metata from file_obj then create
    uuid from md5 of audio content
    """
    _, extension = os.path.splitext(filename)
    if extension == '.mp3':
        metadata = mp3.EasyMP3(filename)
    elif extension == '.flac':
        metadata = flac.FLAC(filename)
    else:
        raise Exception('Extension {} not supported'.format(extension))
    with open(filename, 'rb') as file_obj:
        mid = create_uuid_from_file(file_obj)
    return mid


if __name__ == '__main__':
    print(strip_metadata_and_create_uuid(sys.argv[1]))
