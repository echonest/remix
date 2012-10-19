#!/usr/bin/env python
# encoding: utf=8
"""
save.py

Save an Echo Nest analysis as a local file. You can save analysis by using .save()
You can then load them by simply calling audio.LocalAudioFile('the_saved_file')

Note that save() saves to the same location as the initial file, and 
creates a corresponding .wav file.  Moving the .wav file will break things!

By Thor Kell, 10-2012
"""

usage = """
Usage: 
    python save.py <input_filename> <output_filename>

Example:
    python save.py EverythingIsOnTheOne.mp3 EverythingIsReallyOnTheOne.mp3
"""

import echonest.audio as audio

def main(input_filename, output_filename):
    # This is where the magic happens.  
    audiofile = audio.LocalAudioFile(input_filename)
    audiofile.save()

    # Get the first beats, just to test...
    bars = audiofile.analysis.bars
    collect = audio.AudioQuantumList()
    for bar in bars:
        collect.append(bar.children()[0])
    out = audio.getpieces(audiofile, collect)
    out.encode(output_filename)

if __name__ == '__main__':
    import sys
    try:
        input_filename = sys.argv[1]
        output_filename = sys.argv[2]
    except: 
        print usage
        sys.exit(-1)
    main(input_filename, output_filename)

