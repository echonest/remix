#!/usr/bin/env python
# encoding: utf=8

"""
lopside.py

Cut out the final beat or group of tatums in each bar.
Demonstrates the beat hierarchy navigation in AudioQuantum

Originally by Adam Lindsay, 2009-01-19.
"""
import echonest.audio as audio
import sys

usage = """
Usage: 
    python lopside.py [tatum|beat] <inputFilename> <outputFilename>
Beat is selected by default.

Example:
    python lopside.py beat aha.mp3 ahawaltz.mp3
"""


def main(units, inputFile, outputFile):
    audiofile = audio.LocalAudioFile(inputFile)
    collect = audio.AudioQuantumList()
    if not audiofile.analysis.bars:
        print "No bars found in this analysis!"
        print "No output."
        sys.exit(-1)
    for b in audiofile.analysis.bars[0:-1]:                
        # all but the last beat
        collect.extend(b.children()[0:-1])
        if units.startswith("tatum"):
            # all but the last half (round down) of the last beat
            half = - (len(b.children()[-1].children()) // 2)
            collect.extend(b.children()[-1].children()[0:half])
    # endings were rough, so leave everything after the start
    # of the final bar intact:
    last = audio.AudioQuantum(audiofile.analysis.bars[-1].start,
                              audiofile.analysis.duration - 
                                audiofile.analysis.bars[-1].start)
    collect.append(last)
    out = audio.getpieces(audiofile, collect)
    out.encode(outputFile)

if __name__ == '__main__':
    try:
        units = sys.argv[-3]
        inputFilename = sys.argv[-2]
        outputFilename = sys.argv[-1]
    except:
        print usage
        sys.exit(-1)
    main(units, inputFilename, outputFilename)
