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
import numpy
import os
import random
import sys
import time

from echonest.remix import audio, modify

usage = """
Usage:
    python beatshift.py <input_filename> <output_filename>
Exampel:
    python beatshift.py CryMeARiver.mp3 CryMeAShifty.mp3
"""

def main(input_filename, output_filename):
    soundtouch = modify.Modify()
    audiofile = audio.LocalAudioFile(input_filename)
    beats = audiofile.analysis.beats
    out_shape = (len(audiofile.data),)
    out_data = audio.AudioData(shape=out_shape, numChannels=1, sampleRate=44100)
    
    for i, beat in enumerate(beats):
        data = audiofile[beat].data
        number = beat.local_context()[0] % 12
        new_beat = soundtouch.shiftPitchSemiTones(audiofile[beat], number*-1)
        out_data.append(new_beat)
    
    out_data.encode(output_filename)

if __name__ == '__main__':
    import sys
    try:
        input_filename = sys.argv[1]
        output_filename = sys.argv[2]
    except:
        print usage
        sys.exit(-1)
    main(input_filename, output_filename)
