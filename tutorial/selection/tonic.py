#!/usr/bin/env python
# encoding: utf=8

"""
tonic.py

Digest all beats, tatums, or bars that start in the key of the song.
Demonstrates content-based selection filtering via AudioQuantumLists

Originally by Adam Lindsay, 2008-09-15.
Refactored by Thor Kell, 2012-11-01
"""
import echonest.remix.audio as audio

usage = """
Usage: 
    python tonic.py <tatums|beats|bars> <inputFilename> <outputFilename>

Example:
    python tonic.py beats HereComesTheSun.mp3 HereComesTheTonic.mp3
"""

ACCEPTED_UNITS = ["tatums", "beats", "bars"]

def main(units, inputFile, outputFile):
    audiofile = audio.LocalAudioFile(inputFile)
    tonic = audiofile.analysis.key['value']
    
    chunks = audiofile.analysis.__getattribute__(units)
    
    # Get the segments    
    all_segments = audiofile.analysis.segments
    
    # Find tonic segments
    tonic_segments = audio.AudioQuantumList(kind="segment")
    for segment in all_segments:
        pitches = segment.pitches
        if pitches.index(max(pitches)) == tonic:
            tonic_segments.append(segment)

    # Find each chunk that matches each segment
    out_chunks = audio.AudioQuantumList(kind=units) 
    for chunk in chunks:
        for segment in tonic_segments:
            if chunk.start >= segment.start and segment.end >= chunk.start:
                out_chunks.append(chunk)
                break
    
    out = audio.getpieces(audiofile, out_chunks)
    out.encode(outputFile)

if __name__ == '__main__':
    import sys
    try:
        units = sys.argv[-3]
        inputFilename = sys.argv[-2]
        outputFilename = sys.argv[-1]
    except:
        print usage
        sys.exit(-1)
    if not units in ACCEPTED_UNITS:
        print usage
        sys.exit(-1)
    main(units, inputFilename, outputFilename)
