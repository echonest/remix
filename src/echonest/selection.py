"""
Selection filters as utilities for `echonest.audio`.

For convenience, intended to be imported as::

   from audio.selection import *

The functions in this module each return *another* function that takes 
one argument, an `AudioQuantum`, and returns an `AudioQuantum` or `None`.

By convention, all of these functions are named to be verb phrases that 
agree with a plural noun in a restrictive clause introduced by `that`, 
as in::

    analysis.segments.that(fall_on_the(1))
"""

def are_contained_by_range(start, end):
    """
    Returns a function that tests if its input `AudioQuantum` lies 
    between the *start* and *end* parameters.
    """
    def fun(x): 
        if x.start >= start and x.end <= end: 
            return True
    return fun

def are_contained_by(aq):
    """
    Returns a function that tests if its input `AudioQuantum` lies 
    within the interval of the parameter *aq* `AudioQuantum`,
    """
    def fun(x):
        if x.start >= aq.start and x.end <= aq.end: 
            return True
    return fun

def overlap_range(start, end):
    """
    Returns a function that tests if its input `AudioQuantum` overlaps
    in any way the interval between the parameters *start* and *end*.
    """
    def fun(x): 
        if x.end > start and x.start < end:
            return True
    return fun

def overlap(aq):
    """
    Returns a function that tests if its input `AudioQuantum` overlaps
    in any way the parameter *aq* `AudioQuantum`.
    """
    def fun(x): 
        if x.end > aq.start and x.start < aq.end:
            return True
    return fun


def end_during_range(start, end):
    """
    Returns a function that tests if its input `AudioQuantum`\'s `end`
    lies in the interval between the parameters *start* and *end*.
    """
    def fun(x):
        if x.end > start and x.end <= end:
            return True
    return fun

def end_during(aq):
    """
    Returns a function that tests if its input `AudioQuantum`\'s `end`
    lies anywhere during the parameter *aq* `AudioQuantum`.
    """
    def fun(x):
        if x.end > aq.start and x.end <= aq.end:
            return True
    return fun

def start_during_range(start, end):
    """
    Returns a function that tests if its input `AudioQuantum`\'s `start`
    lies in the interval between the parameters *start* and *end*.
    """
    def fun(x):
        if x.start >= start and x.start < end:
            return True
    return fun

def start_during(aq):
    """
    Returns a function that tests if its input `AudioQuantum`\'s `start`
    lies anywhere during the parameter *aq* `AudioQuantum`.
    """
    def fun(x):
        if x.start >= aq.start and x.start < aq.end:
            return True
    return fun

def contain_point(point):
    """
    Returns a function that tests if its input `AudioQuantum` contains
    the input parameter *point*, a time offset, in seconds.
    """
    def fun(x): 
        if point > x.start and point < x.end:
            return True
    return fun

def have_pitch_max(pitchmax):
    """
    Returns a function that tests if its input `AudioQuantum` has
    a `pitch`\[*pitchmax*] such that it is greater or equal to all 
    other values in its `pitch` vector.
    """
    def fun(x):
        pitches = x.pitches
        if reduce(all_of, [pitches[pitchmax] >= p for p in pitches]):
            return True
    return fun

def have_pitches_max(pitchesmax):
    """
    Returns a function that tests if its input `AudioQuantum` has
    a maximum `pitch`\[*p*] such that it is greater or equal to all 
    other values in its `pitch` vector, and *p* is in `List` parameter 
    *pitchesmax*.
    """
    def fun(x):
        pitches = x.pitches
        for pitchmax in pitchesmax:
            if reduce(all_of,[pitches[pitchmax] >=p for p in pitches]):
                return True
    return fun

def lie_immediately_before(aq):
    """
    Returns a function that tests if its input `AudioQuantum` lies 
    immediately before the parameter *aq* `AudioQuantum`. That is, 
    if the tested `AudioQuantum`\'s `end` == *aq*.start .
    """
    def fun(x):
        if x.end == aq.start:
            return True
    return fun

def lie_immediately_after(aq):
    """
    Returns a function that tests if its input `AudioQuantum` lies 
    immediately after the parameter *aq* `AudioQuantum`. That is, 
    if the tested `AudioQuantum`\'s `start` == *aq*.end .
    """
    def fun(x):
        if x.start == aq.end:
            return True
    return fun

def fall_on_the(beat_number):
    """
    Returns a function that tests if its input `AudioQuantum` has 
    a (one-indexed) ordinality within its `group`\() that is equal 
    to parameter *beat_number*.
    """
    def fun(x):        
        if x.local_context()[0] == (beat_number - 1):
            return True
    return fun

# The following take AudioQuantumLists as input arguments:
def overlap_ends_of(aqs): 
    """
    Returns a function that tests if its input `AudioQuantum` contains 
    the `end` of any of the parameter *aqs*, a `List` of 
    `AudioQuantum`\s.
    """
    def fun(x): 
        for aq in aqs: 
            if x.start <= aq.end and x.end >= aq.end: 
                return True
        return None 
    return fun 

def overlap_starts_of(aqs):
    """
    Returns a function that tests if its input `AudioQuantum` contains 
    the `start` of any of the parameter *aqs*, a `List` of 
    `AudioQuantum`\s.
    """
    def fun(x):
        for aq in aqs: 
            if x.start <= aq.start and x.end >= aq.start:
                return True
        return None
    return fun

def start_during_any(aqs):
    """
    Returns a function that tests if its input `AudioQuantum` has 
    its `start` lie in any of the parameter *aqs*, a `List` of 
    `AudioQuantum`\s.
    """
    def fun(x):
        for aq in aqs:
            if aq.start <= x.start and aq.end >= aq.start:
                return True
        return None
    return fun

# 
def all_of(x, y):
    """
    Local helper function. Returns `True` if everything is true in a 
    `reduce`\(). It's only here because we can't rely on Python 2.5
    being present for `all`\().
    """
    return x and y
