#!/usr/bin/env python
# encoding: utf=8
"""
drums.py

Add drums to a song.

At the moment, only works with songs in 4, and endings are rough.

By Ben Lacker, 2009-02-24.
"""
# These lines import other things. 
import numpy
import sys
import time

# This line imports remix! 
import echonest.remix.audio as audio

usage="""
Usage:
    python drums.py <inputfilename> <breakfilename> <outputfilename> <beatsinbreak> <barsinbreak> [<drumintensity>]

Example:
    python drums.py HereComesTheSun.mp3 breaks/AmenBrother.mp3 HereComeTheDrums.mp3 64 4 0.6

Drum intensity defaults to 0.5
"""

# Drums is pretty complex!
# Hold on, and we'll try to make everything make sense.
# Drums adds a new drum break to the track.  
# It does this by splitting the drum break into its component beats and tatums.
# Then, for every tatum in the input track, it mixes in the appropriate tatum of the break.
# That is to say, it is mapping every beat of the break to the beat of the input track.


    # This converts a mono file to stereo. It is used in main() to make sure that the input break stereo
def mono_to_stereo(audio_data):
    data = audio_data.data.flatten().tolist()
    new_data = numpy.array((data,data))
    audio_data.data = new_data.swapaxes(0,1)
    audio_data.numChannels = 2
    return audio_data

    # This splits the break into each beat
def split_break(breakfile,n):
    drum_data = []
    start = 0
    for i in range(n):
        start = int((len(breakfile) * (i))/n)
        end = int((len(breakfile) * (i+1))/n)
        ndarray = breakfile.data[start:end]
        new_data = audio.AudioData(ndarray=ndarray,
                                    sampleRate=breakfile.sampleRate,
                                    numChannels=breakfile.numChannels)
        drum_data.append(new_data)
    return drum_data
    

    # This is where things happen
def main(input_filename, output_filename, break_filename, break_parts, measures, mix):

    # This takes the input tracks, sends them to the analyzer, and returns the results.  
    audiofile = audio.LocalAudioFile(input_filename)
    sample_rate = audiofile.sampleRate
    breakfile = audio.LocalAudioFile(break_filename)

    # This converts the break to stereo, if it is mono
    if breakfile.numChannels == 1:
        breakfile = mono_to_stereo(breakfile)

    # This gets the number of channels in the main file
    num_channels = audiofile.numChannels

    # This splits the break into each beat
    drum_data = split_break(breakfile, break_parts)
    hits_per_beat = int(break_parts/(4 * measures))
    # This gets the bars from the input track
    bars = audiofile.analysis.bars
    
    # This creates the 'shape' of new array.
    # (Shape is a tuple (x, y) that indicates the length per channel of the audio file)
    out_shape = (len(audiofile)+100000,num_channels)
    # This creates a new AudioData array to write data to
    out = audio.AudioData(shape=out_shape, sampleRate=sample_rate,
                            numChannels=num_channels)
    if not bars:
        # If the analysis can't find any bars, stop!
        # (This might happen with really ambient music)
        print "Didn't find any bars in this analysis!"
        print "No output."
        sys.exit(-1)

    # This is where the magic happens:
    # For every beat in every bar except the last bar, 
    # map the tatums of the break to the tatums of the beat
    for bar in bars[:-1]:
        # This gets the beats in the bar, and loops over them
        beats = bar.children()
        for i in range(len(beats)):
            # This gets the index of matching beat in the break
            try:
                break_index = ((bar.local_context()[0] %\
                                measures) * 4) + (i % 4)
            except ValueError:
                break_index = i % 4
            # This gets the tatums from the beat of the break
            tats = range((break_index) * hits_per_beat,
                        (break_index + 1) * hits_per_beat)
            # This gets the number of samples in each tatum
            drum_samps = sum([len(drum_data[x]) for x in tats])

            # This gets the number of sample and the shape of the beat from the original track
            beat_samps = len(audiofile[beats[i]])
            beat_shape = (beat_samps,num_channels)
            
            # This get the shape of each tatum
            tat_shape = (float(beat_samps/hits_per_beat),num_channels)
        
            # This creates the new AudioData that will be filled with chunks of the drum break
            beat_data= audio.AudioData(shape=beat_shape,
                                        sampleRate=sample_rate,
                                        numChannels=num_channels)
            for j in tats:
                # This creates an audioData for each tatum
                tat_data= audio.AudioData(shape=tat_shape,
                                            sampleRate=sample_rate,
                                            numChannels=num_channels)
                # This corrects for length / timing:
                # If the original is shorter than the break, truncate drum hits to fit beat length
                if drum_samps > beat_samps/hits_per_beat:
                    tat_data.data = drum_data[j].data[:len(tat_data)]
                # If the original is longer, space out drum hits to fit beat length
                elif drum_samps < beat_samps/hits_per_beat:
                    tat_data.append(drum_data[j])

                # This adds each new tatum to the new beat.
                tat_data.endindex = len(tat_data)
                beat_data.append(tat_data)
                del(tat_data)

            # This corrects for rounding errors
            beat_data.endindex = len(beat_data)

            # This mixes the new beat data with the input data, and appends it to the final file
            mixed_beat = audio.mix(beat_data, audiofile[beats[i]], mix=mix)
            del(beat_data)
            out.append(mixed_beat)

    # This works out the last beat and appends it to the final file
    finale = bars[-1].start + bars[-1].duration
    last = audio.AudioQuantum(audiofile.analysis.bars[-1].start,
                            audiofile.analysis.duration - 
                              audiofile.analysis.bars[-1].start)
    last_data = audio.getpieces(audiofile,[last])
    out.append(last_data)
    
    # This writes the newly created audio to the given file.  
    out.encode(output_filename)

    # The wrapper for the script.  
if __name__=='__main__':
    try:
        # This gets the filenames to read from and write to, 
        # and sets the number of beats and bars in the break, and the mix level
        input_filename = sys.argv[1]
        break_filename = sys.argv[2]
        output_filename = sys.argv[3]
        break_parts = int(sys.argv[4])
        measures = int(sys.argv[5])
        if len(sys.argv) == 7:
            mix = float(sys.argv[6])
        else:
            mix = 0.5
    except:
        # If things go wrong, exit!
        print usage
        sys.exit(-1)
    main(input_filename, output_filename, break_filename, break_parts,
            measures, mix)
