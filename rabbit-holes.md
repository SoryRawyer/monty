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
