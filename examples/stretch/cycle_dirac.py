#!/usr/bin/env python
# encoding: utf-8
"""
cycle.py

Periodically time-compress and time-stretch the beats in each measure.
Each measure starts fast and ends slow.

Created by Thor Kell on 2013-05-06, based on code by Ben Lacker.
"""
import math
import os
import sys
import dirac
from echonest.remix import audio

usage = """
Usage:
    python cycle.py <input_filename> <output_filename>
Exampel:
    python cycle.py CryMeARiver.mp3 CryCycle.mp3
"""

def main(input_filename, output_filename):
    audiofile = audio.LocalAudioFile(input_filename)
    bars = audiofile.analysis.bars
    collect = []

    for bar in bars:
        bar_ratio = (bars.index(bar) % 4) / 2.0
        beats = bar.children()
        for beat in beats:
            beat_index = beat.local_context()[0]
            ratio = beat_index / 2.0 + 0.5
            ratio = ratio + bar_ratio # dirac can't compress by less than 0.5!
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
    except:
        print usage
        sys.exit(-1)
    main(input_filename, output_filename)

