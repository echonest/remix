#!/usr/bin/env python
# encoding: utf=8

"""
summary.py

Digest only the first or only the second tatum of every beat.

By Ben Lacker, 2009-02-18.
"""
import echonest.audio as audio
from echonest.selection import have_pitch_max,have_pitches_max

usage = """
Usage: 
    python summary.py [and] <inputFilename> <outputFilename>

Example:
    python summary.py RichGirl.mp3 RichSummary.mp3
"""


def main(inputFile, outputFile, index):
    audiofile = audio.LocalAudioFile(inputFile)
    beats = audiofile.analysis.beats
    collect = audio.AudioQuantumList()
    for beat in beats:
        tata = beat.children()
        if len(tata)>1:
            tat = tata[index]
        else:
            tat = tata[0]
        collect.append(tat)
    out = audio.getpieces(audiofile, collect)
    out.encode(outputFile)


if __name__ == '__main__':
    import sys
    try:
        if sys.argv[-3]=='and':
            index = 1
        else:
            index = 0
        inputFilename = sys.argv[-2]
        outputFilename = sys.argv[-1]
    except:
        print usage
        sys.exit(-1)
    main(inputFilename, outputFilename, index)
