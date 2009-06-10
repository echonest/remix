# By Rob Ochshorn and Adam Baratz.
# Slightly refactored by Joshua Lifton.
import numpy
import os
import random
import time

import echonest.audio as audio

usage = """
Usage: 
    python cowbell.py <inputFilename> <outputFilename> <cowbellIntensity> <walkenIntensity>

Example:
    python cowbell.py YouCanCallMeAl.mp3 YouCanCallMeCow.mp3 0.2 0.5

Reference:
    http://www.youtube.com/watch?v=ZhSkRHXTKlw
"""

# constants
COWBELL_THRESHOLD = 0.85
COWBELL_OFFSET = -0.005

# samples
soundsPath = "sounds/"

cowbellSounds = map(lambda x: audio.AudioData(os.path.join(soundsPath, "cowbell%s.wav" % x), sampleRate=44100, numChannels=2), range(5))
walkenSounds = map(lambda x: audio.AudioData(os.path.join(soundsPath, "walken%s.wav" % x), sampleRate=44100, numChannels=2), range(16))
trill = audio.AudioData(os.path.join(soundsPath, "trill.wav"), sampleRate=44100, numChannels=2)

def linear(input, in1, in2, out1, out2):
    return ((input-in1) / (in2-in1)) * (out2-out1) + out1

def exp(input, in1, in2, out1, out2, coeff):
    if (input <= in1):
        return out1
    if (input >= in2):
        return out2
    return pow( ((input-in1) / (in2-in1)) , coeff ) * (out2-out1) + out1

class Cowbell:
    def __init__(self, input_file):
        self.audiofile = audio.LocalAudioFile(input_file)
        self.audiofile.data *= linear(self.audiofile.analysis.loudness, -2, -12, 0.5, 1.5) * 0.75

    def run(self, cowbell_intensity, walken_intensity, out):
        if cowbell_intensity != -1:
            self.cowbell_intensity = cowbell_intensity
            self.walken_intensity = walken_intensity
        t1 = time.time()
        sequence = self.sequence(cowbellSounds)
        print "Sequence and mixed in %g seconds" % (time.time() - t1)
        self.audiofile.encode(out)

    def sequence(self, chops):
        # add cowbells on the beats
        for beat in self.audiofile.analysis.beats:
            volume = linear(self.cowbell_intensity, 0, 1, 0.1, 0.3)
            # mix in cowbell on beat
            if self.cowbell_intensity == 1:
                self.mix(beat.start+COWBELL_OFFSET, seg=cowbellSounds[random.randint(0,1)], volume=volume)
            else:
                self.mix(beat.start+COWBELL_OFFSET, seg=cowbellSounds[random.randint(2,4)], volume=volume)
            # divide beat into quarters
            quarters = (numpy.arange(1,4) * beat.duration) / 4. + beat.start
            # mix in cowbell on quarters
            for quarter in quarters:
                volume = exp(random.random(), 0.5, 0.1, 0, self.cowbell_intensity, 0.8) * 0.3
                pan = linear(random.random(), 0, 1, -self.cowbell_intensity, self.cowbell_intensity)
                if self.cowbell_intensity < COWBELL_THRESHOLD:
                    self.mix(quarter+COWBELL_OFFSET, seg=cowbellSounds[2], volume=volume)
                else:
                    randomCowbell = linear(random.random(), 0, 1, COWBELL_THRESHOLD, 1)
                    if randomCowbell < self.cowbell_intensity:
                        self.mix(start=quarter+COWBELL_OFFSET, seg=cowbellSounds[random.randint(0,1)], volume=volume)
                    else:
                        self.mix(start=quarter+COWBELL_OFFSET, seg=cowbellSounds[random.randint(2,4)], volume=volume)
        # add trills / walken on section changes
        for section in self.audiofile.analysis.sections[1:]:
            if random.random() > self.walken_intensity:
                sample = trill
                volume = 0.3
            else:
                sample = walkenSounds[random.randint(0, len(walkenSounds)-1)]
                volume = 1.5
            self.mix(start=section.start+COWBELL_OFFSET, seg=sample, volume=volume)

    def mix(self, start=None, seg=None, volume=0.3, pan=0.):
        # this assumes that the audios have the same frequency/numchannels
        startsample = int(start * self.audiofile.sampleRate)
        seg = seg[0:]
        seg.data *= (volume-(pan*volume), volume+(pan*volume)) # pan + volume
        if self.audiofile.data.shape[0] - startsample > seg.data.shape[0]:
            self.audiofile.data[startsample:startsample+len(seg.data)] += seg.data[0:]


def main(inputFilename, outputFilename, cowbellIntensity, walkenIntensity ) :
    c = Cowbell(inputFilename)
    print 'cowbelling...'
    c.run(cowbellIntensity, walkenIntensity, outputFilename)

if __name__ == '__main__':
    import sys
    try :
        inputFilename = sys.argv[1]
        outputFilename = sys.argv[2]
        cowbellIntensity = float(sys.argv[3])
        walkenIntensity = float(sys.argv[4])
    except :
        print usage
        sys.exit(-1)
    main(inputFilename, outputFilename, cowbellIntensity, walkenIntensity)
