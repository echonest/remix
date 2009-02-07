from MidiOutFile import MidiOutFile

"""
This is an example of the smallest possible type 0 midi file, where 
all the midi events are in the same track.
"""

out_file = 'midiout/minimal_type0.mid'
midi = MidiOutFile(out_file)

# non optional midi framework
midi.header()
midi.start_of_track() 


# musical events

midi.update_time(0)
midi.note_on(channel=0, note=0x40)

midi.update_time(192)
midi.note_off(channel=0, note=0x40)


# non optional midi framework
midi.update_time(0)
midi.end_of_track()

midi.eof()
