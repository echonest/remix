#1/usr/bin/env/python
#encoding: utf=8
"""
sorting.py

Sorts AudioQuanta (bars, beats, tatums) by various qualities, and resynthesizes them
Also sorts segments

By Thor Kell, 2012-11-02
"""

import echonest.audio as audio
usage = """
    python sorting.py <bars|beats|tatums> <confidence|duration> <input_filename> <output_filename> [reverse]

"""
def main(units, key, input_filename, output_filename):
    audiofile = audio.LocalAudioFile(input_filename)
    chunks = audiofile.analysis.__getattribute__(units)
    
    # Define the sorting function
    if key == 'confidence':
        sorting_function = lambda chunk: chunk.confidence
    if key == 'duration':
        sorting_function = lambda chunk: chunk.duration

    test_segs = chunks[0].segments()
    # chunk.get_max_pitch
    # chunk.get_average_timbres
    # chunk.get_max_loudness
    # chunk.get_average loudness
    print chunks[0]
    print test_segs

    sorted_chunks = sorted(chunks, key=sorting_function, reverse=reverse)    
#    out = audio.getpieces(audiofile, sorted_chunks)
#    out.encode(output_filename)

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
