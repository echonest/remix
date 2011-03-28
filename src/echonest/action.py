#!/usr/bin/env python
# encoding: utf-8
"""
action.py

Created by Tristan Jehan and Jason Sundram.
"""
import os
from numpy import zeros, multiply, float32, mean, copy
from math import atan, pi
import sys

from echonest.audio import assemble, AudioData
from cAction import limit, crossfade, fadein, fadeout

import dirac

def rows(m):
    """returns the # of rows in a numpy matrix"""
    return m.shape[0]

def make_mono(track):
    """Converts stereo tracks to mono; leaves mono tracks alone."""
    if track.data.ndim == 2:
        mono = mean(track.data,1)
        track.data = mono
        track.numChannels = 1
    return track

def make_stereo(track):
    """If the track is mono, doubles it. otherwise, does nothing."""
    if track.data.ndim == 1:
        stereo = zeros((len(track.data), 2))
        stereo[:,0] = copy(track.data)
        stereo[:,1] = copy(track.data)
        track.data = stereo
        track.numChannels = 2
    return track
    
def render(actions, filename, verbose=True):
    """Calls render on each action in actions, concatenates the results, 
    renders an audio file, and returns a path to the file"""
    pieces = [a.render() for a in actions]
    # TODO: allow numChannels and sampleRate to vary.
    out = assemble(pieces, numChannels=2, sampleRate=44100, verbose=verbose)
    return out, out.encode(filename)


class Playback(object):
    """A snippet of the given track with start and duration. Volume leveling 
    may be applied."""
    def __init__(self, track, start, duration):
        self.track = track
        self.start = float(start)
        self.duration = float(duration)
    
    def render(self):
        # self has start and duration, so it is a valid index into track.
        output = self.track[self]
        # Normalize volume if necessary
        gain = getattr(self.track, 'gain', None)
        if gain != None:
            # limit expects a float32 vector
            output.data = limit(multiply(output.data, float32(gain)))
            
        return output
    
    def __repr__(self):
        return "<Playback '%s'>" % self.track.analysis.pyechonest_track.title
    
    def __str__(self):
        args = (self.start, self.start + self.duration, 
                self.duration, self.track.analysis.pyechonest_track.title)
        return "Playback\t%.3f\t-> %.3f\t (%.3f)\t%s" % args


class Fadeout(Playback):
    """Fadeout"""
    def render(self):
        gain = getattr(self.track, 'gain', 1.0)
        output = self.track[self]
        # second parameter is optional -- in place function for now
        output.data = fadeout(output.data, gain)
        return output
    
    def __repr__(self):
        return "<Fadeout '%s'>" % self.track.analysis.pyechonest_track.title
    
    def __str__(self):
        args = (self.start, self.start + self.duration, 
                self.duration, self.track.analysis.pyechonest_track.title)
        return "Fade out\t%.3f\t-> %.3f\t (%.3f)\t%s" % args


class Fadein(Playback):
    """Fadein"""
    def render(self):
        gain = getattr(self.track, 'gain', 1.0)
        output = self.track[self]
        # second parameter is optional -- in place function for now
        output.data = fadein(output.data, gain)
        return output
    
    def __repr__(self):
        return "<Fadein '%s'>" % self.track.analysis.pyechonest_track.title
    
    def __str__(self):
        args = (self.start, self.start + self.duration, 
                self.duration, self.track.analysis.pyechonest_track.title)
        return "Fade in\t%.3f\t-> %.3f\t (%.3f)\t%s" % args


class Edit(object):
    """Refer to a snippet of audio"""
    def __init__(self, track, start, duration):
        self.track = track
        self.start = float(start)
        self.duration = float(duration)
    
    def __str__(self):
        args = (self.start, self.start + self.duration, 
                self.duration, self.track.analysis.pyechonest_track.title)
        return "Edit\t%.3f\t-> %.3f\t (%.3f)\t%s" % args
    
    def get(self):
        return self.track[self]
    
    @property
    def end(self):
        return self.start + self.duration


