#!/usr/bin/env python
# encoding: utf=8

"""
lopside.py

Cut out the final beat or group of tatums in each bar.
Demonstrates the beat hierarchy navigation in AudioQuantum

Originally by Adam Lindsay, 2009-01-19.
"""

# This line imports remix! 
import echonest.remix.audio as audio
import sys

usage = """
Usage: 
    python lopside.py [tatum|beat] <inputFilename> <outputFilename>
Beat is selected by default.

Example:
    python lopside.py beat aha.mp3 ahawaltz.mp3
"""

# Lopside changes the meter of a track!
# It does this by removing the last beat of every bar.
# So a song that is in 4 will be in 3.
# It does this by looping over the component bars of the track.
# Then, it adds all but the last beat of each bar to a list.
# That list is then used to create the output audio file.

def main(units, inputFile, outputFile):
    # This takes your input track, sends it to the analyzer, and returns the results. 
    audiofile = audio.LocalAudioFile(inputFile)

    # This makes a new list of "AudioQuantums".  
    # Those are just any discrete chunk of audio:  bars, beats, etc
    collect = audio.AudioQuantumList()

    # If the analysis can't find any bars, stop!
    # (This might happen with really ambient music)
    if not audiofile.analysis.bars:
        print "No bars found in this analysis!"
        print "No output."
        sys.exit(-1)

    # This loop puts all but the last of each bar into the new list! 
    for b in audiofile.analysis.bars[0:-1]:                
        collect.extend(b.children()[0:-1])

        # If we're using tatums instead of beats, we want all but the last half (round down) of the last beat
        # A tatum is the smallest rhythmic subdivision of a beat -- http://en.wikipedia.org/wiki/Tatum_grid     
        if units.startswith("tatum"):
            half = - (len(b.children()[-1].children()) // 2)
            collect.extend(b.children()[-1].children()[0:half])

    # Endings were rough, so leave everything after the start of the final bar intact:
    last = audio.AudioQuantum(audiofile.analysis.bars[-1].start,
                              audiofile.analysis.duration - 
                                audiofile.analysis.bars[-1].start)
    collect.append(last)

    # This assembles the pieces of audio defined in collect from the analyzed audio file.
    out = audio.getpieces(audiofile, collect)

    # This writes the newly created audio to the given file.  
    out.encode(outputFile)

    # The wrapper for the script.  
if __name__ == '__main__':
    try:
        # This gets the units type, and the filenames to read from and write to.
        units = sys.argv[-3]
        inputFilename = sys.argv[-2]
        outputFilename = sys.argv[-1]
    except:
        # If things go wrong, exit!
        print usage
        sys.exit(-1)
    main(units, inputFilename, outputFilename)
