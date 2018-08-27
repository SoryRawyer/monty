# monty — eventually a media player

purpose: I'd like a way to play music outside of itunes. Spotify doesn't necessarily have everything I'd listen to.

to run: `$ python launch_player.py`

right now, you need to "load" data into Monty. you can do this by running:  
`$ ingest.py <directory> <upload-bucket> <upload-prefix>`
where
- `directory` is the local directory containing audio files you wish to upload
- `upload-bucket` is the target google cloud storage bucket to upload data
- `upload-prefix` is a prefix that will be prepended to all object names

`ingest.py` will also copy the data in `directory` to monty's local application directory and create an index of that data. This will avoid needing to download the same audio you just ingested.

Once there's audio to play, running `$ python launch_player.py` will open up the audio player
