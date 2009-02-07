from MidiOutFile import MidiOutFile
from MidiInFile import MidiInFile

"""
This is an example of the smallest possible type 0 midi file, where 
all the midi events are in the same track.
"""


class Transposer(MidiOutFile):
    
    "Transposes all notes by 1 octave"
    
    def _transp(self, ch, note):
        if ch != 9: # not the drums!
            note += 12
            if note > 127:
                note = 127
        return note


    def note_on(self, channel=0, note=0x40, velocity=0x40):
        note = self._transp(channel, note)
        MidiOutFile.note_on(self, channel, note, velocity)
        
        
    def note_off(self, channel=0, note=0x40, velocity=0x40):
        note = self._transp(channel, note)
        MidiOutFile.note_off(self, channel, note, velocity)


out_file = 'midiout/transposed.mid'
midi_out = Transposer(out_file)

#in_file = 'midiout/minimal_type0.mid'
#in_file = 'test/midifiles/Lola.mid'
in_file = 'test/midifiles/tennessee_waltz.mid'
midi_in = MidiInFile(midi_out, in_file)
midi_in.read()