class Crossfade(object):
    """Crossfades between two tracks, at the start points specified, 
    for the given duration"""
    def __init__(self, tracks, starts, duration, mode='linear'):
        self.t1, self.t2 = [Edit(t, s, duration) for t,s in zip(tracks, starts)]
        self.duration = self.t1.duration
        self.mode = mode
    
    def render(self):
        t1, t2 = map(make_stereo, (self.t1.get(), self.t2.get()))
        vecout = crossfade(t1.data, t2.data, self.mode)
        audio_out = AudioData(ndarray=vecout, shape=vecout.shape, 
                                sampleRate=t1.sampleRate, 
                                numChannels=vecout.shape[1])
        return audio_out
    
    def __repr__(self):
        args = (analysis.pyechonest_track.title, self.t2.track.analysis.pyechonest_track.title)
        return "<Crossfade '%s' and '%s'>" % args
    
    def __str__(self):
        args = (self.t1.start, self.t2.start + self.duration, self.duration, 
                self.t1.track.analysis.pyechonest_track.title, self.t2.track.analysis.pyechonest_track.title)
        return "Crossfade\t%.3f\t-> %.3f\t (%.3f)\t%s -> %s" % args


class Jump(Crossfade):
    """Move from one point """
    def __init__(self, track, source, target, duration):
        self.track = track
        self.t1, self.t2 = (Edit(track, source, duration), 
                            Edit(track, target - duration, duration))
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
        return "<Jump '%s'>" % (self.t1.track.analysis.pyechonest_track.title)
    
    def __str__(self):
        args = (self.t1.start, self.t2.end, self.duration, 
                self.t1.track.analysis.pyechonest_track.title)
        return "Jump\t\t%.3f\t-> %.3f\t (%.3f)\t%s" % args


class Blend(object):
    """Mix together two lists of beats"""
    def __init__(self, tracks, lists):
        self.t1, self.t2 = tracks
        self.l1, self.l2 = lists
        assert(len(self.l1) == len(self.l2))
        
        self.calculate_durations()
    
    def calculate_durations(self):
        zipped = zip(self.l1, self.l2)
        self.durations = [(d1 + d2) / 2.0 for ((s1, d1), (s2, d2)) in zipped]
        self.duration = sum(self.durations)
    
    def render(self):
        # use self.durations already computed
        # build 2 AudioQuantums
        # call Mix
        pass
    
    def __repr__(self):
        args = (self.t1.analysis.pyechonest_track.title, self.t2.analysis.pyechonest_track.title)
        return "<Blend '%s' and '%s'>" % args
    
    def __str__(self):
        # start and end for each of these lists.
        s1, e1 = self.l1[0][0], sum(self.l1[-1])
        s2, e2 = self.l2[0][0], sum(self.l2[-1])
        n1, n2 = self.t1.analysis.pyechonest_track.title, self.t2.analysis.pyechonest_track.title # names
        args = (s1, s2, e1, e2, self.duration, n1, n2)
        return "Blend [%.3f, %.3f] -> [%.3f, %.3f] (%.3f)\t%s + %s" % args


class Crossmatch(Blend):
    """Makes a beat-matched crossfade between the two input tracks."""
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
            rate = (int(l[i][0] * t.sampleRate) - signal_start, 
                    self.durations[i] / l[i][1])
            rates.append(rate)
        
        vecout = dirac.timeScale(vecin, rates, t.sampleRate, 0)
        if hasattr(t, 'gain'):
            vecout = limit(multiply(vecout, float32(t.gain)))
        
        audio_out = AudioData(ndarray=vecout, shape=vecout.shape, 
                                sampleRate=t.sampleRate, 
                                numChannels=vecout.shape[1])
        return audio_out
    
    def render(self):
        # use self.durations already computed
        # 1) stretch the duration of each item in t1 and t2
        # to the duration prescribed in durations.
        out1 = self.stretch(self.t1, self.l1)
        out2 = self.stretch(self.t2, self.l2)
        
        # 2) cross-fade the results
        # out1.duration, out2.duration, and self.duration should be about 
        # the same, but it never hurts to be safe.
        duration = min(out1.duration, out2.duration, self.duration)
        c = Crossfade([out1, out2], [0, 0], duration, mode='equal_power')
        return c.render()
    
    def __repr__(self):
        args = (self.t1.analysis.pyechonest_track.title, self.t2.analysis.pyechonest_track.title)
        return "<Crossmatch '%s' and '%s'>" % args
    
    def __str__(self):
        # start and end for each of these lists.
        s1, e1 = self.l1[0][0], sum(self.l1[-1])
        s2, e2 = self.l2[0][0], sum(self.l2[-1])
        n1, n2 = self.t1.analysis.pyechonest_track.title, self.t2.analysis.pyechonest_track.title # names
        args = (s1, e2, self.duration, n1, n2)
        return "Crossmatch\t%.3f\t-> %.3f\t (%.3f)\t%s -> %s" % args


def humanize_time(secs):
    """Turns seconds into a string of the form HH:MM:SS, 
    or MM:SS if less than one hour."""
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