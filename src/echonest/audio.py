"""
A module that wraps echonest.web to allow for more sophisticated
manipulation of audio files and their analyses.
"""

__version__ = "$Revision: 0 $"
# $Source$

import echonest.web.analyze as analyze;

class AudioTrack(object) :
    """
    This class wraps echonest.web to allow transparent caching of the
    audio analysis of an audio file.

    For example, the following script will display the bars of a
    track twice:
    
        from echonest import *
        a = audio.AudioTrack('YOUR_TRACK_ID_HERE')
        a.bars
        a.bars

    The first time a.bars is called, a network request is made of the
    Echo Nest anaylze API.  The second time time a.bars is called, the
    cached value is returned immediately.

    An AudioTrack object can be created using an existing ID, as in
    the example above, or by specifying the audio file to upload in
    order to create the ID, as in:

        a = audio.AudioTrack(filename='FULL_PATH_TO_AUDIO_FILE')
    """

    # Any variable in this listing is fetched over the network once
    # and then cached.  Calling refreshCachedVariables will force a
    # refresh.
    CACHED_VARIABLES = ( 'bars', 
                         'beats', 
                         'duration', 
                         'end_of_fade_in', 
                         'key',
                         'loudness',
                         'metadata',
                         'mode',
                         'sections',
                         'segments',
                         'start_of_fade_out',
                         'tatums',
                         'tempo',
                         'time_signature' )

    def __init__( self, id=None, filename=None ) :
        """
        Constructor.  The first argument that is not None is used to
        initialize the track.  Set the id argument if the audio file
        has already been uploaded to the Echo Nest web service for
        analysis, otherwise specify the filename argument and the
        audio file will be uploaded as part of the creation of the
        AudioTrack object.
        
        @param id A string representing the id of an audio file that
        has already been uploaded for analysis.

        @param filename A string representing the full path or URL to
        an audio file that has yet to be uploaded for analysis.

        """

        # Error checking of constructor arguments.
        if id is None :
            if filename is None :
                raise TypeError("One of 'id' and 'filename' must not be None.")
            elif type(filename) is str :
                doc = analyze.upload(filename)
                self.id = doc.getElementsByTagName('thingID')[0].firstChild.data
            else : 
                raise TypeError("Argument 'filename' must be of type None or str.")
        elif type(id) is str :
            self.id = id
        else :
            raise TypeError("Argument 'id' must be of type None or str.")

        # Initialize cached variables to None.
        for cachedVar in AudioTrack.CACHED_VARIABLES : 
            self.__setattr__(cachedVar, None)



    def refreshCachedVariables( self ) :
        """
        Forces all cached variables to be updated over the network.
        """
        for cachedVar in AudioTrack.CACHED_VARIABLES : 
            self.__setattr__(cachedVar, None)
            self.__getattribute__(cachedVar)
        


    def __getattribute__( self, name ) :
        """
        This function has been modified to support caching of
        variables retrieved over the network.
        """
        if name in AudioTrack.CACHED_VARIABLES :
            if object.__getattribute__(self, name) is None :
                getter = analyze.__dict__[ 'get_' + name ]
                value = getter(object.__getattribute__(self, 'id'))
                self.__setattr__(name, value)
        return object.__getattribute__(self, name)
