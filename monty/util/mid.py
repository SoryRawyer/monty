"""
mid.py — get or create a uuid for a song

"mid" is supposed to stand for "Monty ID", but we'll see if that sticks
"""

import hashlib
import sys
import uuid


def create_uuid_from_file(filename) -> str:
    """
    create_uuid_from_file - read from a file-like object, return a uuid string
    created from the md5 hash of the contents
    """
    md5 = hashlib.md5()
    with open(filename, 'rb') as file_obj:
        md5.update(file_obj.read())
    return str(uuid.UUID(bytes=md5.digest()))


def create_uuid_from_string(string):
    """
    create_uuid_from_string - pretty self-explanatory
    """
    md5 = hashlib.md5()
    md5.update(string.encode('UTF-8'))
    return str(uuid.UUID(bytes=md5.digest()))


if __name__ == '__main__':
    print(create_uuid_from_file(sys.argv[1]))
