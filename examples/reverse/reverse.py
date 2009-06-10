#!/usr/bin/env python
# encoding: utf=8

"""
reverse.py

Reverse the beats or segments of a song.

Originally created by Robert Ochshorn on 2008-06-11.  Refactored by
Joshua Lifton 2008-09-07.
"""

import echonest.audio as audio

usage = """
Usage: 
    python reverse.py <beats|segments> <inputFilename> <outputFilename.wav>

Example:
    python reverse.py beats YouCanCallMeAl.mp3 AlMeCallCanYou.mp3
"""

def main(toReverse, inputFilename, outputFilename):
    audioFile = audio.LocalAudioFile(inputFilename)
    if toReverse == 'beats' :
        chunks = audioFile.analysis.beats
    elif toReverse == 'segments' :
        chunks = audioFile.analysis.segments
    else :
        print usage
        return
    chunks.reverse()
    reversedAudio = audio.getpieces(audioFile, chunks)
    reversedAudio.encode(outputFilename)

if __name__ == '__main__':
    import sys
    try :
        toReverse = sys.argv[1]
        inputFilename = sys.argv[2]
        outputFilename = sys.argv[3]
    except :
        print usage
        sys.exit(-1)
    if not toReverse in ["beats", "segments"]:
        print usage
        sys.exit(-1)
    main(toReverse, inputFilename, outputFilename)
