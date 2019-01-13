This is a kind of very simple audio player, that works from a 'schedule' where you can set "stop" points (where playback will always stop) and add notes.

Requirements `pip install audioread pyaudio`



# How to define the schedule

The schedule is a simple text file that looks like this:

```
This is a note that will appear as-is.

This as well!

Below is how to play a file:
PLAY <filename>
PLAY <filename2>

If you want to stop after playing some files use this:
STOP
```


# TODO
- [ ] Show a monitor for how far within a file we are
- [ ] Volume control


