# monty — eventually a media player

purpose: I'd like a way to play music outside of itunes. Spotify doesn't necessarily have everything I'd listen to.

rough outline of things to acheive with varying degrees of "I can do this":
- create a cli for playing music
  - pydub + pyaudio
- create a docker image for this so I can put this wherever and have it *just work*
- use google cloud (or something else) to store music remotely so I don't use all my disk space
- create an API for getting/browsing music
- create an iOS app so I can move this music to my phone
- should iOS be successful, add chromecast support
- try and get video on this thing too
- try some audio fingerprinting
- store play count data
