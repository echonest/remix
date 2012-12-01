class EventDispatcherBase:


    def __init__(self, outstream):
        """
        The event dispatcher generates events on the outstream. This 
        is the base implementation. It is more like an interface for 
        how the EventDispatcher. It has the methods that are used by 
        the Midi Parser.
        """
        # internal values, don't mess with 'em directly
        self.outstream = outstream


    def eof(self):
        "End of file!"
        self.outstream.eof()


    def update_time(self, new_time=0, relative=1):
        "Updates relative/absolute time."
        self.outstream.update_time(new_time, relative)

    # 'official' midi events

    def header(self, format, nTracks, division):
        "Triggers the header event"
        self.outstream.header(format, nTracks, division)


    def start_of_track(self, current_track):
        "Triggers the start of track event"
        
        # I do this twice so that users can overwrite the 
        # start_of_track event handler without worrying whether the 
        # track number is updated correctly.
        self.outstream.set_current_track(current_track)
        self.outstream.start_of_track(current_track)

    # Event dispatchers for midi events

    def channel_messages(self, hi_nible, channel, data):
        "Dispatches channel messages"
        self.outstream.channel_message(hi_nible, channel, data)


    def continuous_controllers(self, channel, controller, value):
        "Dispatches channel messages"
        self.outstream.continuous_controller(channel, controller, value)
    
    
    def system_commons(self, common_type, common_data):
        "Dispatches system common messages"
        self.outstream.system_common(common_type, common_data)


    def meta_event(self, meta_type, data):
        "Dispatches meta events"
        self.outstream.meta_event(meta_type, data)


    def sysex_events(self, data):
        "Dispatcher for sysex events"
        self.outstream.sysex_event(data)



if __name__ == '__main__':


    from MidiToText import MidiToText
    from constants import NOTE_ON
    
    outstream = MidiToText()
    dispatcher = EventDispatcherBase(outstream)
    dispatcher.channel_messages(NOTE_ON, 0x00, '\x40\x40')