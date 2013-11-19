#!/usr/bin/env python
# encoding: utf-8
"""
simple_stretch.py

Compress or exapand the entire track, beat by beat.  

Created by Thor Kell on 2013-11-18
"""
import math
import os
import sys
import dirac
from echonest.remix import audio

usage = """
Usage:
    python simple_stretch.py <input_filename> <output_filename> <ratio> 
Example:
    python simple_stretch.py CryMeARiver.mp3 StrechMeARiver.mp3
Notes:
    Ratio must be greater than 0.5
"""

def main(input_filename, output_filename, ratio):
    audiofile = audio.LocalAudioFile(input_filename)
    beats = audiofile.analysis.beats
    collect = []

    for beat in beats:
        beat_audio = beat.render()
        scaled_beat = dirac.timeScale(beat_audio.data, ratio)
        ts = audio.AudioData(ndarray=scaled_beat, shape=scaled_beat.shape, 
                        sampleRate=audiofile.sampleRate, numChannels=scaled_beat.shape[1])
        collect.append(ts)

    out = audio.assemble(collect, numChannels=2)
    out.encode(output_filename)

if __name__ == '__main__':
    import sys
    try:
        input_filename = sys.argv[1]
        output_filename = sys.argv[2]
        ratio = float(sys.argv[3])
        if ratio < 0.5:
            print "Error:  Ratio must be greater than 0.5!"
            sys.exit(-1)
    except:
        print usage
        sys.exit(-1)
    main(input_filename, output_filename, ratio)
