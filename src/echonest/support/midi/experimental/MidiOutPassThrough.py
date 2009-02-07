from MidiOutStream import MidiOutStream

class MidiOutPassThrough(MidiOutStream):


    """

    This class i mainly used for testing the event dispatcher. The 
    methods just returns the passed parameters as a tupple.

    """


    #####################
    ## Midi channel events


    def note_on(self, channel, note, velocity, time=None):
        return channel, note, velocity, time


    def note_off(self, channel, note, velocity, time=None):
        return channel, note, velocity, time


    def aftertouch(self, channel, note, velocity, time=None):
        return channel, note, velocity, time

        
    def continuous_controller(self, channel, controller, value, time=None):
        return channel, controller, value, time


    def patch_change(self, channel, patch, time=None):
        return channel, patch, time


    def channel_pressure(self, channel, pressure, time=None):
        return channel, pressure, time


    #####################
    ## defined continuous controller events
    
#    def cc_

    #####################
    ## Common events

    def system_exclusive(self, data, time=None):
        return data, time


    def song_position_pointer(self, hiPos, loPos, time=None):
        return hiPos, loPos, time


    def song_select(self, songNumber, time=None):
        return songNumber, time


    def tuning_request(self, time=None):
        return time



    #########################
    # header does not really belong here. But anyhoo!!!
    
    def header(self, format, nTracks, division):
        return format, nTracks, division


    def eof(self):
        return 'eof'


    #####################
    ## meta events

    def start_of_track(self, n_track=0):
        return n_track


    def end_of_track(self, n_track=0, time=None):
        return n_track, time


    def sequence_number(self, hiVal, loVal, time=None):
        return hiVal, loVal, time


    def text(self, text, time=None):
        return text, time


    def copyright(self, text, time=None):
        return text, time


    def sequence_name(self, text, time=None):
        return text, time


    def instrument_name(self, text, time=None):
        return text, time


    def lyric(self, text, time=None):
        return text, time


    def marker(self, text, time=None):
        return text, time


    def cuepoint(self, text, time=None):
        return text, time


    def midi_port(self, value, time=None):
        return value, time


    def tempo(self, value, time=None):
        return value, time

    def smtp_offset(self, hour, minute, second, frame, framePart, time=None):
        return hour, minute, second, frame, framePart, time


    def time_signature(self, nn, dd, cc, bb, time=None):
        return nn, dd, cc, bb, time


    def key_signature(self, sf, mi, time=None):
        return sf, mi, time


    def sequencer_specific(self, data, time=None):
        return data, time




    #####################
    ## realtime events

    def timing_clock(self, time=None):
        return time


    def song_start(self, time=None):
        return time


    def song_stop(self, time=None):
        return time


    def song_continue(self, time=None):
        return time


    def active_sensing(self, time=None):
        return time


    def system_reset(self, time=None):
        return time





if __name__ == '__main__':

    midiOut = MidiOutStream()
    midiOut.note_on(0, 63, 127, 0)
    midiOut.note_off(0, 63, 127, 384)

    