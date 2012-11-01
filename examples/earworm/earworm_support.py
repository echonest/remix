#!/usr/bin/env python
# encoding: utf-8

"""
earworm_support.py

Created by Tristan Jehan and Jason Sundram.
"""

import numpy as np
from copy import deepcopy
from utils import rows

FUSION_INTERVAL = .06   # This is what we use in the analyzer
AVG_PEAK_OFFSET = 0.025 # Estimated time between onset and peak of segment.


def evaluate_distance(mat1, mat2):
    return np.linalg.norm(mat1.flatten() - mat2.flatten())

def timbre_whiten(mat):
    if rows(mat) < 2: return mat
    m = np.zeros((rows(mat), 12), dtype=np.float32)
    m[:,0] = mat[:,0] - np.mean(mat[:,0],0)
    m[:,0] = m[:,0] / np.std(m[:,0],0)
    m[:,1:] = mat[:,1:] - np.mean(mat[:,1:].flatten(),0)
    m[:,1:] = m[:,1:] / np.std(m[:,1:].flatten(),0) # use this!
    return m


def get_central(analysis, member='segments'):
    """ Returns a tuple: 
        1) copy of the members (e.g. segments) between end_of_fade_in and start_of_fade_out.
        2) the index of the first retained member.
    """
    def central(s):
        return analysis.end_of_fade_in <= s.start and (s.start + s.duration) < analysis.start_of_fade_out
    
    members = getattr(analysis, member)
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
    # Make a copy for local use
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