#!/usr/bin/env python
# encoding: utf=8

"""
capsule_support.py

Created by Tristan Jehan and Jason Sundram.
"""

import numpy as np
from copy import deepcopy
from echonest.action import Crossfade, Playback, Crossmatch, Fadein, Fadeout, humanize_time
from utils import rows, flatten

# constants for now
X_FADE = 3
FADE_IN = 0.25
FADE_OUT = 6
MIN_SEARCH = 4
MIN_MARKERS = 2
MIN_ALIGN_DURATION = 3
LOUDNESS_THRESH = -8
FUSION_INTERVAL = .06   # this is what we use in the analyzer
AVG_PEAK_OFFSET = 0.025 # Estimated time between onset and peak of segment.

# TODO: this should probably be in actions?
def display_actions(actions):
    total = 0
    print
    for a in actions:
        print "%s\t  %s" % (humanize_time(total), unicode(a))
        total += a.duration
    print

def evaluate_distance(mat1, mat2):
    return np.linalg.norm(mat1.flatten() - mat2.flatten())

def upsample_matrix(m):
    """ Upsample matrices by a factor of 2."""
    r, c = m.shape
    out = np.zeros((2*r, c), dtype=np.float32)
    for i in xrange(r):
        out[i*2  , :] = m[i, :]
        out[i*2+1, :] = m[i, :]
    return out

def upsample_list(l, rate=2):
    """ Upsample lists by a factor of 2."""
    if rate != 2: return l[:]
    # Assume we're an AudioQuantumList.
    def split(x):
        a = deepcopy(x)
        a.duration = x.duration / 2
        b = deepcopy(a)
        b.start = x.start + a.duration
        return a, b
    
    return flatten(map(split, l))

def average_duration(l):
    return sum([i.duration for i in l]) / float(len(l))

def align(track1, track2, mat1, mat2):
    """ Constrained search between a settled section and a new section.
        Outputs location in mat2 and the number of rows used in the transition.
    """
    # Get the average marker duration.
    marker1 = average_duration(getattr(track1.analysis, track1.resampled['rate'])[track1.resampled['index']:track1.resampled['index']+rows(mat1)])
    marker2 = average_duration(getattr(track2.analysis, track2.resampled['rate'])[track2.resampled['index']:track2.resampled['index']+rows(mat2)])

    def get_adjustment(tr1, tr2):
        """Update tatum rate if necessary"""
        dist = np.log2(tr1 / tr2)
        if  dist < -0.5: return (1, 2)
        elif dist > 0.5: return (2, 1)
        else:            return (1, 1)
    
    rate1, rate2 = get_adjustment(marker1, marker2)
    if rate1 == 2: mat1 = upsample_matrix(mat1)
    if rate2 == 2: mat2 = upsample_matrix(mat2)
    
    # Update sizes.
    rows2 = rows(mat2)
    rows1 = min( rows(mat1), max(rows2 - MIN_SEARCH, MIN_MARKERS)) # at least the best of MIN_SEARCH choices
    
    # Search for minimum.
    def dist(i):
        return evaluate_distance(mat1[0:rows1,:], mat2[i:i+rows1,:])
    
    min_loc = min(xrange(rows2 - rows1), key=dist)
    min_val = dist(min_loc)
    
    # Let's make sure track2 ends its transition on a regular tatum.
    if rate2 == 2 and (min_loc + rows1) & 1: 
        rows1 -= 1
    
    return min_loc, rows1, rate1, rate2

def equalize_tracks(tracks):
    
    def db_2_volume(loudness):
        return (1.0 - LOUDNESS_THRESH * (LOUDNESS_THRESH - loudness) / 100.0)
    
    for track in tracks:
        loudness = track.analysis.loudness
        track.gain = db_2_volume(loudness)
    
def order_tracks(tracks):
    """ Finds the smoothest ordering between tracks, based on tempo only."""
    tempos = [track.analysis.tempo['value'] for track in tracks]
    median = np.median(tempos)
    def fold(t):
        q = np.log2(t / median)
        if  q < -.5: return t * 2.0
        elif q > .5: return t / 2.0
        else:        return t
        
    new_tempos = map(fold, tempos)
    order = np.argsort(new_tempos)
    return [tracks[i] for i in order]

def is_valid(track, inter, transition):
    markers = getattr(track.analysis, track.resampled['rate'])
    if len(markers) < 1:
        dur = track.duration
    else:
        dur = markers[-1].start + markers[-1].duration - markers[0].start
    return inter + 2 * transition < dur

def get_central(analysis, member='segments'):
    """ Returns a tuple: 
        1) copy of the members (e.g. segments) between end_of_fade_in and start_of_fade_out.
        2) the index of the first retained member.
    """
    def central(s):
        return analysis.end_of_fade_in <= s.start and (s.start + s.duration) < analysis.start_of_fade_out
    
    members = getattr(analysis, member) # this is nicer than data.__dict__[member]
    ret = filter(central, members[:]) 
    index = members.index(ret[0]) if ret else 0
    
    return ret, index

