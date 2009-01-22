#!/usr/bin/env python
# encoding: utf=8

"""
lopside.py

Cut out the final beat or group of tatums in each bar.
Demonstrates the beat hierarchy navigation in AudioQuantum

Originally by Adam Lindsay, 2009-01-19.
"""
import echonest.audio as audio

usage = """
Usage: 
    python lopside.py <tatum|beat> <inputFilename> <outputFilename>

Example:
    python tonic.py beat aha.mp3 ahawaltz.wav
"""


def main(units, inputFile, outputFile):
    audiofile = audio.LocalAudioFile(inputFile)
    collect = audio.AudioQuantumList()
    for b in audiofile.analysis.bars:                
        # all but the last beat
        collect.extend(b.children()[0:-1])
        if units.startswith("tatum"):
            # all but the last half (round down) of the last beat
            half = - (len(b.children()[-1].children()) // 2)
            collect.extend(b.children()[-1].children()[0:half])    
    out = audio.getpieces(audiofile, collect)
    out.save(outputFile)

if __name__ == '__main__':
    import sys
    try:
        units = sys.argv[-3]
        inputFilename = sys.argv[-2]
        outputFilename = sys.argv[-1]
    except:
        print usage
        sys.exit(-1)
    main(units, inputFilename, outputFilename)
