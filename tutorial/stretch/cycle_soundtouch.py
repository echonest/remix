#!/usr/bin/env python
# encoding: utf-8
"""
cycle.py

Periodically time-compress and time-stretch the beats in each measure.
Each measure starts fast and ends slow.
This version uses the SoundTouch timestretching library.  
It is faster than dirac, but is lower quality.

Created by Ben Lacker on 2009-06-16.
Refactored by Thor Kell on 2013-03-06.
"""
import math
import os
import sys

from echonest.remix import audio, modify

usage = """
Usage:
    python cycle.py <input_filename> <output_filename>
Exampel:
    python cycle.py CryMeARiver.mp3 CryCycle.mp3
"""

# Cycle timestreches each beat!

# Remix has two timestreching libraries, dirac and SoundTouch.  
# This version uses the SoundTouch timeScale function.
# SoundTouch is faster, but lower quality.   
# Cycle works by looping beat within each bar.
# A stretch ratio is calculate based on what beat it is.
# Then the data is timestretched by this ratio, and added to the output.  

def main(input_filename, output_filename):
    # This takes your input track, sends it to the analyzer, and returns the results.
    audiofile = audio.LocalAudioFile(input_filename)

    # Just a local alias to the soundtouch library, which handles the pitch shifting.
    soundtouch = modify.Modify()

    # This gets a list of every bar in the track.  
    # You can manipulate this just like any other Python list!
    beats = audiofile.analysis.beats

    # The output array
    collect = []

    # This loop streches each beat by a varying ratio, and then re-assmbles them.
    for beat in beats:
        # Find out where in the bar the beat is, and calculate a ratio based on that.
        context = beat.local_context()
        ratio = (math.cos(math.pi * 2 * context[0]/float(context[1])) / 2) + 1
        # Stretch the beat!  SoundTouch returns an AudioData object
        new = soundtouch.shiftTempo(audiofile[beat], ratio)
        # Append the stretched beat to the list of beats
        collect.append(new)
    
    # Assemble and write the output data
    out = audio.assemble(collect)
    out.encode(output_filename)


    # The wrapper for the script.  
if __name__ == '__main__':
    import sys
    try:
        # This gets the filenames to read from and write to.
        input_filename = sys.argv[1]
        output_filename = sys.argv[2]
    except:
        # If things go wrong, exit!
        print usage
        sys.exit(-1)
    main(input_filename, output_filename)
