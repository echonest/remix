#!/usr/bin/env python
# encoding: utf-8
"""
action.py

Created by Tristan Jehan and Jason Sundram.
"""
import os
from numpy import zeros
from math import atan, pi
import sys

from echonest.audio import assemble, AudioData

try:
    if hasattr(os, 'uname') and os.uname()[0] == 'Darwin':
        # The default dlopenflags setting, RTLD_NOW, causes us to look for stuff that's defined in -framework Carbon
        # and then barf. Let's take it nice and lazy instead.
        f = sys.getdlopenflags()
        sys.setdlopenflags(0)
        import dirac
        sys.setdlopenflags(f)
    else:
        import dirac
except Exception, e:
    sys.exit("Unable to load dirac, which is required for Crossmatch. Please install pydirac: %s" % e)

def rows(m):
    """returns the # of rows in a numpy matrix"""
    return m.shape[0]

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

def limit(data):
    for col in range(data.ndim):
        for i, x in enumerate(data[:, col]):
            data[i, col] = limiter(data[i, col])
    return data

def limiter(val):
    DYN_RANGE  = 32767.0
    LIM_THRESH = 30000.0
    LIM_RANGE  = (DYN_RANGE - LIM_THRESH)
    
    if LIM_THRESH < val:
        res = (val - LIM_THRESH) / LIM_RANGE
        res = ( atan(res) / (pi/2) ) * LIM_RANGE + LIM_THRESH
    elif val < - LIM_THRESH:
        res = - (val + LIM_THRESH) / LIM_RANGE
        res = - ( ( atan(res) / (pi/2) ) * LIM_RANGE + LIM_THRESH )
    else:
        res = val
    return res
    
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
        output = self.track[self]
        
        # Normalize volume if necessary
        sound_check = getattr(self.track, 'sound_check', None)
        if sound_check != None:
            output.data = limit(multiply(output.data, sound_check))
        
        return output
    
    def __repr__(self):
        return "<Playback '%s'>" % self.track.analysis.name
    
    def __str__(self):
        return "Playback\t%.3f\t-> %.3f\t (%.3f)\t%s" % (self.start, self.start+self.duration, self.duration, self.track.analysis.name)


class Fadeout(Playback):

    def render(self):
        sound_check = getattr(self.track, 'sound_check', 1.0)
        output = self.track[self]
        n = rows(output.data)
        for col in range(output.data.ndim):
            for i, x in enumerate(output.data[:, col]):
                frac = float(n-i) / float(n)
                output.data[i, col] = limiter(frac * x * sound_check)
        
        return output
    
    def __repr__(self):
        return "<Fadeout '%s'>" % self.track.analysis.name
    
    def __str__(self):
        return "Fade out\t%.3f\t-> %.3f\t (%.3f)\t%s" % (self.start, self.start+self.duration, self.duration, self.track.analysis.name)


class Fadein(Playback):

    def render(self):
        sound_check = getattr(self.track, 'sound_check', 1.0)
        output = self.track[self]
        n = rows(output.data)
        for col in range(output.data.ndim):
            for i, x in enumerate(output.data[:, col]):
                frac = float(i) / float(n-1)
                output.data[i, col] = limiter(frac * x * sound_check)
        
        return output
    
    def __repr__(self):
        return "<Fadein '%s'>" % self.track.analysis.name
    
    def __str__(self):
        return "Fade in\t%.3f\t-> %.3f\t (%.3f)\t%s" % (self.start, self.start+self.duration, self.duration, self.track.analysis.name)


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
        self.t1, self.t2 = [Edit(t, s, duration) for t,s in zip(tracks, starts)]
        self.duration = self.t1.duration
        self.mode = mode
        self.CROSSFADE_COEFF = 0.6
    
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
        res = limiter(res)
        return res
    
    def logFactor(self, val):
        return pow(val, self.CROSSFADE_COEFF)
    
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
        return "<Crossfade '%s' and '%s'>" % (self.t1.analysis.name, self.t2.analysis.name)
    
    def __str__(self):
        return "Crossfade\t%.3f\t-> %.3f\t (%.3f)\t%s -> %s" % (self.t1.start, self.t2.start+self.duration, self.duration, 
                                                                self.t1.track.analysis.name, self.t2.track.analysis.name)


