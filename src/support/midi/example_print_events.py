from MidiToText import MidiToText

"""
This is an example that uses the MidiToText eventhandler. When an 
event is triggered on it, it prints the event to the console.
"""

midi = MidiToText()

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
midi.end_of_track() # not optional!

midi.eof()
