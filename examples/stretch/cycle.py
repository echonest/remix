#!/usr/bin/env python
# encoding: utf-8
"""
cycle.py

Periodically time-compress and time-stretch the beats in each measure.
Each measure starts fast and ends slow.

Created by Ben Lacker on 2009-06-16.
"""
import math
import os
import sys

from echonest import audio, modify

USAGE = """
Usage:
    python cycle.py <input_filename> <output_filename>
Exampel:
    python cycle.py CryMeARiver.mp3 CryCycle.mp3
"""

def main():
    try:
        in_filename = sys.argv[1]
        out_filename = sys.argv[2]
    except Exception:
        print USAGE
        sys.exit(-1)
    afile = audio.LocalAudioFile(in_filename)
    st = modify.Modify()
    beats = afile.analysis.beats
    collect = []
    for beat in beats:
        context = beat.local_context()
        ratio = (math.cos(math.pi * 2 * context[0]/float(context[1])) / 2) + 1
        new = st.shiftTempo(afile[beat], ratio)
        collect.append(new)
    out = audio.assemble(collect)
    out.encode(out_filename)

if __name__ == '__main__':
    main()

