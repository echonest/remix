# By Tristan Jehan, based on cowbell.py, itself based on previous jingler code.
# This script takes an mp3 file and produces an mp3 file dubbed with synchronized sleighbells
# and other christmassy sounds.

import echonest.audio as audio
import lame, mad, numpy, eyeD3
import os, random, time

usage = """
# For this script to work properly, you need to install the Echo Nest Remix API: 
# http://code.google.com/p/echo-nest-remix/ (where you should have found this script)
# You also need to install FFmpeg, lame, and the following python modules: 
# py-lame, eyeD3, numpy, and pymad (as distributed by the Echo Nest in the cowbell example).
# Update the '/echo-nest-remix/src/echonest/web/config.py' file with your own developer key.

Usage: 
    python jingler.py <inputFilename> <outputFilename>
Example:
    python jingler.py aha.mp3 aha_Jingled.mp3
Reference:
    http://www.thejingler.com
"""

# constants
SLEIGH_OFFSET = -0.2
SIGNAL_OFFSET = -1.0

# samples
soundsPath = "sounds/"

sleighBellSounds = map(lambda x: audio.AudioData(os.path.join(soundsPath, "sleighBell%s.wav" % x), sampleRate=44100, numChannels=2), range(1))
signalBellSounds = map(lambda x: audio.AudioData(os.path.join(soundsPath, "signalBell%s.wav" % x), sampleRate=44100, numChannels=2), range(1))

# some math useful for normalization
def linear(input, in1, in2, out1, out2):
    return ((input-in1) / (in2-in1)) * (out2-out1) + out1

def exp(input, in1, in2, out1, out2, coeff):
    if (input <= in1): return out1
    if (input >= in2): return out2
    return pow( ((input-in1) / (in2-in1)) , coeff ) * (out2-out1) + out1

class Jingler:
    def __init__(self, audio, loudness, beats, sections):
        # load audio, normalize it with samples
        t1 = time.time()
        mf = mad.MadFile(audio)
        self.audiodata = numpy.array(mf.readall(), dtype=numpy.int16)
        self.audiodata *= linear(loudness, -2, -12, 0.5, 1.2) * 0.75
        self.audiodata = self.audiodata.reshape(len(self.audiodata) / 2, 2)
        print "Loaded/Normalized audio in %g secs" % (time.time() - t1)
        self.audiorate = mf.samplerate()    
        self.audiochannels = 2 # force it
        self.beats = beats
        self.sections = sections


    def run(self, out):
        # sequence and mix
        t1 = time.time()
        sequence = self.sequence(sleighBellSounds)
        print "Sequenced and mixed in %g secs" % (time.time() - t1)
        # save
        t1 = time.time()
        self.encode(out)
        print "Encoded in %g secs" % (time.time() - t1)


    def sequence(self, chops):
        # add sleigh bells on the beats
        for beat in self.beats:
            sample = sleighBellSounds[0]
            self.mix(beat.start+SLEIGH_OFFSET, seg=sample, volume=0.6)
        # add signal bells on section changes
        for section in self.sections[1:]:
            sample = signalBellSounds[0]
            self.mix(start=section.start+SIGNAL_OFFSET, seg=sample, volume=0.6)


    def mix(self, start=None, seg=None, volume=0.3, pan=0.):
        # this assumes that the audios have the same samplerate/numchannels
        startsample = int(start * self.audiorate)
        seg = seg[0:]
        seg.data *= (volume-(pan*volume), volume+(pan*volume)) # pan and volume
        if self.audiodata.shape[0] - startsample > seg.data.shape[0]:
            self.audiodata[startsample:startsample+len(seg.data)] += seg.data[0:] # mix


    def encode(self, mp3_path):
        sampwidth = 2
        nframes = len(self.audiodata) / self.audiochannels
        raw_size = self.audiochannels * sampwidth * nframes
        mp3_file = open(mp3_path, "wb+")
        mp3 = lame.init()
        mp3.set_num_channels(self.audiochannels)
        mp3.set_in_samplerate(self.audiorate)
        mp3.set_num_samples(long(nframes))
        mp3.init_parameters()
        # 1 sample = 2 bytes
        num_samples_per_enc_run = self.audiorate
        num_bytes_per_enc_run = self.audiochannels * num_samples_per_enc_run * sampwidth
        start = 0
        while True:
            frames = self.audiodata[start:start+num_samples_per_enc_run].tostring()
            data = mp3.encode_interleaved(frames)
            mp3_file.write(data)
            start = start + num_samples_per_enc_run
            if start >= len(self.audiodata): break
        mp3_file.write(mp3.flush_buffers())
        mp3.write_tags(mp3_file)
        mp3_file.close()
        mp3.delete()


def write_tags(path, metadata):
    tag = eyeD3.Tag()
    tag.link(path)
    tag.header.setVersion(eyeD3.ID3_V2_3)
    if metadata.has_key('artist'):
        tag.setArtist(metadata['artist'])
    if metadata.has_key('release'):
        tag.setAlbum(metadata['release'])
    if metadata.has_key('title'):
        tag.setTitle(metadata['title'])
    else:
        tag.setTitle('Unknown song')
    tag.update()


def main( inputFilename, outputFilename ) :

    # Upload track for analysis.
    print 'uploading audio file...'
    #track = audio.ExistingTrack(inputFilename).analysis
    track = audio.AudioFile(inputFilename).analysis
    
    # Get loudness.
    print 'getting loudness...'
    loudness = track.loudness
    # Get beats.
    print 'getting beats...'
    beats = track.beats
    # Get sections.
    print 'getting sections...'
    sections = track.sections
    # Get metadata.
    print 'getting metadata...'
    metadata = track.metadata

    # Add the sleigh bells.
    print 'jingling...'
    Jingler(inputFilename, loudness, beats, sections).run(outputFilename)            

    # Finalize output file.
    print 'finalizing output file...'
    write_tags(outputFilename, metadata)


if __name__ == '__main__':
    import sys
    try :
        inputFilename = sys.argv[-2]
        outputFilename = sys.argv[-1]
    except :
        print usage
        sys.exit(-1)
    main( inputFilename, outputFilename )
