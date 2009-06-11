#!/usr/bin/env python
# encoding: utf=8
#
# by Douglas Repetto, 10 June 2009
# using code from various other examples...

"""
add_blips.py

Add a blip to any combination of each tatum/beat/bar in a song.

"""
import sys
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

#this seems really dumb but I can't figure out how else to do it
#one sound file for each possible combination of tatum/beat/bar

blip_filenames = ('sounds/blip_low.wav', 'sounds/blip_med.wav', 'sounds/blip_low_med.wav',
	'sounds/blip_high.wav', 'sounds/blip_low_high.wav', 'sounds/blip_med_high.wav', 
	'sounds/blip_low_med_high.wav')


def main(input_filename, output_filename, tatums, beats, bars):

	audiofile = audio.LocalAudioFile(input_filename)
	num_channels = audiofile.numChannels
	sample_rate = audiofile.sampleRate
	
	# mono files have a shape of (len,) 
	out_shape = list(audiofile.data.shape)
	out_shape[0] = len(audiofile)+100000
	out = audio.AudioData(shape=out_shape, sampleRate=sample_rate,numChannels=num_channels)
	
	# same hack to change shape: we want blip_files[0] as a short, silent blip
	null_shape = list(audiofile.data.shape)
	null_shape[0] = 2
	null_audio = audio.AudioData(shape=null_shape)
	null_audio.endindex = len(null_audio)
	blip_files = [null_audio]
	
	for name in blip_filenames:
		blip_files.append(audio.AudioData(name))

	#tatum_blip_file = audio.LocalAudioFile(tatum_blip)
	
	all_tatums = audiofile.analysis.tatums
	all_beats = audiofile.analysis.beats
	all_bars = audiofile.analysis.bars
			
	if not all_tatums:
		print "Didn't find any tatums in this analysis!"
		print "No output."
		sys.exit(-1)
	
	print "going to add blips..."
	

	
	for tatum in all_tatums:
		sound_to_use = 0
  		
		if tatums == 1:
			print "match! tatum start time:" + str(tatum.start)
			sound_to_use = sound_to_use + 1

		if beats == 1:
			for beat in all_beats:
				if beat.start == tatum.start:
					print "match! beat start time: " + str(beat.start)
					sound_to_use = sound_to_use + 2
					break

		if bars == 1:
			for bar in all_bars:
				if bar.start == tatum.start:
					print "match! bar start time: " + str(bar.start)
					sound_to_use = sound_to_use + 4
					break
					
		
		print "mixing blip soundfile: ", blip_filenames[sound_to_use]
		out_data = audio.mix(audiofile[tatum], blip_files[sound_to_use], 0.5)
		out.append(out_data)
		del(out_data)
		
		
	print "blips added, going to encode", output_filename, "..."
	out.encode(output_filename)
	print "Finito, Benito!"
		
		

if __name__=='__main__':

	tatums = 0
	beats = 0
	bars = 0

	try:
		input_filename = sys.argv[1]
		output_filename = sys.argv[2]
		
		if len(sys.argv) == 3:
			bars = 1
			print "blipping bars by default."
	
		for arg in sys.argv[3:len(sys.argv)]:
			if arg == "tatums":
				tatums = 1
				print "blipping tatums."
			if arg == "beats":
				beats = 1
				print "blipping beats."
			if arg == "bars":
				bars = 1
				print "blipping bars."
	
	except:
		print usage
		sys.exit(-1)


	
	main(input_filename, output_filename, tatums, beats, bars)
	
