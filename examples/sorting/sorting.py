#1/usr/bin/env/python
#encoding: utf=8
"""
sorting.py

Sorts AudioQuanta (bars, beats, tatums, segments) by various qualities, and resynthesizes them.

By Thor Kell, 2012-11-02
"""

import echonest.audio as audio
usage = """
    python sorting.py <bars|beats|tatums|segments> <confidence|duration|loudness>  <input_filename> <output_filename> [reverse]

"""
def main(units, key, input_filename, output_filename):
    audiofile = audio.LocalAudioFile(input_filename)
    chunks = audiofile.analysis.__getattribute__(units)
    
    # Define the sorting function
    if key == 'duration':
        sorting_function = lambda chunk: chunk.duration
    if key == 'confidence':
        if units == 'segments':
            print "WARNING:  segments have no confidence values"
        sorting_function = lambda chunk: chunk.confidence

    if key == 'loudness':
        # If we are not using segments, we need to get the mean of the loudness data of the segments for this chunk
        if units != 'segments':
            def sorting_function(chunk):
                loudness_average = 0
                for segment in chunk.segments():
                    loudness_average = loudness_average + segment.loudness_max
                return float(loudness_average) / len(chunk.segments())
        else:
            sorting_function = lambda chunk: index(chunk.loudness_max)

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
