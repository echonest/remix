"""
A Python interface to the The Echo Nest's Analyze web API.  See
http://developer.echonest.com/ for details.  Audio analysis is returned
as XML objects.
"""

__version__ = "$Revision: 0 $"
# $Source$

# Standard library modules.
import os
import urllib

# Modules in this package.
import echonest.web.config as config
import echonest.web.util as util


def upload( filename ) :
    """
    Upload a track to The Echo Nest's analyzer for analysis and later
    retrieval of track information.

    @param filename Either the path to a local file or a valid URL.

    @return (id, info)
    """
    fields = { "api_key" : config.API_KEY,
               "wait" : "Y" }
    method = 'upload'
    if os.path.isfile( filename ) : 
        response = util.postChunked( host = config.API_HOST, 
                                     selector = config.API_SELECTOR + method,
                                     fields = fields.items(), 
                                     files = (( 'file', open(filename, 'r')), )
                                     )
    else :
        print "it's a url"
        # Assume the filename is a URL.
        fields['url'] = filename
        params = urllib.urlencode(fields)
        url = 'http://%s%s%s?%s' % (config.API_HOST, config.API_SELECTOR, method, params)
        f = urllib.urlopen( url )
        response = f.read()
    return util.parseXMLString(response)



def get_bars( id ) :
    """
    Retrieve the number of bars of a track after previously calling
    for analysis via upload.

    @param id The track identifier. 
    """
    return util.apiFunctionPrototype( 'get_bars', id )



def get_beats( id ) :
    """
    Retrieve the number of beats of a track after previously calling
    for analysis via upload.

    @param id The track identifier. 
    """
    return util.apiFunctionPrototype( 'get_beats', id )


           
def get_duration( id ) :
    """
    Retrieve the duration of a track after previously calling for
    analysis via upload.

    @param id The track identifier. 
    """
    return util.apiFunctionPrototype( 'get_duration', id )


           
def get_end_of_fade_in( id ) :
    """
    Retrieve the end of the fade-in introduction to a track after
    previously calling for analysis via upload.

    @param id The track identifier. 
    """
    return util.apiFunctionPrototype( 'get_end_of_fade_in', id )


           
def get_key( id ) :
    """
    Retrieve the key of a track after previously calling for analysis
    via upload.

    @param id The track identifier. 
    """
    return util.apiFunctionPrototype( 'get_key', id )


           
def get_loudness( id ) :
    """
    Retrieve the loudness of a track after previously calling for
    analysis via upload.

    @param id The track identifier. 
    """
    return util.apiFunctionPrototype( 'get_loudness', id )


           
def get_metadata( id ) :
    """
    Retrieve the metadata for a track after previously calling for
    analysis via upload.

    @param id The track identifier. 
    """
    return util.apiFunctionPrototype( 'get_metadata', id )


           
def get_mode( id ) :
    """
    Retrieve the mode of a track after previously calling for analysis
    via upload.

    @param id The track identifier. 
    """
    return util.apiFunctionPrototype( 'get_mode', id )


           
def get_sections( id ) :
    """
    Retrieve the number of sections of a track after previously
    calling for analysis via upload.

    @param id The track identifier. 
    """
    return util.apiFunctionPrototype( 'get_sections', id )


           
def get_segments( id ) :
    """
    Retrieve the number of segments of a track after previously
    calling for analysis via upload.

    @param id The track identifier. 
    """
    return util.apiFunctionPrototype( 'get_segments', id )


           
def get_start_of_fade_out( id ) :
    """
    Retrieve the start of the fade out at the end of a track after
    previously calling for analysis via upload.

    @param id The track identifier. 
    """
    return util.apiFunctionPrototype( 'get_start_of_fade_out', id )


           
def get_tatums( id ) :
    """
    Retrieve the tatums of a track after previously calling for
    analysis via upload.

    @param id The track identifier. 
    """
    return util.apiFunctionPrototype( 'get_tatums', id )


           
def get_tempo( id ) :
    """
    Retrieve the tempo of a track after previously calling for
    analysis via upload.

    @param id The track identifier. 
    """
    return util.apiFunctionPrototype( 'get_tempo', id )


           
def get_time_signature( id ) :
    """
    Retrieve the time signature of a track after previously calling
    for analysis via upload.

    @param id The track identifier. 
    """
    return util.apiFunctionPrototype( 'get_time_signature', id )
           
