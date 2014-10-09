#!/usr/bin/env python
# encoding: utf-8
"""
cycle.py

Periodically time-compress and time-stretch the beats in each measure.
Each measure starts fast and ends slow.

Currently there is a bug with soundtouch.
Please see cycle_dirac, and use dirac for time stretching.

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

def main(input_filename, output_filename):

    audiofile = audio.LocalAudioFile(input_filename)
    soundtouch = modify.Modify()
    beats = audiofile.analysis.beats
    collect = []

    for beat in beats:
        context = beat.local_context()
        ratio = (math.cos(math.pi * 2 * context[0]/float(context[1])) / 2) + 1
        new = soundtouch.shiftTempo(audiofile[beat], ratio)
        collect.append(new)
    
    out = audio.assemble(collect)
    out.encode(output_filename)

if __name__ == '__main__':
    import sys
    try:
        input_filename = sys.argv[1]
        output_filename = sys.argv[2]
    except:
        print usage
        sys.exit(-1)
    main(input_filename, output_filename)