def get_mean_offset(segments, markers):
    if segments == markers:
        return 0
    
    index = 0
    offsets = []
    try:
        for marker in markers:
            while segments[index].start < marker.start + FUSION_INTERVAL:
                offset = abs(marker.start - segments[index].start)
                if offset < FUSION_INTERVAL:
                    offsets.append(offset)
                index += 1
    except IndexError, e:
        pass
    
    return np.average(offsets) if offsets else AVG_PEAK_OFFSET
    
def resample_features(data, rate='tatums', feature='timbre'):
    """
    Resample segment features to a given rate within fade boundaries.
    @param data: analysis object.
    @param rate: one of the following: segments, tatums, beats, bars.
    @param feature: either timbre or pitch.
    @return A dictionary including a numpy matrix of size len(rate) x 12, a rate, and an index
    """
    ret = {'rate': rate, 'index': 0, 'cursor': 0, 'matrix': np.zeros((1, 12), dtype=np.float32)}
    segments, ind = get_central(data.analysis, 'segments')
    markers, ret['index'] = get_central(data.analysis, rate)

    if len(segments) < 2 or len(markers) < 2:
        return ret
        
    # Find the optimal attack offset
    meanOffset = get_mean_offset(segments, markers)
    tmp_markers = deepcopy(markers)
    
    # Apply the offset
    for m in tmp_markers:
        m.start -= meanOffset
        if m.start < 0: m.start = 0
    
    # Allocate output matrix, give it alias mat for convenience.
    mat = ret['matrix'] = np.zeros((len(tmp_markers)-1, 12), dtype=np.float32)
    
    # Find the index of the segment that corresponds to the first marker
    f = lambda x: tmp_markers[0].start < x.start + x.duration
    index = (i for i,x in enumerate(segments) if f(x)).next()
    
    # Do the resampling
    try:
        for (i, m) in enumerate(tmp_markers):
            while segments[index].start + segments[index].duration < m.start + m.duration:
                dur = segments[index].duration
                if segments[index].start < m.start:
                    dur -= m.start - segments[index].start
                
                C = min(dur / m.duration, 1)
                
                mat[i, 0:12] += C * np.array(getattr(segments[index], feature))
                index += 1
                
            C = min( (m.duration + m.start - segments[index].start) / m.duration, 1)
            mat[i, 0:12] += C * np.array(getattr(segments[index], feature))
    except IndexError, e:
        pass # avoid breaking with index > len(segments)
        
    return ret

def column_whiten(mat):
    """ Zero mean, unit variance on a column basis"""
    m = mat - np.mean(mat,0)
    return m / np.std(m,0)

def timbre_whiten(mat):
    if rows(mat) < 2: return mat
    m = np.zeros((rows(mat), 12), dtype=np.float32)
    m[:,0] = mat[:,0] - np.mean(mat[:,0],0)
    m[:,0] = m[:,0] / np.std(m[:,0],0)
    m[:,1:] = mat[:,1:] - np.mean(mat[:,1:].flatten(),0)
    m[:,1:] = m[:,1:] / np.std(m[:,1:].flatten(),0) # use this!
    return m

def move_cursor(track, duration, cursor, buf=MIN_MARKERS):
    dur = 0
    while dur < duration and cursor < rows(track.resampled['matrix']) - buf:
        markers = getattr(track.analysis, track.resampled['rate'])    
        dur += markers[track.resampled['index'] + cursor].duration
        cursor += 1
    return dur, cursor

def get_mat_out(track, transition):
    """ Find and output the matrix to use in the next alignment.
        Assumes that track.resampled exists.
    """
    cursor = track.resampled['cursor']
    mat = track.resampled['matrix']
    # update cursor location to after the transition
    duration, cursor = move_cursor(track, transition, cursor)
    # output matrix with a proper number of rows, from beginning of transition
    return mat[track.resampled['cursor']:cursor,:]

def get_mat_in(track, transition, inter):
    """ Find and output the search matrix to use in the next alignment.
        Assumes that track.resampled exists.
    """
    # search from the start
    cursor = 0
    track.resampled['cursor'] = cursor
    mat = track.resampled['matrix']
    
    # compute search zone by anticipating what's playing after the transition
    marker_end = getattr(track.analysis, track.resampled['rate'])[track.resampled['index'] + rows(mat)].start
    marker_start = getattr(track.analysis, track.resampled['rate'])[track.resampled['index']].start
    search_dur = (marker_end - marker_start) - inter - 2 * transition
    
    if search_dur < 0: 
        return mat[:MIN_MARKERS,:]
    
    # find what the location is in rows
    duration, cursor = move_cursor(track, search_dur, cursor)
    
    return mat[:cursor,:]

