#!/usr/bin/env python
# encoding: utf=8

"""
drums.py

Add drums to a song.

At the moment, only works with songs in 4, and endings are rough.

By Ben Lacker, 2009-02-24.
"""
import numpy
import sys
import time
import echonest.audio as audio

usage="""
Usage:
    python drums.py <inputfilename> <outputfilename> [<drumIntensity>]

Example:
    python drums.py HereComesTheSun.mp3 HereComeTheDrums.mp3 0.6
    
Drum Intensity defaults to 0.5.
"""

BREAK_FILENAME = 'FunkyDrummer.wav'

def mono_to_stereo(audio_data):
    data = audio_data.data.flatten().tolist()
    new_data = numpy.array((data,data))
    audio_data.data = new_data.swapaxes(0,1)
    audio_data.numChannels = 2
    return audio_data

def add_drums(input_filename,output_filename,mix=0.5):
    audiofile = audio.LocalAudioFile(input_filename)
    sample_rate = audiofile.sampleRate
    breakfile = audio.LocalAudioFile(BREAK_FILENAME)
    if breakfile.numChannels == 1:
        breakfile = mono_to_stereo(breakfile)
    num_channels = audiofile.numChannels
    drums = breakfile.analysis.tatums[:16]
    bars = audiofile.analysis.bars
    out_shape = (len(audiofile)+100000,num_channels)
    out = audio.AudioData(shape=out_shape, sampleRate=sample_rate,
                            numChannels=num_channels)
    for bar in bars:
        beats = bar.children()
        for i in range(len(beats)):
            tats = range((i % 4) * 4, ((i % 4) * 4) + 4)
            drum_samps = sum([len(breakfile[drums[x]]) for x in tats])
            beat_samps = len(audiofile[beats[i]])
            beat_shape = (beat_samps,num_channels)
            tat_shape = (float(beat_samps/4),num_channels)
            beat_data= audio.AudioData(shape=beat_shape,
                                        sampleRate=sample_rate,
                                        numChannels=num_channels)
            for j in tats:
                tat_data= audio.AudioData(shape=tat_shape,
                                            sampleRate=sample_rate,
                                            numChannels=num_channels)
                if drum_samps > beat_samps/4:
                    # truncate drum hits to fit beat length
                    tat_data.data = breakfile[drums[j]].data[:len(tat_data)]
                elif drum_samps < beat_samps/4:
                    # space out 16th notes of drums to fit beat length
                    tat_data.append(breakfile[drums[j]])
                tat_data.endindex = len(tat_data)
                beat_data.append(tat_data)
                del(tat_data)
            # account for round errors
            beat_data.endindex = len(beat_data)
            mixed_beat = audio.mix(beat_data,audiofile[beats[i]],mix=mix)
            del(beat_data)
            out.append(mixed_beat)
    out.encode(output_filename)

def main():
    try:
        input_filename = sys.argv[1]
        output_filename = sys.argv[2]
        if len(sys.argv) == 4:
            mix = sys.argv[3]
        else:
            mix = 0.5
    except:
        print usage
        sys.exit(-1)
    add_drums(input_filename,output_filename,mix=mix)

if __name__=='__main__':
    tic = time.time()
    main()
    toc = time.time()
    print "Elapsed time: %.3f sec" % float(toc-tic)
