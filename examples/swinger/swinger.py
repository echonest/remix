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
    
    if swing == 0:
        return Playback(track, 0, track.analysis.duration)
    
    beats = track.analysis.beats
    offset = int(beats[0].start * track.sampleRate)

    # compute rates
    rates = []
    for beat in beats[:-1]:
        # put swing
        if 0 < swing:
            rate1 = 1+swing
            dur = beat.duration/2.0
            stretch = dur * rate1
            rate2 = (beat.duration-stretch)/dur
        # remove swing
        else:
            rate1 = 1 / (1+abs(swing))
            dur = (beat.duration/2.0) / rate1
            stretch = dur * rate1
            rate2 = (beat.duration-stretch)/(beat.duration-dur)
        # build list of rates
        start1 = int(beat.start * track.sampleRate)
        start2 = int((beat.start+dur) * track.sampleRate)
        rates.append((start1-offset, rate1))
        rates.append((start2-offset, rate2))
        if verb == True: 
            print "Beat %d — split [%.3f|%.3f] — stretch [%.3f|%.3f] seconds" % (beats.index(beat), dur, beat.duration-dur, stretch, beat.duration-stretch)
    
    # get audio
    vecin = track.data[offset:int(beats[-1].start * track.sampleRate),:]
    # time stretch
    if verb == True: print "\nTime stretching..."
    vecout = dirac.timeScale(vecin, rates, track.sampleRate, 0)
    # build timestretch AudioData object
    ts = AudioData(ndarray=vecout, shape=vecout.shape, sampleRate=track.sampleRate, numChannels=vecout.shape[1])
    # initial and final playback
    pb1 = Playback(track, 0, beats[0].start)
    pb2 = Playback(track, beats[-1].start, track.analysis.duration-beats[-1].start)

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
    try:
        main()
    except Exception, e:
        print e
