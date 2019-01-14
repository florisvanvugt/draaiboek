This is a kind of very simple audio player, that works from a 'schedule' where you can set "stop" points (where playback will always stop) and add notes.

Requirements Python3, and `pip install audioread pyaudio`



# Usage

Launch the program, select a schedule file.

Double click on a sound to play it, or use the space bar.
Click on it again to stop it, or again use the space bar.



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
- [x] Show a monitor for how far within a file we are
- [ ] Volume control
- [x] When you pause and unpause a file, continue playing where it left off.
- [x] Playing files with different framerate
- [x] Check going back and forth between files of different frame rates (sometimes you get some issues it seems)
- [x] <spacebar> continues after a STOP

