#!/usr/bin/env python
# encoding: utf=8

"""
quanta.py

Insert silences between a song's segments, tatums, beats, or sections.
Demonstrates the Remix API's handling of audio quanta.

By Ben Lacker 2009-3-4.
"""

import echonest.audio as audio

usage = """
Usage: 
    python quanta.py <segments|tatums|beats|bars|sections> <inputfilename> <outputfilename> [e]

Example:
    python quanta.py beats SingleLadies.mp3 SingleLadiesBeats.mp3
    
The 'e' flag, inserts a silence equal in duration to the preceding audio quantum.
Otherwise, each silence is one second long.
"""



def main(input_filename,output_filename,quanta,equal_silence):
    audio_file = audio.LocalAudioFile(input_filename)
    if quanta == 'segments':
        chunks = audio_file.analysis.segments
    elif quanta == 'tatums':
        chunks = audio_file.analysis.tatums
    elif quanta == 'beats':
        chunks = audio_file.analysis.tatums
    elif quanta == 'bars':
        chunks = audio_file.analysis.bars
    elif quanta == 'sections':
        chunks = audio_file.analysis.sections
    num_channels = audio_file.numChannels
    sample_rate = audio_file.sampleRate
    if equal_silence:
        new_shape = ((audio_file.data.shape[0]*2)+100000,
                        audio_file.data.shape[1])
    else:
        new_shape = (audio_file.data.shape[0]+(len(chunks)*44100)+10000,
                        audio_file.data.shape[1])
    out = audio.AudioData(shape=new_shape,sampleRate=sample_rate,
                            numChannels=num_channels)
    for chunk in chunks:
        chunk_data = audio_file[chunk]
        if equal_silence:
            silence_shape = chunk_data.data.shape
        else:
            silence_shape = (44100,chunk_data.data.shape[1])
        silence = audio.AudioData(shape=silence_shape,
                                sampleRate=sample_rate,
                                numChannels=num_channels)
        out.append(chunk_data)
        out.append(silence)
    out.encode(output_filename)

if __name__ == '__main__':
    import sys
    try :
        quanta = sys.argv[1]
        input_filename = sys.argv[2]
        output_filename = sys.argv[3]
        if len(sys.argv) == 5:
            equal_silence = True
        else:
            equal_silence = False
    except :
        print usage
        sys.exit(-1)
    main(input_filename,output_filename,quanta,equal_silence)
