#1/usr/bin/env/python
#encoding: utf=8
"""
sorting.py

Sorts AudioQuanta (bars, beats, tatums, segments) by pitch.
Currently only sorts linearly, by semitones.  
Would be nice to put in the interval to work with.


By Thor Kell, 2012-11-02
"""

import echonest.audio as audio
usage = """
    python sorting.py <bars|beats|tatums|segments> <0-11> <0> <input_filename> <output_filename> [reverse]

"""
def main(units, key, interval, input_filename, output_filename):
    audiofile = audio.LocalAudioFile(input_filename)
    chunks = audiofile.analysis.__getattribute__(units)
    key = int(key)
    interval = int(interval)
    
    # For any chunk, return the maximum mean pitch
    if units != 'segments':
        def sorting_function(chunk):
            temp_pitches = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            for segment in chunk.segments():
                for index, pitch in enumerate(segment.pitches):
                    temp_pitches[index] = temp_pitches[index] + pitch

                mean_pitches = [pitch / len(chunk.segments()) for pitch in temp_pitches]

            if interval == 0:
                return mean_pitches.index(max(mean_pitches))- key % 12
            else:
                # figure out a way to do this that works with symmetrical interval
                return counter
    else:
        sorting_function = lambda chunk: chunk.pitches.index(max(chunk.pitches)) - key % 12

    sorted_chunks = sorted(chunks, key=sorting_function, reverse=reverse)
    
    # Debug print of the absolute pitches
    for chunk in sorted_chunks:
        temp_pitches = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for segment in chunk.segments():
            for index, pitch in enumerate(segment.pitches):
                temp_pitches[index] = temp_pitches[index] + pitch

            mean_pitches = [pitch / len(chunk.segments()) for pitch in temp_pitches]
        print mean_pitches.index(max(mean_pitches))

    out = audio.getpieces(audiofile, sorted_chunks)
    out.encode(output_filename)

if __name__ == '__main__':
    import sys
    try:
        unit = sys.argv[1]
        key = sys.argv[2]
        interval = sys.argv[3]
        input_filename = sys.argv[4]
        output_filename = sys.argv[5]
        if len(sys.argv) == 7 and sys.argv[6] == 'reverse':
            reverse = True  
        else:
            reverse = False

    except:
        print usage
        sys.exit(-1)
    main(unit, key, interval, input_filename, output_filename)