def make_crossfade(track1, track2, inter):

    markers1 = getattr(track1.analysis, track1.resampled['rate'])    
    
    if len(markers1) < MIN_SEARCH:
        start1 = track1.resampled['cursor']
    else:
        start1 = markers1[track1.resampled['index'] + track1.resampled['cursor']].start

    start2 = max((track2.analysis.duration - (inter + 2 * X_FADE)) / 2, 0)
    markers2 = getattr(track2.analysis, track2.resampled['rate'])
    
    if len(markers2) < MIN_SEARCH:
        track2.resampled['cursor'] = start2 + X_FADE + inter
        dur = min(track2.analysis.duration - 2 * X_FADE, inter)
    else:
        duration, track2.resampled['cursor'] = move_cursor(track2, start2+X_FADE+inter, 0)
        dur = markers2[track2.resampled['index'] + track2.resampled['cursor']].start - X_FADE - start2

    xf = Crossfade((track1, track2), (start1, start2), X_FADE)
    pb = Playback(track2, start2 + X_FADE, dur)

    return [xf, pb]

def make_crossmatch(track1, track2, rate1, rate2, loc2, rows):
    markers1 = upsample_list(getattr(track1.analysis, track1.resampled['rate']), rate1)
    markers2 = upsample_list(getattr(track2.analysis, track2.resampled['rate']), rate2)
    
    def to_tuples(l, i, n):
        return [(t.start, t.duration) for t in l[i : i + n]]
    
    start1 = rate1 * (track1.resampled['index'] + track1.resampled['cursor'])
    start2 = loc2 + rate2 * track2.resampled['index'] # loc2 has already been multiplied by rate2

    return Crossmatch((track1, track2), (to_tuples(markers1, start1, rows), to_tuples(markers2, start2, rows)))
    
def make_transition(track1, track2, inter, transition):
    # the minimal transition is 2 markers
    # the minimal inter is 0 sec
    markers1 = getattr(track1.analysis, track1.resampled['rate'])
    markers2 = getattr(track2.analysis, track2.resampled['rate'])
    
    if len(markers1) < MIN_SEARCH or len(markers2) < MIN_SEARCH:
        return make_crossfade(track1, track2, inter)
    
    # though the minimal transition is 2 markers, the alignment is on at least 3 seconds
    mat1 = get_mat_out(track1, max(transition, MIN_ALIGN_DURATION))
    mat2 = get_mat_in(track2, max(transition, MIN_ALIGN_DURATION), inter)
    
    try:
        loc, n, rate1, rate2 = align(track1, track2, mat1, mat2)
    except:
        return make_crossfade(track1, track2, inter)
        
    if transition < MIN_ALIGN_DURATION:
        duration, cursor = move_cursor(track2, transition, loc)
        n = max(cursor-loc, MIN_MARKERS)
    
    xm = make_crossmatch(track1, track2, rate1, rate2, loc, n)
    # loc and n are both in terms of potentially upsampled data. 
    # Divide by rate here to get end_crossmatch in terms of the original data.
    end_crossmatch = (loc + n) / rate2
    
    if markers2[-1].start < markers2[end_crossmatch].start + inter + transition:
        inter = max(markers2[-1].start - transition, 0)
        
    # move_cursor sets the cursor properly for subsequent operations, and gives us duration.
    dur, track2.resampled['cursor'] = move_cursor(track2, inter, end_crossmatch)
    pb = Playback(track2, sum(xm.l2[-1]), dur)
    
    return [xm, pb]

def initialize(track, inter, transition):
    """find initial cursor location"""
    mat = track.resampled['matrix']
    markers = getattr(track.analysis, track.resampled['rate'])

    try:
        # compute duration of matrix
        mat_dur = markers[track.resampled['index'] + rows(mat)].start - markers[track.resampled['index']].start
        start = (mat_dur - inter - transition - FADE_IN) / 2
        dur = start + FADE_IN + inter
        # move cursor to transition marker
        duration, track.resampled['cursor'] = move_cursor(track, dur, 0)
        # work backwards to find the exact locations of initial fade in and playback sections
        fi = Fadein(track, markers[track.resampled['index'] + track.resampled['cursor']].start - inter - FADE_IN, FADE_IN)
        pb = Playback(track, markers[track.resampled['index'] + track.resampled['cursor']].start - inter, inter)
    except:
        track.resampled['cursor'] = FADE_IN + inter
        fi = Fadein(track, 0, FADE_IN)
        pb = Playback(track, FADE_IN, inter)

    return [fi, pb]
    
def terminate(track, fade):
    """ Deal with last fade out"""
    cursor = track.resampled['cursor']
    markers = getattr(track.analysis, track.resampled['rate'])
    if MIN_SEARCH <= len(markers):
        cursor = markers[track.resampled['index'] + cursor].start
    return [Fadeout(track, cursor, min(fade, track.duration-cursor))]
