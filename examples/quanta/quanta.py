#!/usr/bin/env python
# encoding: utf=8

"""
quanta.py

Insert silences between a song's segments, tatums, beats, or sections.
Demonstrates the Remix API's handling of audio quanta.

By Ben Lacker 2009-3-4, updated by Thor Kell, 2012-9-26
"""
import sys

import echonest.audio as audio

usage = """
Usage: 
    python quanta.py <segments|tatums|beats|bars|sections> <inputfilename> <outputfilename> [e]

Example:
    python quanta.py beats SingleLadies.mp3 SingleLadiesBeats.mp3
    
The 'e' flag, inserts a silence equal in duration to the preceding audio quantum.
Otherwise, each silence is one second long.
"""

ACCEPTED_UNITS = ["segments", "tatums", "beats", "bars", "sections"]

def main(input_filename, output_filename, units, equal_silence):
    audio_file = audio.LocalAudioFile(input_filename)   
    chunks = audio_file.analysis.__getattribute__(units)
    num_channels = audio_file.numChannels
    sample_rate = audio_file.sampleRate
    if equal_silence:
        new_shape = ((audio_file.data.shape[0] * 2) + 100000,
                        audio_file.data.shape[1])
    else:
        new_shape = (audio_file.data.shape[0]+(len(chunks) * 44100) + 10000,
                        audio_file.data.shape[1])
    out = audio.AudioData(shape=new_shape, sampleRate=sample_rate, numChannels=num_channels)

    for chunk in chunks:
        chunk_data = audio_file[chunk]
        if equal_silence:
            silence_shape = chunk_data.data.shape
        else:
            silence_shape = (44100, audio_file.data.shape[1])
        silence = audio.AudioData(shape=silence_shape, sampleRate=sample_rate, numChannels=num_channels)
        silence.endindex = silence.data.shape[0]

        out.append(chunk_data)
        out.append(silence)
    out.encode(output_filename)

if __name__ == '__main__':
    try:
        units = sys.argv[1]
        input_filename = sys.argv[2]
        output_filename = sys.argv[3]
        if len(sys.argv) == 5:
            equal_silence = True
        else:
            equal_silence = False
    except:
        print usage
        sys.exit(-1)
    if not units in ACCEPTED_UNITS:
        print usage
        sys.exit(-1)
    main(input_filename, output_filename, units, equal_silence)
