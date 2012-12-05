#!/usr/bin/env/python
#encoding: utf=8
"""
sorting_pitch.py

Sorts AudioQuanta (bars, beats, tatums, segments) by the maximum pitch.
Results can be modded by 0-11 to sort relative to C, C#, D, D#, etc.

By Thor Kell, 2012-11-02
"""

import echonest.remix.audio as audio
usage = """
    python sorting_pitch.py <bars|beats|tatums|segments> <0-11> <input_filename> <output_filename> [reverse]

"""
def main(units, key, input_filename, output_filename):
    audiofile = audio.LocalAudioFile(input_filename)
    chunks = audiofile.analysis.__getattribute__(units)
    key = int(key)
    
    def sorting_function(chunk):
        pitches = chunk.mean_pitches()
        return pitches.index(max(pitches)) - key % 12

    sorted_chunks = sorted(chunks, key=sorting_function, reverse=reverse)

    out = audio.getpieces(audiofile, sorted_chunks)
    out.encode(output_filename)

if __name__ == '__main__':
    import sys
    try:
        unit = sys.argv[1]
        key = sys.argv[2]
        input_filename = sys.argv[3]
        output_filename = sys.argv[4]
        if len(sys.argv) == 6 and sys.argv[5] == 'reverse':
            reverse = True  
        else:
            reverse = False

    except:
        print usage
        sys.exit(-1)
    main(unit, key, input_filename, output_filename)
