#!/usr/bin/env python
# encoding: utf=8

"""
reverse.py

Reverse the beats or segments of a song.

Originally created by Robert Ochshorn on 2008-06-11.  Refactored by
Joshua Lifton 2008-09-07.
"""

import echonest.remix.audio as audio

usage = """
Usage: 
    python reverse.py <beats|segments> <inputFilename> <outputFilename.wav>

Example:
    python reverse.py beats YouCanCallMeAl.mp3 AlMeCallCanYou.mp3
"""

# Reverse plays the beats or segments of a sound backwards!
# It does this by getting a list of every beat or segment in a track.
# Then, it reverses the list.
# This reversed list is used to create the output file.

def main(toReverse, inputFilename, outputFilename):
    # This takes your input track, sends it to the analyzer, and returns the results.  
    audioFile = audio.LocalAudioFile(inputFilename)

    # Checks what sort of reversing we're doing.
    if toReverse == 'beats' :
        # This gets a list of every beat in the track.  
        chunks = audioFile.analysis.beats
    elif toReverse == 'segments' :
        # This gets a list of every segment in the track.  
        # Segments are the smallest chunk of audio that Remix deals with
        chunks = audioFile.analysis.segments
    else :
        print usage
        return

    # Reverse the list!
    chunks.reverse()

    # This assembles the pieces of audio defined in chunks from the analyzed audio file.
    reversedAudio = audio.getpieces(audioFile, chunks)
    # This writes the newly created audio to the given file.  
    reversedAudio.encode(outputFilename)

    # The wrapper for the script.  
if __name__ == '__main__':
    import sys
    try :
        # This gets what sort of reversing we're doing, and the filenames to read from and write to.
        toReverse = sys.argv[1]
        inputFilename = sys.argv[2]
        outputFilename = sys.argv[3]
    except :
        # If things go wrong, exit!
        print usage
        sys.exit(-1)
    if not toReverse in ["beats", "segments"]:
        print usage
        sys.exit(-1)
    main(toReverse, inputFilename, outputFilename)
