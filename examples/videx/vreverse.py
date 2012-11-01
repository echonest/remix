#!/usr/bin/env python
# encoding: utf-8
"""
vreverse.py

Created by Ben Lacker on 2009-06-19.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

import sys
import os

from echonest import video

usage = """
Usage: 
    python vreverse.py <beats|tatums> <inputFilename> <outputFilename>

Example:
    python vreverse.py beats YouCanCallMeAl.mpg AlMeCallCanYou.mpg
"""


def main(toReverse, inputFilename, outputFilename):
    if inputFilename.startswith("http://"):
        av = video.loadavfromyoutube(inputFilename)
    else:
        av = video.loadav(inputFilename)
    if toReverse == 'tatums':
        chunks = av.audio.analysis.tatums
    elif toReverse == 'beats':
        chunks = av.audio.analysis.beats
    chunks.reverse()
    out = video.getpieces(av, chunks)
    out.save(outputFilename)

if __name__ == '__main__':
    try :
        toReverse = sys.argv[1]
        inputFilename = sys.argv[2]
        outputFilename = sys.argv[3]
    except :
        print usage
        sys.exit(-1)
    if not toReverse in ["beats", "tatums"]:
        print usage
        sys.exit(-1)
    main(toReverse, inputFilename, outputFilename)
