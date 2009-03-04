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
    python quanta.py <segments|tatums|beats|bars|sections> <inputfilename> <outputfilename>

Example:
    python quanta.py beats SingleLadies.mp3 SingleLadiesBeats.mp3
"""



def main(input_filename,output_filename,quanta) :
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
    new_shape = ((audio_file.data.shape[0]*2)+100000,audio_file.data.shape[1])
    out = audio.AudioData(shape=new_shape,sampleRate=sample_rate,
                            numChannels=num_channels)
    for chunk in chunks:
        chunk_data = audio_file[chunk]
        silence = audio.AudioData(shape=chunk_data.data.shape,
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
    except :
        print usage
        sys.exit(-1)
    main(input_filename,output_filename,quanta)
