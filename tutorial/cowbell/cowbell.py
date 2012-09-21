# By Rob Ochshorn and Adam Baratz.
# Slightly refactored by Joshua Lifton.

# These lines import other things. 
import numpy
import os
import random
import time
# This line imports remix! 
import echonest.audio as audio

usage = """
Usage: 
    python cowbell.py <inputFilename> <outputFilename> <cowbellIntensity> <walkenIntensity>

Example:
    python cowbell.py YouCanCallMeAl.mp3 YouCanCallMeCow.mp3 0.2 0.5

Reference:
    http://www.youtube.com/watch?v=ZhSkRHXTKlw
"""

# Cowbell is pretty complex!
# Hold on, and we'll try to make everything make sense

# These are constants for how the cowbell is added
COWBELL_THRESHOLD = 0.85
COWBELL_OFFSET = -0.005

# This is the path to the samples
soundsPath = "sounds/"
# This gets the samples into remix
cowbellSounds = map(lambda x: audio.AudioData(os.path.join(soundsPath, "cowbell%s.wav" % x), sampleRate=44100, numChannels=2), range(5))
walkenSounds = map(lambda x: audio.AudioData(os.path.join(soundsPath, "walken%s.wav" % x), sampleRate=44100, numChannels=2), range(16))
trill = audio.AudioData(os.path.join(soundsPath, "trill.wav"), sampleRate=44100, numChannels=2)

    # Helper function for dealing with volume
def linear(input, in1, in2, out1, out2):
    return ((input-in1) / (in2-in1)) * (out2-out1) + out1
    # Helper function for dealing with volume
def exp(input, in1, in2, out1, out2, coeff):
    if (input <= in1):
        return out1
    if (input >= in2):
        return out2
    return pow( ((input-in1) / (in2-in1)) , coeff ) * (out2-out1) + out1

    # The main class
class Cowbell:
        # This gets the input file into remix, and scales the loudness down to avoid clipping
    def __init__(self, input_file):
        self.audiofile = audio.LocalAudioFile(input_file)
        self.audiofile.data *= linear(self.audiofile.analysis.loudness, -2, -12, 0.5, 1.5) * 0.75

        # This sets up the intensities, and then sequences the file
    def run(self, cowbell_intensity, walken_intensity, out):
        # This sets the intensities
        if cowbell_intensity != -1:
            self.cowbell_intensity = cowbell_intensity
            self.walken_intensity = walken_intensity
        t1 = time.time()
        # This calls sequence, which adds the cowbell sounds
        sequence = self.sequence(cowbellSounds)
        print "Sequence and mixed in %g seconds" % (time.time() - t1)
        # This writes the newly created audio to the given file.  
        self.audiofile.encode(out)

        # Where the magic happens:  
    def sequence(self, chops):
        # This adds cowbell to each beat
        for beat in self.audiofile.analysis.beats:
            volume = linear(self.cowbell_intensity, 0, 1, 0.1, 0.3)
            # Mix the audio
            if self.cowbell_intensity == 1:
                self.mix(beat.start+COWBELL_OFFSET, seg=cowbellSounds[random.randint(0,1)], volume=volume)
            else:
                self.mix(beat.start+COWBELL_OFFSET, seg=cowbellSounds[random.randint(2,4)], volume=volume)
            
            # This splits the beat into quarters (16th notes)
            quarters = (numpy.arange(1,4) * beat.duration) / 4. + beat.start
            # This adds occasional extra cowbell hits on the 16th notes
            for quarter in quarters:
                volume = exp(random.random(), 0.5, 0.1, 0, self.cowbell_intensity, 0.8) * 0.3
                pan = linear(random.random(), 0, 1, -self.cowbell_intensity, self.cowbell_intensity)
                # If we're over the cowbell threshold, add a cowbell
                if self.cowbell_intensity < COWBELL_THRESHOLD:
                    self.mix(quarter+COWBELL_OFFSET, seg=cowbellSounds[2], volume=volume)
                else:
                    randomCowbell = linear(random.random(), 0, 1, COWBELL_THRESHOLD, 1)
                    if randomCowbell < self.cowbell_intensity:
                        self.mix(start=quarter+COWBELL_OFFSET, seg=cowbellSounds[random.randint(0,1)], volume=volume)
                    else:
                        self.mix(start=quarter+COWBELL_OFFSET, seg=cowbellSounds[random.randint(2,4)], volume=volume)
        
        # This adds cowbell trills or Walken samples when sections change
        for section in self.audiofile.analysis.sections[1:]:
            # This chooses a cowbell trill or a Walken sample
            if random.random() > self.walken_intensity:
                sample = trill
                volume = 0.3
            else:
                sample = walkenSounds[random.randint(0, len(walkenSounds)-1)]
                volume = 1.5
            # Mix the audio
            self.mix(start=section.start+COWBELL_OFFSET, seg=sample, volume=volume)

        # This function mixes the input audio with the cowbell audio.  (audio.mix also does this!)
    def mix(self, start=None, seg=None, volume=0.3, pan=0.):
        # this assumes that the audios have the same frequency/numchannels
        startsample = int(start * self.audiofile.sampleRate)
        seg = seg[0:]
        seg.data *= (volume-(pan*volume), volume+(pan*volume)) # pan + volume
        if self.audiofile.data.shape[0] - startsample > seg.data.shape[0]:
            self.audiofile.data[startsample:startsample+len(seg.data)] += seg.data[0:]

    # Creates a 'Cowbell' object, and then runs it.
def main(inputFilename, outputFilename, cowbellIntensity, walkenIntensity ) :
    c = Cowbell(inputFilename)
    print 'cowbelling...'
    c.run(cowbellIntensity, walkenIntensity, outputFilename)

    # The wrapper for the script.  
if __name__ == '__main__':
    import sys
    try :
        # This gets the filenames to read from and write to, 
        # and sets how loud the cowbell and walken samples will be
        inputFilename = sys.argv[1]
        outputFilename = sys.argv[2]
        cowbellIntensity = float(sys.argv[3])
        walkenIntensity = float(sys.argv[4])
    except :
        # If things go wrong, exit!
        print usage
        sys.exit(-1)
    main(inputFilename, outputFilename, cowbellIntensity, walkenIntensity)

