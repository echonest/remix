class MidiOutStreamBase:


    """

    MidiOutStreamBase is Basically an eventhandler. It is the most central
    class in the Midi library. You use it both for writing events to
    an output stream, and as an event handler for an input stream.

    This makes it extremely easy to take input from one stream and
    send it to another. Ie. if you want to read a Midi file, do some
    processing, and send it to a midiport.

    All time values are in absolute values from the opening of a
    stream. To calculate time values, please use the MidiTime and
    MidiDeltaTime classes.

    """

    def __init__(self):
        
        # the time is rather global, so it needs to be stored 
        # here. Otherwise there would be no really simple way to 
        # calculate it. The alternative would be to have each event 
        # handler do it. That sucks even worse!
        self._absolute_time = 0
        self._relative_time = 0
        self._current_track = 0

    # time handling event handlers. They should overwritten with care

    def update_time(self, new_time=0, relative=1):
        """
        Updates the time, if relative is true, new_time is relative, 
        else it's absolute.
        """
        if relative:
            self._relative_time = new_time
            self._absolute_time += new_time
        else:
            self._absolute_time = new_time
            self._relative_time = new_time - self._absolute_time

    def rel_time(self):
        "Returns the relative time"
        return self._relative_time

    def abs_time(self):
        "Returns the absolute time"
        return self._absolute_time

    # track handling event handlers
    
    def set_current_track(self, new_track):
        "Sets the current track number"
        self._current_track = new_track
    
    def get_current_track(self):
        "Returns the current track number"
        return self._current_track
    
    
    #####################
    ## Midi events


    def channel_message(self, message_type, channel, data):
        """The default event handler for channel messages"""
        pass


    #####################
    ## Common events

    def system_exclusive(self, data):

        """The default event handler for system_exclusive messages"""
        pass


    def system_common(self, common_type, common_data):

        """The default event handler for system common messages"""
        pass


    #########################
    # header does not really belong here. But anyhoo!!!
    
    def header(self, format, nTracks, division):

        """
        format: type of midi file in [1,2]
        nTracks: number of tracks
        division: timing division
        """
        pass


    def start_of_track(self, n_track=0):

        """
        n_track: number of track
        """
        pass


    def eof(self):

        """
        End of file. No more events to be processed.
        """
        pass


    #####################
    ## meta events


    def meta_event(self, meta_type, data, time):
        
        """The default event handler for meta_events"""
        pass




if __name__ == '__main__':

    midiOut = MidiOutStreamBase()
    midiOut.update_time(0,0)
    midiOut.note_on(0, 63, 127)
    midiOut.note_off(0, 63, 127)

    