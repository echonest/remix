#!/usr/bin/env python
# encoding: utf-8
"""
utils.py

Created by Jason Sundram, on 2010-04-05.
Copyright (c) 2010 The Echo Nest. All rights reserved.
"""

def flatten(l):
    """ Converts a list of tuples to a flat list.
        e.g. flatten([(1,2), (3,4)]) => [1,2,3,4]
    """
    return [item for pair in l for item in pair]

def tuples(l, n=2):
    """ returns n-tuples from l.
        e.g. tuples(range(4), n=2) -> [(0, 1), (1, 2), (2, 3)]
    """
    return zip(*[l[i:] for i in range(n)])

def rows(m):
    """returns the # of rows in a numpy matrix"""
    return m.shape[0]