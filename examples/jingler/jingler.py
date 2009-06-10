# By Tristan Jehan, based on cowbell.py, itself based on previous jingler code.
# This script takes an mp3 file and produces an mp3 file dubbed with synchronized sleighbells
# and other christmassy sounds.
import numpy
import os
import random
import time

import echonest.audio as audio

usage = """
Usage: 
    python jingler.py <inputFilename> <outputFilename>
Example:
    python jingler.py aha.mp3 aha_Jingled.mp3
Reference:
    http://www.thejingler.com
"""

# constants
SLEIGH_OFFSET = [-0.2, -0.075] # seconds
SIGNAL_OFFSET = -1.0 # seconds
SANTA_OFFSET = -6.25 # seconds
SLEIGH_THRESHOLD = 0.420 # seconds
MIN_BEAT_DURATION = 0.280 # seconds
MAX_BEAT_DURATION = 0.560 # seconds
LIMITER_THRESHOLD = 29491 # 90% of the dynamic range
LIMITER_COEFF = 0.2 # compresion curve

# samples
soundsPath = "sounds/"

snowSantaSounds  = map(lambda x: audio.AudioData(os.path.join(soundsPath, "snowSanta%s.wav" % x), sampleRate=44100, numChannels=2), range(1))
sleighBellSounds = map(lambda x: audio.AudioData(os.path.join(soundsPath, "sleighBell%s.wav" % x), sampleRate=44100, numChannels=2), range(2))
signalBellSounds = map(lambda x: audio.AudioData(os.path.join(soundsPath, "signalBell%s.wav" % x), sampleRate=44100, numChannels=2), range(3))

# some math useful for normalization
def linear(input, in1, in2, out1, out2):
    return ((input-in1) / (in2-in1)) * (out2-out1) + out1

class Jingler:
    def __init__(self, input_file):
        self.audiofile = audio.LocalAudioFile(input_file)
        self.audiofile.data *= linear(self.audiofile.analysis.loudness, 
                                        -2, -12, 0.5, 1.5) * 0.75
        # Check that there are beats in the song
        if len(self.audiofile.analysis.beats) < 5: 
            print 'not enough beats in this song...'
            sys.exit(-2)
        self.duration = len(self.audiofile.data) / self.audiofile.sampleRate

    def run(self, out):
        # sequence and mix
        t1 = time.time()
        print "Sequencing and mixing..."
        self.sequence(sleighBellSounds)
        print "Normalizing audio output..."
        #self.limiter() # slow but can be used in place of self.normalize()
        self.normalize() # remove this line if you use self.limiter() instead
        # at this point self.audiofile.data is down to a int16 array
        print "Sequenced, mixed and normalized in %.3f secs" % (time.time() - t1)
        # save
        t1 = time.time()
        print "Encoding mp3..."
        self.audiofile.encode(out)
        print "Encoded in %.3f secs" % (time.time() - t1)

    def normalize(self):
        # simple normalization that prevents clipping. There can be a little bit of a volume drop.
        # to prevent volume drops, use self.limiter() instead, however it is slower.
        factor = 32767.0 / numpy.max(numpy.absolute(self.audiofile.data.flatten()))
        if factor < 1:
            # we return to 16 bit arrays
            self.audiofile.data = numpy.array(self.audiofile.data * factor, dtype=numpy.int16)

    def sequence(self, chops):
        # adjust sounds and durations
        if self.audiofile.analysis.beats[4].duration < MIN_BEAT_DURATION:
            stride = 2
        else:
            stride = 1
        if self.audiofile.analysis.beats[4].duration > MAX_BEAT_DURATION:
            multiplier = 0.5
        else:
            multiplier = 1
        if self.audiofile.analysis.beats[4].duration * stride * multiplier > SLEIGH_THRESHOLD:
            sleighBellIndex = 0
        else:
            sleighBellIndex = 1
        # add sleigh bells on the beats
        for i in range(0,len(self.audiofile.analysis.beats),stride):
            beat = self.audiofile.analysis.beats[i]
            # let's put a little bit of jitter in the volume
            vol = 0.6 + random.randint(-100, 100) / 1000.0
            sample = sleighBellSounds[sleighBellIndex]
            # let's stop jingling 5 seconds before the end anyhow
            if beat.start + SLEIGH_OFFSET[sleighBellIndex] + 5.0 < self.duration:
                self.mix(beat.start + SLEIGH_OFFSET[sleighBellIndex], seg=sample, volume=vol)
            if multiplier == 0.5:
                self.mix(beat.start + beat.duration/2.0 + SLEIGH_OFFSET[sleighBellIndex], seg=sample, volume=vol/2.0)
        # add signal bells on section changes
        for section in self.audiofile.analysis.sections[1:]:
            sample = signalBellSounds[random.randint(0,1)]
            self.mix(start=section.start+SIGNAL_OFFSET, seg=sample, volume=0.5)
        # add other signals in case there's some silence at the beginning
        if self.audiofile.analysis.end_of_fade_in > 0.5:
            sample = signalBellSounds[2]
            self.mix(start=max(0,self.audiofile.analysis.end_of_fade_in-1.0), seg=sample, volume=1.0)
        # add santa walking at the end of the track
        sample = snowSantaSounds[0]
        self.mix(start=self.duration+SANTA_OFFSET, seg=sample, volume=1.0)

    def mix(self, start=None, seg=None, volume=0.3, pan=0.):
        # this assumes that the audios have the same samplerate/numchannels
        startsample = int(start * self.audiofile.sampleRate)
        seg = seg[0:]
        seg.data *= (volume-(pan*volume), volume+(pan*volume)) # pan and volume
        if start > 0 and self.audiofile.data.shape[0] - startsample > seg.data.shape[0]:
            self.audiofile.data[startsample:startsample+len(seg.data)] += seg.data[0:]

    def curve_int16(self, x):
        return int(numpy.power((x-LIMITER_THRESHOLD)/3276, LIMITER_COEFF) * 3276 + LIMITER_THRESHOLD)

    def limit_int16(self, x):
        if x > LIMITER_THRESHOLD:
            tmp = self.curve_int16(x)
            if tmp > 32767: return 32767
            else: return tmp
        elif x < -LIMITER_THRESHOLD:
            value = -x
            tmp = self.curve_int16(value)
            if tmp > 32767: return -32767
            else: return -tmp
        return x

    def limiter(self):
        # simple attempt at compressing and limiting the mixed signal to avoid clipping
        # this is a bit slower than I would like (roughly 10 secs) but it works fine
        vec_limiter = numpy.vectorize(self.limit_int16, otypes=[numpy.int16])
        self.audiofile.data = vec_limiter(self.audiofile.data)


def main(inputFilename, outputFilename):
    j = Jingler(inputFilename)
    print 'jingling...'
    j.run(outputFilename)
    print 'Done.'

if __name__ == '__main__':
    import sys
    try :
        inputFilename = sys.argv[1]
        outputFilename = sys.argv[2]
    except :
        print usage
        sys.exit(-1)
    main(inputFilename, outputFilename)
