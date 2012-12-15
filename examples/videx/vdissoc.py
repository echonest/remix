#!/usr/bin/env python
# encoding: utf=8

"""
vdissoc.py

The video version of step-by-section.py.

For each bar, take one of the nearest (in timbre) beats 
to the last beat, chosen from all of the beats that fall
on the one in this section. Repeat for all the twos, etc.

This version divides things by section, retaining the 
structure and approximate length of the original. The 
variation parameter, (_v_) means there's a roughly 
one in _v_ chance that the actual next beat is chosen. A 
musical M-x dissociated-press.

Originally by Adam Lindsay, 2009-06-27.
Refactored by Thor Kell, 2012-15-12
"""
import random
import numpy
from echonest.remix import video, audio

usage = """
Usage:
    python vdissoc.py inputFilenameOrUrl outputFilename [variation]

variation is the number of near candidates chosen from. [default=4]

Example:
    python vdissoc.py 'http://www.youtube.com/watch?v=Es7mk19wMrk' Seventh.mp4
"""
def main(infile, outfile, choices=4):
    if infile.startswith("http://"):
        av = video.loadavfromyoutube(infile)
    else:
        av = video.loadav(infile)

    meter = av.audio.analysis.time_signature['value']
    sections = av.audio.analysis.sections
    output = audio.AudioQuantumList()

    for section in sections:
        beats = []
        bars = section.children()
        for bar in bars:
            beats.extend(bar.children())
    
        if not bars or not beats:
            continue

        beat_array = []
        for m in range(meter):
            metered_beats = []
            for b in beats:
                if beats.index(b) % meter == m:
                    metered_beats.append(b)
            beat_array.append(metered_beats)

        # Always start with the first beat
        output.append(beat_array[0][0]);
        for x in range(1, len(bars) * meter):
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
    
    out = video.getpieces(av, output)
    out.save(outfile)

if __name__ == '__main__':
    import sys
    try:
        inputFilename = sys.argv[1]
        outputFilename = sys.argv[2]
        if len(sys.argv) > 3:
            variation = int(sys.argv[3])
        else:
            variation = 4
    except:
        print usage
        sys.exit(-1)
    main(inputFilename, outputFilename, variation)
