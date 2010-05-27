"""
Convenience methods for creating Remix audio objects by searching.
Created 2010-04-12 by Jason Sundram

See the docs here for how to use the api directly:
http://beta.developer.echonest.com/song.html#search
"""
import os
import sys
import urllib
from urllib2 import quote, urlparse

try:
    from beta_pyechonest import song
except:
    sys.exit("""
            You need to have v4 pyechonest (BETA) installed for cloud.py to work!
            Just check it out and install it:
                svn checkout http://pyechonest.googlecode.com/svn/branches/beta_pyechonest beta_pyechonest
                cd beta_pyechonest
                python setup.py install
            """)

from cloud_support import AnalyzedAudioFile


def find_track(artist, title, catalog):
    """
        Given an artist and title, uses v4 pyechonest to get a song object,
        download the track and audio analysis for that song from the given 
        catalog, and return an AudioData-type thing.
    """
    songs = song.search(artist=artist, title=title, results=1, buckets=['id:' + catalog], limit=True)
    if songs:
        return make_track(songs[0], catalog)
    return None

def make_track(s, catalog):
    """
        Takes a song object, created by manipulating v4 pyechonest.
        Downloads the audio for the song, as well as the full analysis.
        Synthesizes those into the return value, a remix AudioData object.
        
        returns None if either the audio or the analysis could not be found.
        
        Catalog specifies the audio source.
    """
    tracks = s.get_tracks(catalog=catalog, limit=True)
    t = None
    if tracks:
        track = tracks[0]
        
        filename = download(track.audio_url)
        if not os.path.exists(filename + '.json'):
            json = download(track.analysis_url)
            os.rename(json, filename + '.json')
        
        t = AnalyzedAudioFile(filename)
        if t:
            # fill in some things that are missing.
            t.analysis.name = s.title
            t.analysis.identifier = track.id
            t.analysis.metadata['artist'] = s.artist_name
            t.analysis.metadata['id'] = track.id
            t.analysis.metadata['title'] = s.title
            t.analysis.metadata['samplerate'] = t.sampleRate
    return t


def download(url):
    """Copy the contents of a file from a given URL to a local file in the current directory and returns the filename"""
    
    def fix_url(url):
        """urllib requires a properly url-encoded path."""
        parsed = urlparse.urlparse(url)
        parts = [parsed.scheme, '://', parsed.netloc, quote(parsed.path)] 
        if parsed.query:
            parts.extend(['?', parsed.query])
        return ''.join(parts)
        
    def get_filename(url):
        "get the part of the url that will make a good filename"
        parsed = urlparse.urlparse(url)
        return parsed.path.split('/')[-1]
    
    filename = get_filename(url)
    if not os.path.exists(filename):
        # print "Downloading %s to %s" % (fix_url(url), filename)
        urllib.urlretrieve(fix_url(url), filename)
    return filename
