#!/usr/bin/env python
# encoding: utf=8
"""
one.py

Digest only the first beat of every bar.

By Ben Lacker, 2009-02-18.  
"""
# This line imports remix! 
import echonest.remix.audio as audio

usage = """
Usage: 
    python one.py <input_filename> <output_filename>

Example:
    python one.py EverythingIsOnTheOne.mp3 EverythingIsReallyOnTheOne.mp3
"""

# One outputs only the first beat of each bar!
# It does this by looping over the component bars of the track.
# Then, it adds the first beat of each bar to a list.
# That list is then used to create the output audio file.

def main(input_filename, output_filename):
    # This takes your input track, sends it to the analyzer, and returns the results.  
    audiofile = audio.LocalAudioFile(input_filename)

    # This gets a list of every bar in the track.  
    # You can manipulate this just like any other Python list!
    bars = audiofile.analysis.bars

    # This makes a new list of "AudioQuantums".  
    # Those are just any discrete chunk of audio:  bars, beats, etc.
    collect = audio.AudioQuantumList()

    # This loop puts the first item in the children of each bar into the new list. 
    # A bar's children are beats!  Simple as that. 
    for bar in bars:
        collect.append(bar.children()[0])

    # This assembles the pieces of audio defined in collect from the analyzed audio file.
    out = audio.getpieces(audiofile, collect)
    
    # This writes the newly created audio to the given file.  
    out.encode(output_filename)


    # The wrapper for the script.  
if __name__ == '__main__':
    import sys
    try:
        # This gets the filenames to read from and write to.
        input_filename = sys.argv[1]
        output_filename = sys.argv[2]
    except:
        # If things go wrong, exit!
        print usage
        sys.exit(-1)
    main(input_filename, output_filename)
