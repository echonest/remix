#!/usr/bin/env python
# encoding: utf=8

"""
step-by-pitch.py

For each bar, take one of the nearest (in pitch) beats 
to the last beat, chosen from all of the beats that fall
on the one. Repeat for all the twos, etc.

The variation parameter, (_v_) means there's a roughly 
one in _v_ chance that the actual next beat is chosen. The 
length is the length in bars you want it to go on.

Originally by Adam Lindsay, 2009-03-10.
"""

import random

import echonest.audio as audio
from echonest.sorting import *
from echonest.selection import *

usage = """
Usage:
    python step-by-pitch.py inputFilename outputFilename [variation [length]]

variation is the number of near candidates chosen from. [default=4]
length is the number of bars in the final product. [default=40]

Example:
    python step-by-pitch.py Discipline.mp3 SpicDinLie.mp3 3 60
"""
def main(infile, outfile, choices=4, bars=40):
    audiofile = audio.LocalAudioFile(infile)
    meter = audiofile.analysis.time_signature['value']
    fade_in = audiofile.analysis.end_of_fade_in
    fade_out = audiofile.analysis.start_of_fade_out
    segments = audiofile.analysis.segments.that(are_contained_by_range(fade_in, fade_out))
    beats = audiofile.analysis.beats.that(are_contained_by_range(segments[0].start, segments[-1].end))
    
    outchunks = audio.AudioQuantumList()
    
    b = []
    segstarts = []
    for m in range(meter):
        b.append(beats.that(are_beat_number(m)))
        segstarts.append(segments.that(overlap_starts_of(b[m])))
        
    now = b[0][0]
    
    for x in range(0, bars * meter):
        beat = x % meter
        next_beat = (x + 1) % meter
        now_end_segment = segments.that(contain_point(now.end))[0]
        next_candidates = segstarts[next_beat].ordered_by(pitch_distance_from(now_end_segment))
        next_choice = next_candidates[random.randrange(min(choices, len(next_candidates)))]
        next = b[next_beat].that(start_during(next_choice))[0]
        outchunks.append(now)
        print now.context_string()
        now = next
    
    out = audio.getpieces(audiofile, outchunks)
    out.encode(outfile)
    
    
def are_beat_number(beat):
    def fun(x):        
        if x.local_context()[0] == beat:
            return x
    return fun

#
if __name__ == '__main__':
    import sys
    try:
        inputFilename = sys.argv[1]
        outputFilename = sys.argv[2]
        if len(sys.argv) > 3:
            variation = int(sys.argv[3])
        else:
            variation = 4
        if len(sys.argv) > 4:
            length = int(sys.argv[4])
        else:
            length = 40
    except:
        print usage
        sys.exit(-1)
    main(inputFilename, outputFilename, variation, length)
