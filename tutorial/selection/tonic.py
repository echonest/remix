#!/usr/bin/env python
# encoding: utf=8

"""
tonic.py

Digest all beats, tatums, or bars that start in the key of the song.
Demonstrates the content-based selection filtering in AudioQuantumLists.that()

Originally by Adam Lindsay, 2008-09-15.
"""
# This line imports remix! 
import echonest.remix.audio as audio
# This line imports descriptions from remix.
from echonest.selection import have_pitch_max, overlap_ends_of, overlap_starts_of

usage = """
Usage: 
    python tonic.py <tatums|beats|bars> <inputFilename> <outputFilename>

Example:
    python tonic.py beats HereComesTheSun.mp3 HereComesTheTonic.mp3
"""

# The list of rhythmic units that we can filter on
ACCEPTED_UNITS = ["tatums", "beats", "bars"]

def main(units, inputFile, outputFile):
    # This takes your input track, sends it to the analyzer, and returns the results.  
    audiofile = audio.LocalAudioFile(inputFile)

    # This gets the overall key of the track
    tonic = audiofile.analysis.key['value']
    
    # This gets a list of all of the selected unit in the track.  
    chunks = audiofile.analysis.__getattribute__(units)
    
    # This is a serious line!  
    # It means:  "segments that have the tonic as the max pitch and that overlap the start of the <units>"
    # Note the syntax:  ".that(do_something)". These work just the way you think they should
    # (That is, they act like list comprehensions for the given statement!)
    # Also, note that have_pitch_max and overlap are imported from selection.py
    segs = audiofile.analysis.segments.that(have_pitch_max(tonic)).that(overlap_starts_of(chunks))
    
    # Using the same synatx as the above line:
    # this line gets all rhythmic units that begin with the segment we found above
    outchunks = chunks.that(overlap_ends_of(segs))
    
    # This assembles the pieces of audio defined in collect from the analyzed audio file.
    out = audio.getpieces(audiofile, outchunks)
    
     # This writes the newly created audio to the given file.  
    out.encode(outputFile)

    # The wrapper for the script. 
if __name__ == '__main__':
    import sys
    try:
        # This gets the unit to work with, and filenames to read from and write to.
        units = sys.argv[-3]
        inputFilename = sys.argv[-2]
        outputFilename = sys.argv[-1]
    except:
        # If things go wrong, exit!
        print usage
        sys.exit(-1)
    if not units in ACCEPTED_UNITS:
        print usage
        sys.exit(-1)
    main(units, inputFilename, outputFilename)
