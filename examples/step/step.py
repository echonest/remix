#!/usr/bin/env python
# encoding: utf=8

"""
step.py

For each bar, take one of the nearest (in timbre) beats 
to the last beat, chosen from all of the beats that fall
on the one. Repeat for all the twos, etc.

The variation parameter, (_v_) means there's a roughly 
one in _v_ chance that the actual next beat is chosen. The 
length is the length in bars you want it to go on.

Originally by Adam Lindsay, 2009-03-10.
Refactored by Thor Kell, 2012-12-12
"""

import random
import numpy
import echonest.remix.audio as audio

usage = """
Usage:
    python step.py inputFilename outputFilename [variation [length]]

variation is the number of near candidates chosen from. [default=4]
length is the number of bars in the final product. [default=40]

Example:
    python step.py Discipline.mp3 Undisciplined.mp3 4 100
"""

def main(infile, outfile, choices=4, bars=40):
    audiofile = audio.LocalAudioFile(infile)
    meter = audiofile.analysis.time_signature['value']
    fade_in = audiofile.analysis.end_of_fade_in
    fade_out = audiofile.analysis.start_of_fade_out

    beats = []
    for b in audiofile.analysis.beats:
        if b.start > fade_in or b.end < fade_out:
            beats.append(b)
    output = audio.AudioQuantumList()
    
    beat_array = []
    for m in range(meter):
        metered_beats = []
        for b in beats:
            if beats.index(b) % meter == m:
                metered_beats.append(b)
        beat_array.append(metered_beats)
    
    # Always start with the first beat
    output.append(beat_array[0][0]);
    for x in range(1, bars * meter):
        meter_index = x % meter
        next_candidates = beat_array[meter_index]

        def sorting_function(chunk, target_chunk=output[-1]):
            timbre = chunk.mean_timbre()
            target_timbre = target_chunk.mean_timbre()
            timbre_distance = numpy.linalg.norm(numpy.array(timbre) - numpy.array(target_timbre))
            return timbre_distance

        next_candidates = sorted(next_candidates, key=sorting_function)
        next_index = random.randint(0, min(choices, len(next_candidates) - 1))
        output.append(next_candidates[next_index])
    
    out = audio.getpieces(audiofile, output)
    out.encode(outfile)
    

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
