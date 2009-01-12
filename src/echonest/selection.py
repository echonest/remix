# selection.py
# selection filters as utilities for audio.py
# for convenience, intended to be imported as:
#   from selection import *
# if it's not clear, they are all named to be called as analysis.segments.that...

def are_contained_by_range(start, end):
    def fun(x): 
        if x.start >= start and x.start + x.duration <= end: 
            return x
    return fun

def are_contained_by(aq):
    'expects an AudioQuantum, with start and duration'
    def fun(x):
        if x.start >= aq.start and x.start + x.duration <= aq.start + aq.duration: 
            return x
    return fun

def overlap_range(start, end):
    def fun(x): 
        if x.start + x.duration > start and x.start < end:
            return x
    return fun

def overlap(aq):
    def fun(x): 
        if x.start + x.duration > aq.start and x.start < aq.start + aq.duration:
            return x
    return fun


def end_during_range(start, end):
    def fun(x):
        if x.start + x.duration > start and x.start + x.duration < end:
            return x
    return fun

def end_during(aq):
    def fun(x):
        if x.start + x.duration > aq.start and x.start + x.duration < aq.start + aq.duration:
            return x
    return fun

def start_during_range(start, end):
    def fun(x):
        if x.start > start and x.start < end:
            return x
    return fun

def start_during(aq):
    def fun(x):
        if x.start > aq.start and x.start < aq.start + aq.duration:
            return x
    return fun

def contain_point(point):
    def fun(x): 
        if point > x.start and point < x.start + x.duration:
            return x
    return fun

def have_pitch_max(pitchmax):
    def fun(x):
        pitches = x.pitches
        if reduce(all_of, [pitches[pitchmax] >= p for p in pitches]):
            return x
    return fun

def lie_immediately_before(aq):
    def fun(x):
        if x.start + x.duration == aq.start:
            return x
    return fun

def lie_immediately_after(aq):
    def fun(x):
        if x.start == aq.start + aq.duration:
            return x
    return fun

# selection filters that take lists of AudioQuanta, originally from
#  examples/selection/tonic.py

def overlap_ends_of(aqs): 
    def fun(x): 
        for aq in aqs: 
            if x.start <= aq.start + aq.duration and x.start + x.duration >= aq.start + aq.duration: 
                return x 
        return None 
    return fun 

def overlap_starts_of(aqs):
    def fun(x):
        for aq in aqs: 
            if x.start <= aq.start and x.start + x.duration >= aq.start:
                return x
        return None
    return fun

# 
def all_of(x, y):
    return x and y
