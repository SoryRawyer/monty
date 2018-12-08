"""
config.py : project-wide configuration
"""

import os

# local app values
APP_DIR = os.path.join(os.environ['HOME'], '.monty/')
MEDIA_DIR = os.path.join(APP_DIR, 'media', 'audio')
DB_LOCATION = os.path.join(APP_DIR, 'db/local.db')
AUDIO_INDEX_LOCATION = os.path.join(APP_DIR, 'index/audio.json')

# Cloud storage values
CLOUD_STORAGE_PREFIX = 'audio'
CLOUD_STORAGE_BUCKET = 'monty-media'

def ensure_dir(complete_dir):
    """
    given a directory, only try to make the intermediate directories
    that don't already exist
    """
    complete_dir = os.path.abspath(os.path.dirname(complete_dir))
    curr = '/'
    levels = [i for i in complete_dir.split('/') if i]
    for level in levels:
        curr = os.path.join(curr, level)
        if not os.path.isdir(curr):
            os.mkdir(curr)
    return
