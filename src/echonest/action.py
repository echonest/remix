#!/usr/bin/env python
# encoding: utf-8
"""
action.py

Created by Tristan Jehan and Jason Sundram.
"""
from echonest.audio import assemble
from numpy import zeros
from utils import rows
from math import atan, pi

CROSSFADE_COEFF = 0.6

def make_mono(track):
    "Converts stereo tracks to mono; leaves mono tracks alone."
    if track.data.ndim == 2:
        mono = zeros((len(track.data), ))
        for i, d in enumerate(track.data):
            mono[i] = d[0]
        track.data = mono
    return track

def make_stereo(track):
    """If the track is mono, doubles it. otherwise, does nothing."""
    if track.data.ndim == 1:
        stereo = zeros((len(track.data), 2))
        for i, d in enumerate(track.data):
            stereo[i] = (d, d)
        track.data = stereo
    return track

def render(actions, filename):
    """Calls render on each action in actions, concatenates the results, renders an audio file, and returns a path to the file"""
    pieces = [a.render() for a in actions]
    out = assemble(pieces, numChannels=2, sampleRate=44100) # TODO: make these vary.
    return out, out.encode(filename)


class Playback(object):
    def __init__(self, track, start, duration):
        self.track = track
        self.start = float(start)
        self.duration = float(duration)
    
    def render(self):
        # self has start and duration, so it is a valid index into track.
        return self.track[self] 
    
    def __repr__(self):
        return "<Playback '%s'>" % self.track.analysis.name
    
    def __str__(self):
        return "Playback\t%.3f\t-> %.3f\t (%.3f)\t%s" % (self.start, self.start+self.duration, self.duration, self.track.analysis.name)


class Fadeout(Playback):

    def render(self):
        output = self.track[self]
        n = rows(output.data)
        for col in range(output.data.ndim):
            for i, x in enumerate(output.data[:, col]):
                frac = float(n-i) / float(n)
                output.data[i, col] = frac * x
        
        return output
    
    def __repr__(self):
        return "<Fadeout '%s'>" % self.track.analysis.name
    
    def __str__(self):
        return "Fade out\t%.3f\t-> %.3f\t (%.3f)\t%s" % (self.start, self.start+self.duration, self.duration, self.track.analysis.name)


class Fadein(Playback):

    def render(self):
        output = self.track[self]
        n = rows(output.data)
        for col in range(output.data.ndim):
            for i, x in enumerate(output.data[:, col]):
                frac = float(i) / float(n-1)
                output.data[i, col] = frac * x
        
        return output
    
    def __repr__(self):
        return "<Fadein '%s'>" % self.track.analysis.name
    
    def __str__(self):
        return "Fade in\t\t%.3f\t-> %.3f\t (%.3f)\t%s" % (self.start, self.start+self.duration, self.duration, self.track.analysis.name)


class Edit(object):
    def __init__(self, track, start, duration):
        self.track = track
        self.start = float(start)
        self.duration = float(duration)
    
    def __str__(self):
        return "Edit\t%.3f\t-> %.3f\t (%.3f)\t%s" % (self.start, self.start+self.duration, self.duration, self.track.analysis.name)
    
    def get(self):
        return self.track[self]
    
    @property
    def end(self):
        return self.start + self.duration


class Crossfade(object):
    def __init__(self, tracks, starts, duration, mode='linear'):
        self.track = track;
        self.t1, self.t2 = [Edit(t, s, duration) for t,s in zip(tracks, starts)]
        self.mode = mode
        
    def render(self):
        t1, t2 = map(make_stereo, (self.t1.get(), self.t2.get()))
        output = self.allocate_output(t1, t2)
        n = rows(output.data)
        for col in range(output.data.ndim):
            for (i, (x1, x2)) in enumerate(zip(t1.data[:, col], t2.data[:, col])):
                if self.mode == 'equal_power':
                    output.data[i, col] = self.equal_power(x1, x2, i, n)
                else:
                    output.data[i, col] = self.linear(x1, x2, i, n)
        return output
        
    def linear(self, x1, x2, i, n):
        f_in  = float(i) / float(n-1)
        f_out = float(n-i) / float(n)
        return int(round(f_out * x1 + f_in * x2))
        
    def equal_power(self, x1, x2, i, n):
        f_in  = float(i) / float(n-1)
        f_out = float(n-i) / float(n)
        res = int(round(self.logFactor(f_out) * x1 + self.logFactor(f_in) * x2))
        res = self.limiter(res)
        return res
        
    def logFactor(self, val):
        return pow(val, CROSSFADE_COEFF)
        
    def limiter(self, val):
        DYN_RANGE = 32767.0
        LIM_THRESH = 30000.0
        LIM_RANGE = (DYN_RANGE - LIM_THRESH)
        
        if LIM_THRESH < val:
            res = (val - LIM_THRESH) / LIM_RANGE
            res = ( atan(res) / (pi/2) ) * LIM_RANGE + LIM_THRESH
        elif val < - LIM_THRESH:
            res = - (val + LIM_THRESH) / LIM_RANGE
            res = - ( ( atan(res) / (pi/2) ) * LIM_RANGE + LIM_THRESH )
        else:
            res = val
        return res
    
    def allocate_output(self, t1, t2):
        n1, n2 = rows(t1.data), rows(t2.data)
        n = min(n1, n2)
        if n1 != n2:
            print "t1 (%s) has %d rows, t2 (%s) has %d rows" % (str(t1), n1, str(t2), n2)
        if n1 < n2: 
            output = t1[:]
        else: 
            output = t2[:]
        return output
    
    def __repr__(self):
        return "<Crossfade '%s' and '%s'>" % (self.tracks[0].analysis.name, self.tracks[1].analysis.name)
    
    def __str__(self):
        return "Crossfade\t%.3f\t-> %.3f\t (%.3f)\t%s -> %s" % (self.starts[0], self.starts[1]+self.duration, self.duration, 
                                                                self.tracks[0].analysis.name, self.tracks[0].analysis.name)


class Jump(Crossfade):
    def __init__(self, track, source, target, duration):
        self.track = track;
        self.t1, self.t2 = (Edit(track, source, duration), Edit(track, target-duration, duration))
        self.duration = float(duration)
        self.mode = 'equal_power'
    
    @property
    def source(self):
        return self.t1.start
    
    @property
    def target(self):
        return self.t2.end 
    
    def __repr__(self):
        return "<Jump '%s'>" % (self.t1.track.analysis.name)
    
    def __str__(self):
        return "Jump\t\t%.3f\t-> %.3f\t (%.3f)\t%s" % (self.t1.start, self.t2.end, self.duration, self.t1.track.analysis.name)


def humanize_time(secs):
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    if 0 < hours: 
        return '%02d:%02d:%02d' % (hours, mins, secs)
    
    return '%02d:%02d' % (mins, secs)


def display_actions(actions):
    total = 0
    print
    for a in actions:
        print "%s\t  %s" % (humanize_time(total), unicode(a))
        total += a.duration
    print