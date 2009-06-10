"""
Sorting key functions as utilities for `echonest.audio`.

For convenience, intended to be imported as::

   from audio.sorting import *

All of the functions in this module can be used as a sorting key for
`AudioQuantumList.ordered_by`, as in::

    analysis.segments.ordered_by(duration)

Some of the functions in this module return *another* function that takes 
one argument, an `AudioQuantum`, and returns a value (typically a `float`)
that can then be used as a sorting value.

By convention, all of these functions are named to be noun phrases that 
follow `sorted_by`, as seen above.
"""

def confidence(x):      
    """
    Returns the `AudioQuantum`\'s `confidence` as a sorting value.
    """
    return x.confidence

def duration(x):      
    """
    Returns the `AudioQuantum`\'s `duration` as a sorting value.
    """
    return x.duration

def timbre_value(index):
    """
    Returns a function that returns the value of `timbre`\[*index*]
    of its input `AudioQuantum`. Sorts by the values of the *index*-th 
    value in the timbre vector.
    """
    return lambda x: x.timbre[index]

def pitch_value(index):
    """
    Returns a function that returns the value of `pitch`\[*index*]
    of its input `AudioQuantum`. Sorts by the values of the *index*-th 
    value in the pitch vector.
    """
    return lambda x: x.pitches[index]

def pitch_distance_from(seg):
    """
    Returns a function that returns the sum of the squared differences
    between the `pitch` vector of its input `AudioQuantum` and the `pitch` 
    vector of the reference parameter *seg*. Sorts by the pitch distance 
    from the reference `AudioSegment`.
    """
    return lambda x: sum(map(_diff_squared, seg.pitches, x.pitches))

def timbre_distance_from(seg):
    """
    Returns a function that returns the sum of the squared differences 
    between the `pitch` vector of its input `AudioQuantum` and the `pitch` 
    vector of the reference parameter *seg*. Sorts by the pitch distance 
    from the reference `AudioSegment`.
    """
    return lambda x: sum(map(_diff_squared, seg.timbre, x.timbre))

def noisiness(x):
    """
    Returns the sum of the twelve pitch vectors' elements. This is a very
    fast way of judging the relative noisiness of a segment.
    """
    return sum(x.pitches)

# local helper functions:
def _diff_squared(a, b):
    """
    Local helper function. The square of the difference between a and b.
    """
    return pow(a-b, 2)
