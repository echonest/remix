#!/usr/bin/env python
# encoding: utf=8

"""
capsule.py

accepts songs on the commandline, order them, beatmatch them, and output an audio file

Created by Tristan Jehan and Jason Sundram.
"""

import os
import sys
from optparse import OptionParser

from echonest.action import render, make_stereo
from echonest.audio import LocalAudioFile
from pyechonest import util

from capsule_support import order_tracks, equalize_tracks, resample_features, timbre_whiten, initialize, make_transition, terminate, FADE_OUT, display_actions, is_valid


def tuples(l, n=2):
    """ returns n-tuples from l.
        e.g. tuples(range(4), n=2) -> [(0, 1), (1, 2), (2, 3)]
    """
    return zip(*[l[i:] for i in range(n)])

def do_work(audio_files, options):

    inter = float(options.inter)
    trans = float(options.transition)
    order = bool(options.order)
    equal = bool(options.equalize)
    verbose = bool(options.verbose)
    
    # Get pyechonest/remix objects
    analyze = lambda x : LocalAudioFile(x, verbose=verbose)
    tracks = map(analyze, audio_files)
    
    # decide on an initial order for those tracks
    if order == True:
        if verbose: print "Ordering tracks..."
        tracks = order_tracks(tracks)
    
    if equal == True:
        equalize_tracks(tracks)
        if verbose:
            print
            for track in tracks:
                print "Vol = %.0f%%\t%s" % (track.gain*100.0, track.analysis.pyechonest_track.title)
            print
    
    valid = []
    # compute resampled and normalized matrices
    for track in tracks:
        if verbose: print "Resampling features for", track.analysis.pyechonest_track.title
        track.resampled = resample_features(track, rate='beats')
        track.resampled['matrix'] = timbre_whiten(track.resampled['matrix'])
        # remove tracks that are too small
        if is_valid(track, inter, trans):
            valid.append(track)
        # for compatibility, we make mono tracks stereo
        track = make_stereo(track)
    tracks = valid
    
    if len(tracks) < 1: return []
    # Initial transition. Should contain 2 instructions: fadein, and playback.
    if verbose: print "Computing transitions..."
    start = initialize(tracks[0], inter, trans)
    
    # Middle transitions. Should each contain 2 instructions: crossmatch, playback.
    middle = []
    [middle.extend(make_transition(t1, t2, inter, trans)) for (t1, t2) in tuples(tracks)]
    
    # Last chunk. Should contain 1 instruction: fadeout.
    end = terminate(tracks[-1], FADE_OUT)
    
    return start + middle + end

def get_options(warn=False):
    usage = "usage: %s [options] <list of mp3s>" % sys.argv[0]
    parser = OptionParser(usage=usage)
    parser.add_option("-t", "--transition", default=8, help="transition (in seconds) default=8")
    parser.add_option("-i", "--inter", default=8, help="section that's not transitioning (in seconds) default=8")
    parser.add_option("-o", "--order", action="store_true", help="automatically order tracks")
    parser.add_option("-e", "--equalize", action="store_true", help="automatically adjust volumes")
    parser.add_option("-v", "--verbose", action="store_true", help="show results on screen")        
    parser.add_option("-p", "--pdb", default=True, help="dummy; here for not crashing when using nose")
    
    (options, args) = parser.parse_args()
    if warn and len(args) < 2: 
        parser.print_help()
    return (options, args)
    
def main():
    options, args = get_options(warn=True);
    actions = do_work(args, options)
    verbose = bool(options.verbose)
    
    if verbose:
        display_actions(actions)
        print "Output Duration = %.3f sec" % sum(act.duration for act in actions)
    
        print "Rendering..."
    # Send to renderer
    render(actions, 'capsule.mp3', verbose)
    return 1
    
if __name__ == "__main__":
    main()
    # for profiling, do this:
    #import cProfile
    #cProfile.run('main()', 'capsule_prof')
    # then in ipython:
    #import pstats
    #p = pstats.Stats('capsule_prof')
    #p.sort_stats('cumulative').print_stats(30)
