#!/usr/bin/env python
# encoding: utf-8
"""
Test that an Echo-Nest-Remix-compatible version of ffmpeg is installed.

Run the tests like this:
    python test_ffmpeg.py
    
If you want to test that your version of ffmpeg can handle a particular file, 
(like if you're planning on analyzing OggVorbis files and want to make sure
your ffmpeg can decode them), run like this:
    python test_ffmpeg.py my_crazy_audio_file.mp47
"""

import os
import sys
import tempfile

from echonest import audio

def main():
    """Run some tests"""
    if len(sys.argv) > 1:
        input_filename = sys.argv[1]
    else:
	    input_filename = 'input_file.mp3'
    test_en_ffmpeg_exists(input_filename)
    test_round_trip(input_filename)

def test_en_ffmpeg_exists(input_filename):
    """Don't do any conversion, just see if en-ffmpeg, the command used
    by Remix, is installed."""
    result = audio.ffmpeg(input_filename, overwrite=False, verbose=True)
    audio.ffmpeg_error_check(result[1])

def test_round_trip(input_filename):
    """Convert the input file to a wav file, then back to an mp3 file."""
    result = audio.ffmpeg(input_filename, overwrite=False, verbose=True)
    audio.ffmpeg_error_check(result[1])
    sampleRate, numChannels = audio.settings_from_ffmpeg(result[1])
    
    temp_file_handle, temp_filename = tempfile.mkstemp(".wav")
    result = audio.ffmpeg(input_filename, temp_filename, overwrite=True, 
        numChannels=numChannels, sampleRate=sampleRate, verbose=True)
    audio.ffmpeg_error_check(result[1])
    
    temp_filesize = os.path.getsize(temp_filename)
    print 'temp file size: %s bytes' % temp_filesize
    
    output_filename = 'output_file.mp3'
    result = audio.ffmpeg(temp_filename, output_filename, overwrite=True, 
        numChannels=numChannels, sampleRate=sampleRate, verbose=True)
    audio.ffmpeg_error_check(result[1])
    
    if temp_file_handle is not None:
        os.close(temp_file_handle)
        os.remove(temp_filename)
    
    input_filesize = os.path.getsize(input_filename)
    output_filesize = os.path.getsize(output_filename)
    difference = output_filesize - input_filesize
    args = (input_filesize, output_filesize, difference)
    print 'input file size: %s bytes | output file size: %s bytes | difference: %s bytes ' % args
    if abs(int(difference)) > 1000:
        print 'input and output files are different sizes. something might be wrong with your ffmpeg.'
    else:
        print 'Ok!'

if __name__ == '__main__':
	main()

