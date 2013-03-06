#!/usr/bin/env python
# encoding: utf-8
"""
cycle.py

Periodically time-compress and timestretch the beats in each measure.
Things start fast and ends slow.
This version uses the dirac timestretching library.  
It is slower than SoundTouch, but is higher quality.

Created by Thor Kell on 2013-05-06, based on code by Ben Lacker.
"""
# Import other things
import math
import os
import sys
# Import the timestretching library.  
import dirac
# This line imports remix! 
from echonest.remix import audio

usage = """
Usage:
    python cycle.py <input_filename> <output_filename>
Exampel:
    python cycle.py CryMeARiver.mp3 CryCycle.mp3
"""

# Cycle timestreches each beat!

# Remix has two timestreching libraries, dirac and SoundTouch.  
# This version uses the dirac timeScale function.
# Dirac is slower, but higher quality.   

# Cycle works by looping over every bar and beat within each bar.
# A stretch ratio is calculate based on what beat and bar it is.
# Then the data is timestretched by this ratio, and added to the output.  

def main(input_filename, output_filename):
    # This takes your input track, sends it to the analyzer, and returns the results.  
    audiofile = audio.LocalAudioFile(input_filename)

    # This gets a list of every bar in the track.  
    bars = audiofile.analysis.bars

    # The output array
    collect = []

    # This loop streches each beat by a varying ratio, and then re-assmbles them.
    for bar in bars:
        # Caculate a stretch ratio that repeats every four bars.
        bar_ratio = (bars.index(bar) % 4) / 2.0
        # Get the beats in the bar
        beats = bar.children()
        for beat in beats:
            # Find out where in the bar the beat is.
            beat_index = beat.local_context()[0]
            # Calculate a stretch ratio based on where in the bar the beat is
            ratio = beat_index / 2.0 + 0.5
            # Note that dirac can't compress by less than 0.5!
            ratio = ratio + bar_ratio 
            # Get the raw audio data from the beat and scale it by the ratio
            # dirac only works on raw data, and only takes floating-point ratios
            beat_audio = beat.render()
            scaled_beat = dirac.timeScale(beat_audio.data, ratio)
            # Create a new AudioData object from the scaled data
            ts = audio.AudioData(ndarray=scaled_beat, shape=scaled_beat.shape, 
                            sampleRate=audiofile.sampleRate, numChannels=scaled_beat.shape[1])
            # Append the new data to the output list!
            collect.append(ts)

    # Assemble and write the output data
    out = audio.assemble(collect, numChannels=2)
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

