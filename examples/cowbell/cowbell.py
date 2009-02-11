# By Rob Ochshorn and Adam Baratz.
# Slightly refactored by Joshua Lifton.

import echonest.audio as audio
import lame, mad, numpy, eyeD3
import os, random, time

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
    def __init__(self, audio, loudness, beats, sections):
        # load audio, normalize it with samples
        t1 = time.time()
        
        mf = mad.MadFile(audio)
        self.audiodata = numpy.array(mf.readall(), dtype=numpy.int16)
        self.audiodata *= linear(loudness, -2, -12, 0.5, 1.2) * 0.75
        self.audiodata = self.audiodata.reshape(len(self.audiodata) / 2, 2)
        
        print "LOADED/NORMALIZED AUDIO IN %g SECONDS" % (time.time() - t1)
        
        self.audiorate = mf.samplerate()    
        self.audiochannels = 2 # force it
        
        self.beats = beats
        self.sections = sections


    def run(self, cowbell_intensity, walken_intensity, out):
        if cowbell_intensity != -1:
            self.cowbell_intensity = cowbell_intensity
            self.walken_intensity = walken_intensity
        
        # sequence and mix
        t1 = time.time()
        
        sequence = self.sequence(cowbellSounds)
        print "SEQUENCED AND MIXED IN %g SECONDS" % (time.time() - t1)
        
        # save
        t1 = time.time()
        self.encode(out)
        print "ENCODED IN %g SECONDS" % (time.time() - t1)


    def sequence(self, chops):
        # add cowbells on the beats
        for beat in self.beats:
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
        for section in self.sections[1:]:
            if random.random() > self.walken_intensity:
                sample = trill
                volume = 0.3
            else:
                sample = walkenSounds[random.randint(0, len(walkenSounds)-1)]
                volume = 1.5

            self.mix(start=section.start+COWBELL_OFFSET, seg=sample, volume=volume)
    
    
    def mix(self, start=None, seg=None, volume=0.3, pan=0.):
        # this assumes that the audios have the same frequency/numchannels

        startsample = int(start * self.audiorate)
        seg = seg[0:]
        seg.data *= (volume-(pan*volume), volume+(pan*volume)) # pan + volume

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



def main( inputFilename, outputFilename, cowbellIntensity, walkenIntensity ) :

    # Upload track for analysis.
    print 'uploading audio file...'
    #track = audio.ExistingTrack(inputFilename).analysis
    track = audio.LocalAudioFile(inputFilename).analysis
    
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

    # Add the cowbells.
    print 'cowbelling...'
    Cowbell(inputFilename, loudness, beats, sections).run(cowbellIntensity, walkenIntensity, outputFilename)            

    # Finalize output file.
    print 'finalizing output file...'
    write_tags(outputFilename, metadata)



if __name__ == '__main__':
    import sys
    try :
        inputFilename = sys.argv[-4]
        outputFilename = sys.argv[-3]
        cowbellIntensity = float(sys.argv[-2])
        walkenIntensity = float(sys.argv[-1])
    except :
        print usage
        sys.exit(-1)
    main( inputFilename, outputFilename, cowbellIntensity, walkenIntensity )
