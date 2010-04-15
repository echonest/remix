#!/usr/bin/env python
# encoding: utf=8
"""
one.py

Digest only the first beat of every bar, without local audio.

Originally by Ben Lacker, 2009-02-18, adapted by Jason Sundram 2010-04-15.
"""
import echonest.cloud as cloud
import echonest.audio as audio
from echonest.selection import have_pitch_max,have_pitches_max

usage = """
Usage: 
    python one.py <artist> <title (in quotes if necessary)> <output_filename>

Example:
    python one.py EverythingIsOnTheOne.mp3 EverythingIsReallyOnTheOne.mp3
"""

def main(artist, title, output_filename):
    audiofile = cloud.find_track(artist, title)
    if not audiofile:
        print 'Unable to find a track with artist "%s" and title "%s"' % (artist, title)
        return;
    
    bars = audiofile.analysis.bars
    collect = audio.AudioQuantumList()
    for bar in bars:
        collect.append(bar.children()[0])
    out = audio.getpieces(audiofile, collect)
    out.encode(output_filename)

if __name__ == '__main__':
    import sys
    try:
        artist = sys.argv[1]
        title = sys.argv[2]
        output_filename = sys.argv[3]
    except:
        print usage
        sys.exit(-1)
    main(artist, title, output_filename)
