#!/usr/bin/env python
# encoding: utf-8
"""
beatshift.py

Pitchshift each beat based on its position in the bar.
Beat one is unchanged, beat two is shifted down one half step,
beat three is shifted down two half steps, etc.

Created by Ben Lacker on 2009-06-24.
"""
import numpy
import os
import random
import sys
import time

import soundtouch
from echonest import audio, modify

USAGE = """
Usage:
    python beatshift.py <input_filename> <output_filename>
Exampel:
    python beatshift.py CryMeARiver.mp3 CryMeAShifty.mp3
"""

def main():
    try:
        in_filename = sys.argv[1]
        out_filename = sys.argv[2]
    except Exception:
        print USAGE
        sys.exit(-1)
    st = modify.Modify()
    afile = audio.LocalAudioFile(in_filename)
    beats = afile.analysis.beats
    out_shape = (len(afile.data),)
    out_data = audio.AudioData(shape=out_shape, numChannels=1, sampleRate=44100)
    for i, beat in enumerate(beats):
        data = afile[beat].data
        number = beat.local_context()[0] % 12
        new_ad = st.shiftPitchSemiTones(afile[beat], number*-1)
        out_data.append(new_ad)
    out_data.encode(out_filename)


if __name__ == '__main__':
    main()

