#!/usr/bin/env python
# encoding: utf=8
"""
save.py

Save an Echo Nest analysis as a local file. You can save analysis by using .save()
You can then load them by simply calling audio.LocalAudioFile('the_file.analysis.en')

Note that save() saves to the same location as the initial file, and 
creates a corresponding .wav file.  Moving the .wav file will break things!

By Thor Kell, 10-2012
"""

usage = """
Usage: 
    python save.py <input_filename>

Example:
    python save.py SaveMe.mp3 
"""

import echonest.remix.audio as audio

def main(input_filename):
    audiofile = audio.LocalAudioFile(input_filename)
    audiofile.save()
    print "Saved anaylsis for %s" % input_filename


if __name__ == '__main__':
    import sys
    try:
        input_filename = sys.argv[1]
    except: 
        print usage
        sys.exit(-1)
    main(input_filename)

