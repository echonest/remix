#!/usr/bin/env python
# encoding: utf=8

"""
swinger.py
(name suggested by Jason Sundram)

Make your music swing (or un-swing).
Created by Tristan Jehan.
"""

from optparse import OptionParser
import os, sys

from echonest.audio import LocalAudioFile, AudioData
from echonest.action import render, Playback, display_actions
from echonest.cloud_support import AnalyzedAudioFile
from echonest.cloud import find_track

try:
    if hasattr(os, 'uname') and os.uname()[0] == 'Darwin':
        # The default dlopenflags setting, RTLD_NOW, causes us to look for stuff that's defined in -framework Carbon
        # and then barf. Let's take it nice and lazy instead.
        f = sys.getdlopenflags()
        sys.setdlopenflags(0)
        import dirac
        sys.setdlopenflags(f)
    else:
        import dirac
except Exception, e:
    sys.exit("Unable to load dirac, which is required for Crossmatch. Please install pydirac: %s" % e)

def do_work(track, options):
    
    verb = bool(options.verbose)
    # swing factor
    swing = float(options.swing)
    if swing < -0.9: swing = -0.9
    if swing > +0.9: swing = +0.9
    
    beats = track.analysis.beats
    offset = int(beats[0].start * track.sampleRate)
    
    # build rates
    rates = []
    for beat in beats:
        dur_2 = beat.duration/2.0
        start1 = int(beat.start * track.sampleRate)
        start2 = int((beat.start+dur_2) * track.sampleRate)
        stretch = dur_2 * (1+swing)
        rates.append((start1-offset, 1+swing))
        rates.append((start2-offset, ((beat.duration-stretch)/dur_2)))
        if verb == True: print "Beat %d — split [%.3f|%.3f] — stretch [%.3f|%.3f] seconds" % (beats.index(beat), dur_2, beat.duration-dur_2, stretch, beat.duration-stretch)

    # get audio
    vecin = track.data[offset:int((beats[-1].start + beats[-1].duration) * track.sampleRate),:]
    # initial and final playback
    pb1 = Playback(track, 0, beats[0].start)
    pb2 = Playback(track, beats[-1].start+beats[-1].duration, offset)
    # time stretch
    if verb == True: print "\nTime stretching..."
    vecout = dirac.timeScale(vecin, rates, track.sampleRate, 0)
    # build timestretch AudioData object
    ts = AudioData(ndarray=vecout, shape=vecout.shape, sampleRate=track.sampleRate, numChannels=vecout.shape[1])

    return [pb1, ts, pb2]

def main():
    usage = "usage: %s [options] <one_single_mp3>" % sys.argv[0]
    parser = OptionParser(usage=usage)
    parser.add_option("-s", "--swing", default=0.33, help="swing factor default=0.33")
    parser.add_option("-v", "--verbose", action="store_true", help="show results on screen")
    
    (options, args) = parser.parse_args()
    if len(args) < 1:
        parser.print_help()
        return -1
    
    track = None
    if len(args) == 2:
        track = find_track(args[0], args[1])
        if not track:
            print "Couldn't find %s by %s" % (args[0], args[1])
            return 1
    else:
        mp3 = args[0]
        
        if os.path.exists(mp3 + '.json'):
            track = AnalyzedAudioFile(mp3)
        else:
            track = LocalAudioFile(mp3)
    
    # this is where the work takes place
    actions = do_work(track, options)
    
    if bool(options.verbose) == True:
        display_actions(actions)
    
    # Send to renderer
    name = os.path.splitext(os.path.basename(args[0]))
    sign = ('-','+')[float(options.swing) >= 0]
    name = name[0]+'_swing'+sign+str(int(abs(float(options.swing))*100))+'.mp3'
    name = name.replace(' ','')
    
    print "Rendering..."
    render(actions, name)
    return 1


if __name__ == "__main__":
    #try:
    main()
    #except Exception, e:
    #    print e
