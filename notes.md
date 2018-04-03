### notes

>>> import pyaudio
>>> p = pyaudio.PyAudio()
>>> stream = p.open(format=p.get_format_from_width(song.sample_width), channels=song.channels, rate=song.frame_rate, output=True)
>>> for i in range(0, 1000):
...     stream.write(song._data[i])
...
Traceback (most recent call last):
  File "<stdin>", line 2, in <module>
  File "/Users/rorysawyer/.pyenv/versions/3.6.3/lib/python3.6/site-packages/pyaudio.py", line 582, in write
    num_frames = int(len(frames) / (self._channels * width))
TypeError: object of type 'int' has no len()
>>> song._data[i]
0
>>> for i in range(0, 1000):
...     stream.write(song._data)
...