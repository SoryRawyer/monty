# monty — eventually a media player

purpose: I'd like a way to play music outside of apple music/google play. Spotify doesn't necessarily have everything I'd listen to.  

to run: `$ python launch_player.py`  

right now, you need to "load" data into Monty. you can do this by running:
`$ ingest.py <directory> <upload-bucket> <upload-prefix>`
where
- `directory` is the local directory containing audio files you wish to upload
- `upload-bucket` is the target google cloud storage bucket to upload data
- `upload-prefix` is a prefix that will be prepended to all object names

`ingest.py` will also copy the data in `directory` to monty's local application directory and create an index of that data. This will avoid needing to download the same audio you just ingested.

Once there's audio to play, running `$ python launch_player.py` will open up the audio player

The GUI uses TKinter, but I'm thinking about moving to Kivy.

The idea is that, since the gui doesn't support any import stuff at the moment, users would point the ingest script at some directory they want to pull into Monty. That script will:
- look up the track(s) in musicbrainz
  - I'm actually not sure if Monty will continue to process things that don't have musicbrainz data. I can't forget if that code ever landed in master or not. let me check real quick
- something about uploading to google cloud, if possible
- move files to a central monty location (by default I think this is `~/media/audio`)
- add those files to an index, either in sqlite, google cloud, or both
