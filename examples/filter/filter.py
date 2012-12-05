#!/usr/bin/env/python
#encoding: utf=8
"""
filter.py

Filters lists of  AudioQuanta (bars, beats, tatums, segments) 
by various proporties, and resynthesizes them

'pitch' takes an integer a finds chunks that have a pitch maximum in the given index
'pitches' takes a list of integers (be sure to quote them on the command line:  "[0, 4, 7]")
 and finds chunks that have pitch maxima in those pitches - a simple chord-finder
'duration' takes a pair of integers (be sure to quote them on the command line:  "[7, 14]")
 or floats and finds chunks that overlap / are within that range in time
'louder' and 'softer' take a float and finds chunks that are louder or softer than the number
 (in dBFS, so 0.0 is the loudest)

By Thor Kell, 2012-11-14
"""

import echonest.remix.audio as audio

usage = """
    python filter.py <bars|beats|tatums|segments> <pitch|pitches|duration|louder|softer> <value> <input_filename> <output_filename>

"""
def main(units, key, value, input_filename, output_filename):
    audiofile = audio.LocalAudioFile(input_filename)
    chunks = audiofile.analysis.__getattribute__(units)
    
    if key == 'pitch':
        value = int(value);
    if key == 'pitches':
        value = eval(value)
        if type(value) != list:
            print usage
            sys.exit(-1)
    if key == 'duration':
        value = eval(value)
        duration_start = value[0]
        duration_end = value[1]
    if key == 'louder' or key == 'softer':
        value = float(value)
    
    filtered_chunks = []
    for chunk in chunks:
        if key == 'pitch':      
            pitches = chunk.mean_pitches()
            if pitches.index(max(pitches)) == value:        
                filtered_chunks.append(chunk)
   
        if key == 'pitches':
            max_indexes = []
            pitches = chunk.mean_pitches()
            max_pitches = sorted(pitches, reverse=True)
            for pitch in max_pitches:
                 max_indexes.append(pitches.index(pitch)) 
            
            if set(value) == set(max_indexes[0:len(value)]):
                filtered_chunks.append(chunk)

        if key == 'duration':
            if chunk.start < duration_end and chunk.end > duration_start:
                filtered_chunks.append(chunk)
            elif chunk.start > duration_end:
                break

        if key == 'louder':
            if chunk.mean_loudness() > value:
                filtered_chunks.append(chunk)

        if key == 'softer':
            if chunk.mean_loudness() < value:
                filtered_chunks.append(chunk)

    out = audio.getpieces(audiofile, filtered_chunks)
    out.encode(output_filename)

if __name__ == '__main__':
    import sys
    try:
        unit = sys.argv[1]
        key = sys.argv[2]
        value = sys.argv[3]
        input_filename = sys.argv[4]
        output_filename = sys.argv[5]

    except:
        print usage
        sys.exit(-1)
    main(unit, key, value, input_filename, output_filename)
