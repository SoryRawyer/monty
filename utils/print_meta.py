import os
from mutagen import mp3

def get_tracks_from_media_dir(input_dir):
    """
    get_tracks_from_media_dir : create a generator for files in media_dir
    """
    for (dirpath, dirnames, filenames) in os.walk(input_dir):
        for dirname in dirnames:
            get_tracks_from_media_dir(dirname)
        for filename in filenames:
            print(mp3.EasyMP3(os.path.join(dirpath, filename)))

if __name__ == '__main__':
    get_tracks_from_media_dir('/Users/rorysawyer/media/audio')
