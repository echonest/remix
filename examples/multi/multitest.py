#!/usr/bin/env python
# encoding: utf=8

"""
multitest.py

Take a whole directory of audio files and smash them together, by
beat, with a fairly simple algorithm. Demonstrates the use of 
deferred audio file loading used in conjunction with render_serially(),
which allow one to remix countless files without running out of memory
too soon. Also outputs a "score" in XML.

Originally by Adam Lindsay, 2000-05-05.
"""

import os, sys
import time
from math import sqrt

from echonest import audio

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
            aud.append(audio.LocalAudioFile(os.path.join(directory,f)))
        # mind the rate limit
        time.sleep(SLEEPTIME)
    
    num_files = len(aud)
    x = audio.AudioQuantumList()
    
    print >> sys.stderr, "Assembling beats.",
    for w in range(num_beats):
        if w < num_files:
            # while we're still caching these results, slow down for the rate limit
            time.sleep(SLEEPTIME)
        print >> sys.stderr, '.',
        ssong = aud[w%num_files].analysis
        s = ssong.beats[w%len(ssong.beats)]
        x.append(s)
    
    print >> sys.stderr, "\nStarting rendering pass..."
    
    then = time.time()
    # call render_sequentially() with no arguments, and then it calls itself with
    #  contextual arguments for each source, for each AudioQuantum. It's a lot of
    #  tree-walking, but each source file gets loaded once (and takes itself from)
    #  memory when its rendering pass finishes.
    x.render().encode(outfile)
    
    print >> sys.stderr, "%f sec for rendering" % (time.time() - then,)
    
    print >> sys.stderr, "Outputting XML: each source makes an API call for its metadata."
    # output an XML file, for debugging purposes
    y = open(outfile.rsplit('.', 1)[0] + '.xml', 'w')
    y.write(x.toxml().dom.toprettyxml())
    y.close()

if __name__ == '__main__':
    try:
        directory = sys.argv[-3]
        outfile = sys.argv[-2]
        num_beats = int(sys.argv[-1])
    except:
        print usage
        sys.exit(-1)
    main(num_beats, directory, outfile)

