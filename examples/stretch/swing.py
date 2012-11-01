#!/usr/bin/env python
# encoding: utf-8
"""
swing.py

Distort the tatums in time to achieve a swung beat.

Created by Adam T. Lindsay on 2009-04-02.
"""

from echonest import audio, modify

usage = """
Usage:
    python swing.py <inputFilename> <outputFilename> <percent>
    
"cheap" or "underwater" signifies which of the time-altering algorithms is used.
"underwater" is significantly more computationally expensive.

Example:
    python swing.py Discipline.mp3 Disciswing.mp3 60 
"""

def main(inputFilename, outputFilename, swing):
    
    infile = audio.LocalAudioFile(inputFilename)
    tats = infile.analysis.tatums
    st = modify.Modify()
    collect = []
    
    for x in tats:
        y, z = x.local_context()
        if y < z/2.:
            ratio = swing / (((z + 1) // 2) / float(z))
        else:
            ratio = (1. - swing) / (1 - ((z + 1) // 2) / float(z))
        new = st.shiftTempo(infile[x], 1./ratio)
        print "Expected:\t%1.3f\tActual:  \t%1.3f" % (x.duration * ratio, float(len(new))/new.sampleRate)
        collect.append(new)
    out = audio.assemble(collect)
    out.encode(outputFilename)

def swung_tatums(swing):
    def fun(x):
        y, z = x.local_context()
        if y < z/2.:
            x.duration *= swing / (((z + 1) // 2) / float(z))
        else:
            x.duration *= (1. - swing) / (1 - ((z + 1) // 2) / float(z))
        return x
    return fun

if __name__ == '__main__':
    import sys
    try :
        inputFilename = sys.argv[1]
        outputFilename = sys.argv[2]
        swing = float(sys.argv[3]) / 100.
    except :
        print usage
        sys.exit(-1)
    main(inputFilename, outputFilename, swing)

