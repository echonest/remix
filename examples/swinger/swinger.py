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
import dirac

from echonest.audio import LocalAudioFile, AudioData
from echonest.action import render, Playback, display_actions

def do_work(track, options):
    
    verbose = bool(options.verbose)
    
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
        if verbose:
            args = (beats.index(beat), dur, beat.duration-dur, stretch, beat.duration-stretch)
            print "Beat %d — split [%.3f|%.3f] — stretch [%.3f|%.3f] seconds" % args
    
    # get audio
    vecin = track.data[offset:int(beats[-1].start * track.sampleRate),:]
    # time stretch
    if verbose: 
        print "\nTime stretching..."
    vecout = dirac.timeScale(vecin, rates, track.sampleRate, 0)
    # build timestretch AudioData object
    ts = AudioData(ndarray=vecout, shape=vecout.shape, 
                    sampleRate=track.sampleRate, numChannels=vecout.shape[1], 
                    verbose=verbose)
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
    
    verbose = options.verbose
    track = None
    
    track = LocalAudioFile(args[0], verbose=verbose)
    if verbose:
        print "Computing swing . . ."
    # this is where the work takes place
    actions = do_work(track, options)
    
    if verbose:
        display_actions(actions)
    
    # Send to renderer
    name = os.path.splitext(os.path.basename(args[0]))
    sign = ('-','+')[float(options.swing) >= 0]
    name = name[0] + '_swing' + sign + str(int(abs(float(options.swing))*100)) +'.mp3'
    name = name.replace(' ','') 
    name = os.path.join(os.getcwd(), name) # TODO: use sys.path[0] instead of getcwd()?
    
    if verbose:
        print "Rendering... %s" % name
    render(actions, name, verbose=verbose)
    if verbose:
        print "Success!"
    return 1


if __name__ == "__main__":
    try:
        main()
    except Exception, e:
        print e
