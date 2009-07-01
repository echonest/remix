#!/usr/bin/env python
# encoding: utf=8
#
# by Douglas Repetto, 10 June 2009
# plus code from various other examples and fixes by remix devs

"""
add_blips.py

Add a blip to any combination of each tatum/beat/bar in a song.

"""
import sys
import os.path
import numpy

import echonest.audio as audio

usage="""
Usage:
python add_blips.py <inputfilename><outputfilename> [tatums] [beats] [bars]

where 
    tatums == add blips to tatums
    beats == add blips to beats (default)
    bars == add blips to bars

Example:
python add_blips.py bootsy.mp3 bootsy_blips.mp3 beats bars

"""

blip_filenames = ('sounds/blip_low.wav', 'sounds/blip_med.wav', 'sounds/blip_high.wav')

#the blip.wav files are stored in the sounds/ directory relative to the 
#script. if the script is run from another directory those sounds won't
#be found. this fixes that problem.
prefix = os.path.dirname(os.path.abspath(sys.argv[0]))
blip_filenames = map(lambda x: os.path.join(prefix, x), blip_filenames)

def main(input_filename, output_filename, tatums, beats, bars):

    audiofile = audio.LocalAudioFile(input_filename)
    num_channels = audiofile.numChannels
    sample_rate = audiofile.sampleRate
    
    # mono files have a shape of (len,) 
    out_shape = list(audiofile.data.shape)
    out_shape[0] = len(audiofile)
    out = audio.AudioData(shape=out_shape, sampleRate=sample_rate,numChannels=num_channels)

    # same hack to change shape: we want blip_files[0] as a short, silent blip
    null_shape = list(audiofile.data.shape)
    null_shape[0] = 2
    null_audio = audio.AudioData(shape=null_shape)
    null_audio.endindex = len(null_audio)
    
    low_blip = audio.AudioData(blip_filenames[0])
    med_blip = audio.AudioData(blip_filenames[1])
    high_blip = audio.AudioData(blip_filenames[2])
    
    all_tatums = audiofile.analysis.tatums
    all_beats = audiofile.analysis.beats
    all_bars = audiofile.analysis.bars
            
    if not all_tatums:
        print "Didn't find any tatums in this analysis!"
        print "No output."
        sys.exit(-1)
    
    print "going to add blips..."
    
    for tatum in all_tatums:
        mix_list = [audiofile[tatum], null_audio, null_audio, null_audio]
        if tatums:
            print "match! tatum start time:" + str(tatum.start)
            mix_list[1] = low_blip

        if beats:
            for beat in all_beats:
                if beat.start == tatum.start:
                    print "match! beat start time: " + str(beat.start)
                    mix_list[2] = med_blip
                    break

        if bars:
            for bar in all_bars:
                if bar.start == tatum.start:
                    print "match! bar start time: " + str(bar.start)
                    mix_list[3] = high_blip
                    break
        out_data = audio.megamix(mix_list)
        out.append(out_data)
        del(out_data)
    print "blips added, going to encode", output_filename, "..."
    out.encode(output_filename)
    print "Finito, Benito!"


if __name__=='__main__':
    tatums = False
    beats = False
    bars = False
    try:
        input_filename = sys.argv[1]
        output_filename = sys.argv[2]
        if len(sys.argv) == 3:
            bars = 1
            print "blipping bars by default."
        for arg in sys.argv[3:len(sys.argv)]:
            if arg == "tatums":
                tatums = True
                print "blipping tatums."
            if arg == "beats":
                beats = True
                print "blipping beats."
            if arg == "bars":
                bars = True
                print "blipping bars."
    except:
        print usage
        sys.exit(-1)
    main(input_filename, output_filename, tatums, beats, bars)
