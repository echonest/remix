#!/usr/bin/env python
# encoding: utf=8

"""
kernels.py

Take a whole directory of audio files and smash them together, by
beat, with a fairly simple algorithm. Demonstrates the use of 
deferred audio file loading used in conjunction with render_serially(),
which allow one to remix countless files without running out of memory
too soon.

Originally by Adam Lindsay, 2000-05-05.
"""

import os, sys, os.path
import time
from math import sqrt

import echonest.audio as audio

usage = """
Usage: 
    python kernels.py <inputDirectory> <outputFilename> <beats>

Example:
    python kernels.py /path/to/mp3s popped.mp3 320
"""

SLEEPTIME = 0.5

def main(num_beats, directory, outfile):
    # register the two special effects we need. Since we only make 
    #  AudioQuanta shorter, TimeTruncate is a good choice.
    aud = []
    ff = os.listdir(directory)
    for f in ff:
        # collect the files
        if f.rsplit('.', 1)[1].lower() in ['mp3', 'aif', 'aiff', 'aifc', 'wav']:
            # the new defer kwarg doesn't load the audio until needed
            filename = os.path.join(directory, f)
            aud.append(audio.LocalAudioFile(filename, defer= True))
        # mind the rate limit
    
    num_files = len(aud)
    
    print >> sys.stderr, "Sorting files by key..."
    # sort by key signature: with enough files, it'll sound 
    # like it's always going up in pitch
    aud.sort(key=keysig)
    
    x = audio.AudioQuantumList()
    
    print >> sys.stderr, "Assembling beats.",
    for w in range(num_beats):
        print >> sys.stderr, '.',
        
        # cycle through the audio files (with a different period)
        ssong = aud[w%(num_files-1)].analysis
        
        # cycle through the beats
        s = ssong.beats[w%len(ssong.beats)]
        
        # run an accelerando, and truncate the beats if the reference is shorter
        new_dur = pow(2, -3.0 * w / num_beats)
        if new_dur < s.duration:
            shorter = audio.TimeTruncateLength(new_dur)
            s = shorter(s)
        
        # sort-of normalize based on overall track volume with a crescendo
        level_change = audio.LevelDB(-15 - ssong.loudness + (6.0 * w / num_beats))
        s = level_change(s)
        
        # cycle through the songs (out of phase with 's')
        tsong = aud[(w-1)%num_files].analysis
        
        # cycle through the beats (out of phase)
        t = tsong.beats[w%len(tsong.beats)]
        
        # have a more dramatic volume change
        level_change = audio.LevelDB(-18 - tsong.loudness + (9.0 * w / num_beats))
        t = level_change(t)
        # also note that there will be significant overlap of the un-truncated 't' beats 
        #  by the end, making things louder overall
        
        # glue the two beats together
        x.append(audio.Simultaneous([s, t]))
        
    print >> sys.stderr, "\nStarting rendering pass..."
    
    then = time.time()
    # call render_sequentially() with no arguments, and then it calls itself with
    #  contextual arguments for each source, for each AudioQuantum. It's a lot of
    #  tree-walking, but each source file gets loaded once (and takes itself from)
    #  memory when its rendering pass finishes.
    x.render().encode(outfile)
    
    print >> sys.stderr, "%f sec for rendering" % (time.time() - then,)
    
    print >> sys.stderr, "Outputting XML: each source makes an API call for its metadata."

def keysig(audiofile):
    return int(audiofile.analysis.key['value'])

if __name__ == '__main__':
    try:
        directory = sys.argv[-3]
        outfile = sys.argv[-2]
        num_beats = int(sys.argv[-1])
    except:
        print usage
        sys.exit(-1)
    main(num_beats, directory, outfile)

