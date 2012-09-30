#!/usr/bin/env python
# encoding: utf=8
"""
multivideo.py

Take a whole directory of video files and smash them together, by
beat, with a fairly simple algorithm.

By Ben Lacker, based on multitest.py by Adam Lindsay.
"""
import os, sys
from math import sqrt

from echonest import audio, video

usage = """
Usage: 
    python multivideo.py <inputSong> <inputDirectory> <outputFilename>

Example:
    python multivideo.py ../music/SingleLadies.mp3 ../videos mashedbeats.mpg
"""

def main(infile, directory, outfile):
    afile = audio.LocalAudioFile(infile)
    av = []
    ff = os.listdir(directory)
    for f in ff:
        # collect the files
        if f.rsplit('.', 1)[1].lower() in ['mp3', 'aif', 'aiff', 'aifc', 'wav', 'mpg', 'flv', 'mov', 'mp4']:
            av.append(video.loadav(os.path.join(directory,f)))
    num_files = len(av)
    # not sure the best way to handle these settings
    newv = video.EditableFrames(settings=av[0].video.settings)
    print >> sys.stderr, "Assembling beats.",
    for i, beat in enumerate(afile.analysis.beats):
        print >> sys.stderr, '.',
        vid = av[i%num_files]
        if beat.end > vid.audio.duration:
            # do something smart
            continue
        newv += vid.video[beat]
    outav = video.SynchronizedAV(audio=afile, video=newv)
    outav.save(outfile)

if __name__ == '__main__':
    try:
        infile = sys.argv[-3]
        directory = sys.argv[-2]
        outfile = sys.argv[-1]
    except:
        print usage
        sys.exit(-1)
    main(infile, directory, outfile)
