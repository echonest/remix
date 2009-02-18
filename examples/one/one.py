#!/usr/bin/env python
# encoding: utf=8

"""
one.py

Digest only the first beat of every bar.

By Ben Lacker, 2009-02-18.
"""
import echonest.audio as audio
from echonest.selection import have_pitch_max,have_pitches_max

usage = """
Usage: 
    python one.py <inputFilename> <outputFilename>

Example:
    python one.py HereComesTheSun.mp3 HereComesTheOne.mp3
"""


def main(inputFile, outputFile):
    audiofile = audio.LocalAudioFile(inputFile)
    bars = audiofile.analysis.bars
    collect = audio.AudioQuantumList()
    for bar in bars:
        collect.append(bar.children()[0])
    out = audio.getpieces(audiofile, collect)
    out.encode(outputFile)


if __name__ == '__main__':
    import sys
    try:
        inputFilename = sys.argv[-2]
        outputFilename = sys.argv[-1]
    except:
        print usage
        sys.exit(-1)
    main(inputFilename, outputFilename)
