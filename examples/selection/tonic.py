#!/usr/bin/env python
# encoding: utf=8

"""
tonic.py

Digest all beats, tatums, or bars that start in the key of the song.
Demonstrates the content-based selection filtering in AudioQuantumLists.that()

Originally by Adam Lindsay, 2008-09-15.
"""
import md5
import echonest.audio as audio
from echonest.selection import have_pitch_max

usage = """
Usage: 
    python tonic.py <tatums|beats|bars> <inputFilename> <outputFilename>

Example:
    python tonic.py beats HereComesTheSun.mp3 HereComesTheTonic.wav
"""


def main(units, inputFile, outputFile):
    audiofile = audio.AudioFile(inputFile)
    tonic = audiofile.analysis.key[0]
    
    if units in ["tatums", "beats", "bars"]:
        chunks = audiofile.analysis.__getattribute__(units)
    else:
        print usage
        return
    
    # "segments that have the tonic as the max pitch and that overlap the start of the <units>"
    # (have_pitch_max() is imported from selection.py)
    segs = audiofile.analysis.segments.that(have_pitch_max(tonic)).that(overlap_starts_of(chunks))
    
    # "<units> that begin with the above-found segments"
    outchunks = chunks.that(overlap_ends_of(segs))
    
    out = audio.getpieces(audiofile, outchunks)
    out.save(outputFile)

# New selection filters that take lists of AudioQuanta
def overlap_ends_of(aqs): 
    def fun(x): 
        for aq in aqs: 
            if x.start <= aq.start + aq.duration and x.start + x.duration >= aq.start + aq.duration: 
                return x 
        return None 
    return fun 

def overlap_starts_of(aqs):
    def fun(x):
        for aq in aqs: 
            if x.start <= aq.start and x.start + x.duration >= aq.start:
                return x
        return None
    return fun


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
