#!/usr/bin/env python
# encoding: utf-8
"""
test_dirac.py

Test Dirac LE Time Stretcher.

Created by Tristan Jehan on 2010-04-22.
"""
import math, os, sys
from echonest import audio

import dirac
    
USAGE = """
Usage:
    python test_dirac.py <input_filename>
Example:
    python test_dirac.py will.wav
"""

def main():
    
    try:
        in_filename = sys.argv[1]
    except Exception:
        print USAGE
        sys.exit(-1)

    afile = audio.LocalAudioFile(in_filename)
    vecin = afile.data
    
    # ------------------------------------------------------------------------------------
    # Single time-stretch
    # ------------------------------------------------------------------------------------
    rate = 1.25 # 25% slower
    quality = 0 # fast processing
    
    print "Time Stretching with single rate", rate
    # arguments are:
    # 1) a numpy array of size N x C, where N is a number of samples, and C the number of channels (1 or 2)
    # 2) a float representing the time-stretching rate, e.g. 0.5 for twice as short, and 2.0 for twice as long
    # 3) an integer representing the sample rate of the input signal, e.g. 44100
    # 4) an optional integer representing the processing quality and speed between the default 0 (fastest, lowest quality) and 2 (slowest, highest quality)
    vecout = dirac.timeScale(vecin, rate, afile.sampleRate, quality)
    
    # output audio
    out = audio.AudioData(ndarray=vecout, shape=vecout.shape, sampleRate=afile.sampleRate, numChannels=vecout.shape[1])
    out_filename = 'out_single_rate.wav'
    print "Writing file", out_filename
    out.encode(out_filename)
    
    # ------------------------------------------------------------------------------------
    # Varying time-stretch
    # ------------------------------------------------------------------------------------
    # This example will linearly change the speed from 'rate' to 1.0 in 'numChunks' chunks
    numChunks = 16 # divide the signal into 16 chunks
    sizeChunk = int(vecin.shape[0] / numChunks)
    incRate = (1.0-rate) / (numChunks-1)
    
    # first tuple must start at index 0
    index = 0
    rates = [(index, rate)]
    for i in xrange(numChunks-1):
        index += sizeChunk
        rate += incRate
        rates.append((index, rate))
    
    print "Time Stretching with list of rates", rates
    # arguments are:
    # 1) a numpy array of size N x C, where N is a number of samples, and C the number of channels (1 or 2)
    # 2) a list of tuples each representing (a sample index, a rate). First index must be 0.
    # 3) an integer representing the sample rate of the input signal, e.g. 44100
    # 4) an optional integer representing the processing quality and speed between the default 0 (fastest, lowest quality) and 2 (slowest, highest quality)
    vecout = dirac.timeScale(vecin, rates, afile.sampleRate, quality)
    out = audio.AudioData(ndarray=vecout, shape=vecout.shape, sampleRate=afile.sampleRate, numChannels=vecout.shape[1])

    out_filename = 'out_list_rates.wav'
    print "Writing file", out_filename
    out.encode(out_filename)

if __name__ == '__main__':
    main()

