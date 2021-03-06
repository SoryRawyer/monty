### rabbit holes

- decoding MP3s
- explore interaction with OSX/handling keyboard events
- HLS/RTTP
- multithreading

### monty-server

API needs:
- list tracks
- get track(s)

cloud storage + 1 database table?

nice to know:
- estimate of number of files we'll be hosting
    - cost of serving that data/listing objects on cloud storage
    - cost of keeping that stuff in a database table and querying it

rest vs grpc: maybe go with grpc because it's newer and I know less about it?

### how it will eventually work
- launch_player.py:
  - launches gui
  - looks for local DB, if it's not there it will make one
  - local DB has a list of all the music on the computer
  - local db will also try to get a list of all music in cloud storage
  - if a user wants to listen to a song that's on cloud storage, monty will download it
- index.py recursively reads a directory and returns metadata about it (both from the file and from musicbrainz)
- ingest.py uploads music returned by index.py to cloud storage
  - upload path is determined by data returned by the musicbrainz API
  - moves data to the application's media directory, also stored using musicbrainz IDs

---

rough outline of things to acheive with varying degrees of "I can do this":
- create a docker image for this so I can put this wherever and have it *just work*
- use google cloud (or something else) to store music remotely so I don't use all my disk space
- create an API for getting/browsing music
- create an iOS app so I can move this music to my phone
- should iOS be successful, add chromecast support
- try and get video on this thing too
- try some audio fingerprinting
- store play count data
- get the gui to display a little more information in a way that's useful?

