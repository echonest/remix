#!/usr/bin/env/python
#encoding: utf=8
"""
filter.py

Filters lists of  AudioQuanta (bars, beats, tatums, segments) 
by various qualities, and resynthesizes them

By Thor Kell, 2012-11-14
"""

import echonest.audio as audio

usage = """
    python filter.py <bars|beats|tatums|segments> <pitch> <value> <input_filename> <output_filename>

"""
def main(units, key, value, input_filename, output_filename):
    audiofile = audio.LocalAudioFile(input_filename)
    chunks = audiofile.analysis.__getattribute__(units)
    value = int(value);
    
    filtered_chunks = []
    for chunk in chunks:
        # Filter by which pitch is the most prominant
        if key == 'pitch':      
            pitches = chunk.mean_pitches()
            if pitches.index(max(pitches)) == value:        
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
