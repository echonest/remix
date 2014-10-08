#!/usr/bin/env python
# encoding: utf-8
"""
rhythmstring.py

Computes and prints a rhythm vector for a file - compare with beat starts.

The rhythm vector presents eight channels of onsets.
Each channel represents a band of frequency from 0 to 5512.5 Hz.
(Specifically, these are the 8 lowest bands in the MPEG-Audio 32 band filterbank.)

Created by Tristan Jehan on 2013-08-12, refactored by Thor Kell on 2014-10
Copyright (c) 2013 The Echo Nest. All rights reserved.
"""

import sys, os
import numpy as np
import zlib, base64
import json
import cPickle as pkl
import echonest.remix.audio as audio

usage = """
Usage: 
    python rhythmstring.py <input_filename>

Example:
    python rhythmstring.py IveGotRhythm.mp3
"""

# The rhythmstring format goes as follows:
# Fs Hop Nch <Nos Oi do_1 ... do_n> ... <Nos Oi do_1 ... do_n>

# where:
# Fs: sampling rate
# Hop: hop size
# Nch: number of echoprint channels
# Cm: channel index
# Nos: number of onsets
# Oi: intial onset frame
# do_n: number of frames to the next onset


def get_beat_starts(analysis):   
  beat_starts = []
  for b in analysis.beats:
    beats.append(float(b.start))
  return beat_starts

def decode_string(s):
  if s == None or s == "":
    return None
  l = [int(i) for i in s.split(' ')]
  Fs = l.pop(0)
  Hop = l.pop(0)
  frame_duration = float(Hop)/float(Fs)
  Nch = l.pop(0)
  onsets = []
  n = 0
  for i in range(Nch):
    N = l[n]
    n += 1
    for j in range(N):
      if j == 0: ons = [l[n]]
      else: ons.append(ons[j-1] + l[n])
      n += 1
    onsets.append(ons)
  new_onsets = []
  for ons in onsets:
    new_ons = []
    for o in ons:
      new_ons.append(o*frame_duration)
    new_onsets.append(new_ons)
  return new_onsets

def decompress_string(compressed_string):
  compressed_string = compressed_string.encode('utf8')
  if compressed_string == "":
    return None
  try:
    actual_string = zlib.decompress(base64.urlsafe_b64decode(compressed_string))
  except (zlib.error, TypeError):
    print "Could not decode base64 zlib string %s" % (compressed_string)
    return None
  return actual_string

def get_rhythm_data(analysis):
  beat_starts = get_beat_starts(analysis)
  rhythmstring = analysis.rhythmstring
  decompressed_string = decompress_string(rhythmstring)
  onsets = decode_string(decompressed_string)
  return beat_starts, onsets

def get_rhythm(analysis):
  onsets = get_rhythm_data(analysis)
  return onsets

def main(input_filename):
  audiofile = audio.LocalAudioFile(input_filename)
  onsets = get_rhythm(audiofile.analysis)
  print onsets

if __name__ == '__main__':
    import sys
    try:
        input_filename = sys.argv[1]
    except:
        print usage
        sys.exit(-1)
    main(input_filename)

