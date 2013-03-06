#!/usr/bin/env python
# encoding: utf-8
"""
beatshift.py

Pitchshift each beat based on its position in the bar.
Beat one is unchanged, beat two is shifted down one half step,
beat three is shifted down two half steps, etc.

Created by Ben Lacker on 2009-06-24.
Refactored by Thor Kell on 2013-03-06.
"""

# Import other things
import numpy
import os
import random
import sys
import time

# This line imports remix! 
from echonest.remix import audio, modify

usage = """
Usage:
    python beatshift.py <input_filename> <output_filename>
Exampel:
    python beatshift.py CryMeARiver.mp3 CryMeAShifty.mp3
"""

# Beatshift changes the pitch of each beat!
# It does this by looping over the component beats of the track.
# Then, it pitchshifts each beat relative to it's position in the bar
# This pitch-shifted beat is added to a list.
# That list is then used to create the output audio file.

def main(input_filename, output_filename):
    # Just a local alias to the soundtouch library, which handles the pitch shifting.
    soundtouch = modify.Modify()

    # This takes your input track, sends it to the analyzer, and returns the results.  
    audiofile = audio.LocalAudioFile(input_filename)

    # This gets a list of every beat in the track.  
    # You can manipulate this just like any other Python list!
    beats = audiofile.analysis.beats

    # This creates a new chunk of audio that is the same size and shape as the input file
    # We can do this because we know that our output will be the same size as our input
    out_shape = (len(audiofile.data),)
    out_data = audio.AudioData(shape=out_shape, numChannels=1, sampleRate=44100)
    
    # This loop pitch-shifts each beat and adds it to the new file!
    for i, beat in enumerate(beats):
        # Pitch shifting only works on the data from each beat, not the beat objet itself
        data = audiofile[beat].data
        # The amount to pitch shift each beat.
        # local_context just returns a tuple the position of a beat within its parent bar.
        # (0, 4) for the first beat of a bar, for example
        number = beat.local_context()[0] % 12
        # Do the shift!
        new_beat = soundtouch.shiftPitchSemiTones(audiofile[beat], number*-1)
        out_data.append(new_beat)
    
    # Write the new file
    out_data.encode(output_filename)

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
