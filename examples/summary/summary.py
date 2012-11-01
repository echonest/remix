#!/usr/bin/env python
# encoding: utf=8

"""
summary.py

Digest only the first or only the second tatum of every beat.

By Ben Lacker, 2009-02-18.
"""
import sys

import echonest.audio as audio
from echonest.selection import have_pitch_max,have_pitches_max

usage = """
Usage: 
    python summary.py [and] <input_filename> <output_filename>

Example:
    python summary.py RichGirl.mp3 RichSummary.mp3
"""


def main(input_filename, output_filename, index):
    audio_file = audio.LocalAudioFile(input_filename)
    beats = audio_file.analysis.beats
    collect = audio.AudioQuantumList()
    for beat in beats:
        tata = beat.children()
        if len(tata)>1:
            tat = tata[index]
        else:
            tat = tata[0]
        collect.append(tat)
    out = audio.getpieces(audio_file, collect)
    out.encode(output_filename)


if __name__ == '__main__':
    try:
        if sys.argv[1]=='and':
            index = 1
        else:
            index = 0
        input_filename = sys.argv[-2]
        output_filename = sys.argv[-1]
    except:
        print usage
        sys.exit(-1)
    main(input_filename, output_filename, index)
