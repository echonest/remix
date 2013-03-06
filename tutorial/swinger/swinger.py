#!/usr/bin/env python
# encoding: utf=8

"""
swinger.py
(name suggested by Jason Sundram)

Make your music swing (or un-swing).
Created by Tristan Jehan.
"""

# These lines import other things.  
from optparse import OptionParser
import os, sys
import dirac

# These line import specific things from Remix! 
from echonest.remix.audio import LocalAudioFile, AudioData
from echonest.action import render, Playback, display_actions


# Swinger is much more complex than the prior examples!  
# Hold on, and we'll try to make everything make sense
# Swinger returns a swung version of the track.
# That is to say, that every second eighth note in the track is swung:  
# they occur later later than they otherwise would.
# It does this by timestretching the first eighth note to make it longer,
# and by timestretching the second eighth note to make it shorter.

    # This is the function that does the swingin'
def do_work(track, options):
    
    verbose = bool(options.verbose)
    
    # This gets the swing factor
    swing = float(options.swing)
    if swing < -0.9: swing = -0.9
    if swing > +0.9: swing = +0.9
    
    # If there's no swing, return the original tune
    if swing == 0:
        return Playback(track, 0, track.analysis.duration)
    
    # This gets the beat and the where the beats strt
    beats = track.analysis.beats
    offset = int(beats[0].start * track.sampleRate)

    # compute rates
    rates = []
    # This is where the magic happens:
    # For each beat, compute how much to stretch / compress each half of each beat
    for beat in beats[:-1]:
        # This adds swing:
        if 0 < swing:
            rate1 = 1+swing
            dur = beat.duration/2.0
            stretch = dur * rate1
            rate2 = (beat.duration-stretch)/dur
        # This removes swing
        else:
            rate1 = 1 / (1+abs(swing))
            dur = (beat.duration/2.0) / rate1
            stretch = dur * rate1
            rate2 = (beat.duration-stretch)/(beat.duration-dur)
        # This builds the list of swing rates for each beat
        start1 = int(beat.start * track.sampleRate)
        start2 = int((beat.start+dur) * track.sampleRate)
        rates.append((start1-offset, rate1))
        rates.append((start2-offset, rate2))
        if verbose:
            args = (beats.index(beat), dur, beat.duration-dur, stretch, beat.duration-stretch)
            print "Beat %d — split [%.3f|%.3f] — stretch [%.3f|%.3f] seconds" % args
    
    # This gets all the audio, from the
    vecin = track.data[offset:int(beats[-1].start * track.sampleRate),:]
    # This block does the time stretching
    if verbose: 
        print "\nTime stretching..."
    # Dirac is a timestretching tool that comes with remix.
    vecout = dirac.timeScale(vecin, rates, track.sampleRate, 0)
    # This builds the timestretched AudioData object
    ts = AudioData(ndarray=vecout, shape=vecout.shape, 
                    sampleRate=track.sampleRate, numChannels=vecout.shape[1], 
                    verbose=verbose)
     # Create playback objects (just a collection of audio) for the first and last beat
    pb1 = Playback(track, 0, beats[0].start)
    pb2 = Playback(track, beats[-1].start, track.analysis.duration-beats[-1].start)
    
    # Return the first beat, the timestreched beats, and the last beat
    return [pb1, ts, pb2]

    # The main function!
def main():
    # This setups up a parser for the various options
    usage = "usage: %s [options] <one_single_mp3>" % sys.argv[0]
    parser = OptionParser(usage=usage)
    parser.add_option("-s", "--swing", default=0.33, help="swing factor default=0.33")
    parser.add_option("-v", "--verbose", action="store_true", help="show results on screen")
    
    # If we don't have enough options, exit!
    (options, args) = parser.parse_args()
    if len(args) < 1:
        parser.print_help()
        return -1
    
    # Set up the track and verbose-ness
    verbose = options.verbose
    track = None
    track = LocalAudioFile(args[0], verbose=verbose)
    if verbose:
        print "Computing swing . . ."

    # This is where the work takes place
    actions = do_work(track, options)
    
    if verbose:
        display_actions(actions)
    
    # This renders the audio out to the new file
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

    # The wrapper for the script.  
if __name__ == "__main__":
    try:
        main()
    except Exception, e:
        print e

