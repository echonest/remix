#!/usr/bin/env/python
#encoding: utf=8
"""
sorting.py

Sorts AudioQuanta (bars, beats, tatums, segments) by various qualities, and resynthesizes them.

By Thor Kell, 2012-11-02
"""
import echonest.remix.audio as audio
usage = """
    python sorting.py <bars|beats|tatums|segments> <confidence|duration|loudness>  <input_filename> <output_filename> [reverse]

"""
def main(units, key, input_filename, output_filename):
    audiofile = audio.LocalAudioFile(input_filename)
    chunks = audiofile.analysis.__getattribute__(units)

    # Define the sorting function
    if key == 'duration':
        def sorting_function(chunk):
            return chunk.duration

    if key == 'confidence':
        def sorting_function(chunk):
            if units != 'segments':
                return chunk.confidence
            else:
                # Segments have no confidence, so we grab confidence from the tatum
                return chunk.tatum.confidence

    if key == 'loudness':
        def sorting_function(chunk):
            return chunk.mean_loudness()
    
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
