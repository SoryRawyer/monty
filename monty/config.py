"""
config.py : project-wide configuration
"""

import os

# local app values
APP_DIR = '/Users/rorysawyer/.monty'
MEDIA_DIR = '/Users/rorysawyer/media/audio'
DB_LOCATION = os.path.join(APP_DIR, 'db/local.db')
AUDIO_INDEX_LOCATION = os.path.join(APP_DIR, 'index/audio.json')

# Cloud storage values
CLOUD_STORAGE_PREFIX = '/audio'
CLOUD_STORAGE_BUCKET = 'monty-media'
