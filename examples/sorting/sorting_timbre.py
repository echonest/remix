#!/usr/bin/env/python
#encoding: utf=8
"""
sorting_timbre.py

Sorts AudioQuanta (bars, beats, tatums, segments) by timbral bin (0-11).
By Thor Kell, 2012-11-14
"""

import echonest.remix.audio as audio
usage = """
    python sorting.py <bars|beats|tatums|segments> <0-11> <input_filename> <output_filename> [reverse]

"""
def main(units, timbre_bin, input_filename, output_filename):
    audiofile = audio.LocalAudioFile(input_filename)
    chunks = audiofile.analysis.__getattribute__(units)
    timbre_bin = int(timbre_bin)
    
    # For any chunk, return the timbre value of the given bin
    def sorting_function(chunk):
        timbre = chunk.mean_timbre()
        return timbre[timbre_bin]

    sorted_chunks = sorted(chunks, key=sorting_function, reverse=reverse)

    import pdb
    #pdb.set_trace()

    out = audio.getpieces(audiofile, sorted_chunks)
    out.encode(output_filename)

if __name__ == '__main__':
    import sys
    try:
        unit = sys.argv[1]
        timbre_bin = sys.argv[2]
        input_filename = sys.argv[3]
        output_filename = sys.argv[4]
        if len(sys.argv) == 6 and sys.argv[5] == 'reverse':
            reverse = True  
        else:
            reverse = False

    except:
        print usage
        sys.exit(-1)
    main(unit, timbre_bin, input_filename, output_filename)
