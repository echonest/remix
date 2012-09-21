#!/usr/bin/env python
# encoding: utf=8

"""
waltzify.py

Turn 4/4 music into 3/4
Modified approach suggested by Mary Farbood.
Created by Tristan Jehan.
"""

# These lines import other things.  
import os, sys
import dirac, math
from optparse import OptionParser

# These line import specific things from Remix! 
from echonest.audio import LocalAudioFile, AudioData
from echonest.action import render, Playback, display_actions

# Waltzify is much more complex than the prior examples!  
# Hold on, and we'll try to make everything make sense

# This picks a tempo to set each beat to.
def select_tempo(index, num_beats, min_tempo, max_tempo, rate):
    v = math.atan(float(rate)*float(index)/float(num_beats))/1.57
    return min_tempo + v * float(max_tempo-min_tempo)

    # This is the function that does the waltzifying
def do_work(track, options):
    
    # This manages the various input options
    verbose = bool(options.verbose)    
    low_tempo = float(options.low)    
    high_tempo = float(options.high)    
    rate_tempo = float(options.rate)    
    rubato = float(options.rubato)    
    tempo = float(options.tempo)    

    # This set the tempo and applies acceleration or not
    if rate_tempo == 0:
        if tempo == 0:
            low_tempo = track.analysis.tempo['value']
            high_tempo = low_tempo
        else:
            low_tempo = tempo
            high_tempo = tempo
    
    rates = []
    count = min(max(0,int(options.offset)),1)
    beats = track.analysis.beats
    offset = int(beats[0].start * track.sampleRate)

    # For every beat, we get a tempo, and apply a time stretch
    for beat in beats[:-1]:

        # Get a tempo for the beat
        target_tempo = select_tempo(beats.index(beat), len(beats), low_tempo, high_tempo, rate_tempo)

        # Calculate rates for time stretching each beat.
        # 
        if count == 0:
            dur = beat.duration/2.0
            rate1 = 60.0 / (target_tempo * dur)
            stretch = dur * rate1
            rate2 = rate1 + rubato
        elif count == 1:
            rate1 = 60.0 / (target_tempo * beat.duration)

        # Add a change of rate at a given time
        start1 = int(beat.start * track.sampleRate)
        rates.append((start1-offset, rate1))
        if count == 0:
            start2 = int((beat.start+dur) * track.sampleRate)
            rates.append((start2-offset, rate2))

        # This prints what's happening, if verbose mode is on.
        if verbose:
            if count == 0:
                args = (beats.index(beat), count, beat.duration, dur*rate1, dur*rate2, 60.0/(dur*rate1), 60.0/(dur*rate2))
                print "Beat %d (%d) | stretch %.3f sec into [%.3f|%.3f] sec | tempo = [%d|%d] bpm" % args
            elif count == 1:
                args = (beats.index(beat), count, beat.duration, beat.duration*rate1, 60.0/(beat.duration*rate1))
                print "Beat %d (%d) | stretch %.3f sec into %.3f sec | tempo = %d bpm" % args
        
        count = (count + 1) % 2
   
    # This gets the audio
    vecin = track.data[offset:int(beats[-1].start * track.sampleRate),:]

    # This does the time stretch
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
    # This setups up a parser for the various input options
    usage = "usage: %s [options] <one_single_mp3>" % sys.argv[0]
    parser = OptionParser(usage=usage)
    parser.add_option("-o", "--offset", default=0, help="offset where to start counting")
    parser.add_option("-l", "--low", default=100, help="low tempo")
    parser.add_option("-H", "--high", default=192, help="high tempo")
    parser.add_option("-r", "--rate", default=0, help="acceleration rate (try 30)")
    parser.add_option("-R", "--rubato", default=0, help="rubato on second beat (try 0.2)")
    parser.add_option("-t", "--tempo", default=0, help="target tempo (try 160)")
    parser.add_option("-v", "--verbose", action="store_true", help="show results on screen")
    
    # If we don't have enough options, exit!
    (options, args) = parser.parse_args()
    if len(args) < 1:
        parser.print_help()
        return -1
    
    verbose = options.verbose

    # This gets the analysis for this file
    track = LocalAudioFile(args[0], verbose=verbose)
    
    if verbose:
        print "Waltzifying..."

    # This is where the work takes place
    actions = do_work(track, options)

    if verbose:
        display_actions(actions)
    
    # This makes the new name for the output file
    name = os.path.splitext(os.path.basename(args[0]))
    name = str(name[0] + '_waltz_%d' % int(options.offset) +'.mp3')
    
    if verbose:
        print "Rendering... %s" % name

    # This renders the audio out to the output file
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