class Jump(Crossfade):
    def __init__(self, track, source, target, duration):
        self.track = track
        self.t1, self.t2 = (Edit(track, source, duration), Edit(track, target-duration, duration))
        self.duration = float(duration)
        self.mode = 'equal_power'
        self.CROSSFADE_COEFF = 0.6
    
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


class Blend(object):
    """Mix together two lists of beats"""
    def __init__(self, tracks, lists):
        self.t1, self.t2 = tracks
        self.l1, self.l2 = lists
        assert(len(self.l1) == len(self.l2))
        
        self.calculate_durations()
    
    def calculate_durations(self):
        self.durations = [(d1 + d2) / 2.0 for ((s1, d1), (s2, d2)) in zip(self.l1, self.l2)]
        self.duration = sum(self.durations)
    
    def render(self):
        # use self.durations already computed
        # build 2 AudioQuantums
        # call Mix
        pass
    
    def __repr__(self):
        return "<Blend '%s' and '%s'>" % (self.t1.analysis.name, self.t2.analysis.name)
    
    def __str__(self):
        s1, e1 = self.l1[0][0], sum(self.l1[-1]) # start and end for each of these lists.
        s2, e2 = self.l2[0][0], sum(self.l2[-1])
        n1, n2 = self.t1.analysis.name, self.t2.analysis.name # names
        return "Blend [%.3f, %.3f] -> [%.3f, %.3f] (%.3f)\t%s + %s" % (s1, s2, e1, e2, self.duration, n1, n2)


class Crossmatch(Blend):
    
    def calculate_durations(self):
        c, dec = 1.0, 1.0 / float(len(self.l1)+1)
        self.durations = []
        for ((s1, d1), (s2, d2)) in zip(self.l1, self.l2):
            c -= dec
            self.durations.append(c * d1 + (1 - c) * d2)
        self.duration = sum(self.durations)
    
    def stretch(self, t, l):
        """t is a track, l is a list"""
        signal_start = int(l[0][0] * t.sampleRate)
        signal_duration = int((sum(l[-1]) - l[0][0]) * t.sampleRate)
        vecin = t.data[signal_start:signal_start + signal_duration,:]
        
        rates = []
        for i in xrange(len(l)):
            rates.append((int(l[i][0] * t.sampleRate) - signal_start, self.durations[i] / l[i][1]))
        
        vecout = dirac.timeScale(vecin, rates, t.sampleRate, 0)
        if hasattr(t, 'sound_check'):
            vecout = limit(multiply(vecout, t.sound_check))
        
        return AudioData(ndarray=vecout, shape=vecout.shape, sampleRate=t.sampleRate, numChannels=vecout.shape[1])
    
    def render(self):
        # use self.durations already computed
        # 1) stretch the duration of each item in t1 and t2 to the duration prescribed in durations.
        out1 = self.stretch(self.t1, self.l1)
        out2 = self.stretch(self.t2, self.l2)
        
        # 2) cross-fade the results
        # out1.duration, out2.duration, and self.duration should be about the same
        # but it never hurts to be safe.
        duration = min(out1.duration, out2.duration, self.duration)
        c = Crossfade([out1, out2], [0, 0], duration, mode='equal_power')
        return c.render()
    
    def __repr__(self):
        return "<Crossmatch '%s' and '%s'>" % (self.t1.analysis.name, self.t2.analysis.name)
    
    def __str__(self):
        s1, e1 = self.l1[0][0], sum(self.l1[-1]) # start and end for each of these lists.
        s2, e2 = self.l2[0][0], sum(self.l2[-1])
        n1, n2 = self.t1.analysis.name, self.t2.analysis.name # names
        return "Crossmatch\t%.3f\t-> %.3f\t (%.3f)\t%s -> %s" % (s1, e2, self.duration, n1, n2)


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