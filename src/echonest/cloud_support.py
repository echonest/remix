"""
Make pyechonest and remix objects from local audio and json files
Created 2010-04-12 by Jason Sundram
"""
import hashlib
try:
    import json
except ImportError:
    import simplejson as json
import sys
from echonest.audio import _dataParser as data_parser
from echonest.audio import _attributeParser as attribute_parser
from echonest.audio import _segmentsParser as segment_parser
from echonest.audio import AudioData

class attrdict(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.__dict__ = self

class AnalysisProxy(object):
    def __init__(self, jsonpath):
        s = open(jsonpath).read()
        a = json.loads(s)
        self.__dict__.update(a)

class JsonTrack(object):
    """
        A way to make a .json file spit out from an3 look like a pyechonest track.
        This quacks like track.Track, but doesn't derive from it, since track has a 
        bunch of methods that aren't appropriate here.
    """
    def __init__(self, identifier):
        a = AnalysisProxy(identifier)
        self._analysis = a
        self.md5 = a.track['sample_md5']
        # Json files don't have trackids in them, so not sure what to do about ids.
        self.identifier = "music://id.echonest.com/~/TR/TR_UNKNOWN" 
        self.params = {'md5': self.md5, 'analysis_version': a.meta['analyzer_version'] }
        self.bars = map(attrdict, a.bars)
        self.beats = map(attrdict, a.beats)
        self.tatums = map(attrdict, a.tatums)
        self.duration = a.track['duration']
        self.end_of_fade_in = a.track['end_of_fade_in']
        self.key = {'value' : a.track['key'], 'confidence' : a.track['key_confidence']}
        self.loudness = a.track['loudness']
        self.mode = {'value' : a.track['mode'], 'confidence' : a.track['mode_confidence']} 
        self.start_of_fade_out = a.track['start_of_fade_out']
        self.tempo = {'value' : a.track['tempo'], 'confidence' : a.track['tempo_confidence']} 
        self.time_signature = {'value' : a.track['time_signature'], 'confidence' : a.track['time_signature_confidence']} 
        self.sections = a.sections
        self.metadata = {
                            'artist': a.meta.get('artist'),
                            'bitrate': a.meta.get('bitrate'),
                            'duration': int(self.duration),
                            'genre': a.meta.get('genre'),
                            'id': self.identifier,
                            'md5': self.md5,
                            'release': a.meta.get('album'),
                            'samplerate': a.meta.get('sample_rate'),
                            'status': a.meta['detailed_status'], 
                            'title': a.meta.get('title')
                        }
        def fixup_segment(seg):
            s = dict()
            s.update(seg)
            s['time_loudness_max'] = s['loudness_max_time']
            del s['loudness_max_time']
            s['loudness_begin'] = s['loudness_start']
            del s['loudness_start']
            s['loudness_end'] = None # TODO: how is this populated?
            return attrdict(s) # return s
        self.segments = map(fixup_segment, a.segments)
        self.name = self.metadata['title']
    
    def __repr__(self):
        return "<Track '%s'>" % self.name
    
    def __str__(self):
        return self.name

class LocalAudioAnalysis(JsonTrack):
    """An equivalent to remix's AudioAnalysis, using whole audio and json objects"""
    def __init__(self, json_file):
        h = JsonTrack(json_file)
        
        # Previously had:
        # super(LocalAudioAnalysis, self).__init__(json_file)
        # super(LocalAudioAnalysis, self).bars
        # but kept getting errors becuase there were no bars. WTF?
        # The following line of insanity actually works.
        self.__dict__.update(h.__dict__) 
        
        # Walk like an AudioAnalysis
        self.sections = attribute_parser('section', self.sections)
        self.bars = data_parser('bar', self.bars)
        self.beats = data_parser('beat', self.beats)
        self.tatums = data_parser('tatum', self.tatums)
        self.segments = segment_parser(self.segments)
        
        self.sections.attach(self)
        self.bars.attach(self)
        self.beats.attach(self)
        self.tatums.attach(self)
        self.segments.attach(self)

class AnalyzedAudioFile(AudioData):
    """
    Equivalent to LocalAudioFile, this class assumes you have a local .json
    version of the analysis (produced by an3).
    """
    def __init__(self, filename, defer=False):
        """
        :param filename: path to a local audio file, with a .json sidecar file.
        """
        self.analysis = LocalAudioAnalysis(filename + '.json')
        self.analysis.identifier = filename # better than nothing
        # analyzer has the md5 of the decoded audio bits, which is less useful
        self.analysis.md5 = hashlib.md5(file(filename, 'rb').read()).hexdigest()
        AudioData.__init__(self, filename=filename, defer=defer)
        self.analysis.source = self # circles!
