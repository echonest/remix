# By Tristan Jehan, based on cowbell.py, itself based on previous jingler code.
# This script takes an mp3 file and produces an mp3 file dubbed with synchronized sleighbells
# and other christmassy sounds.

import echonest.audio as audio
import lame, mad, numpy, eyeD3
import os, random, time

usage = """
# For this script to work properly, you need to install the Echo Nest Remix API: 
# http://code.google.com/p/echo-nest-remix/ (where you should have found this script)
# You also need to install the lame libraries and the following python modules: 
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
    def __init__(self, audio, loudness, endOfFadeIn, beats, sections):
        # load audio, normalize it with samples
        t1 = time.time()
        mf = mad.MadFile(audio)
        # we choose int32 to cope with possible overflows after mixing
        self.audiodata = numpy.array(mf.readall(), dtype=numpy.int32)
        self.audiodata *= linear(loudness, -2, -12, 0.5, 1.5) * 0.75
        self.audiodata = self.audiodata.reshape(len(self.audiodata) / 2, 2)
        print "Loaded/Normalized audio input in %.3f secs" % (time.time() - t1)
        self.audiorate = mf.samplerate()    
        self.audiochannels = 2 # force it
        self.beats = beats
        self.sections = sections
        self.duration = len(self.audiodata) / self.audiorate
        self.endOfFadeIn = endOfFadeIn

    def run(self, out):
        # sequence and mix
        t1 = time.time()
        print "Sequencing and mixing..."
        self.sequence(sleighBellSounds)
        print "Normalizing audio output..."
        #self.limiter() # slow but can be used in place of self.normalize()
        self.normalize() # remove this line if you use self.limiter() instead
        # at this point self.audiodata is down to a int16 array
        print "Sequenced, mixed and normalized in %.3f secs" % (time.time() - t1)
        # save
        t1 = time.time()
        print "Encoding mp3..."
        self.encode(out)
        print "Encoded in %.3f secs" % (time.time() - t1)

    # simple normalization that prevents clipping. There can be a little bit of a volume drop.
    # to prevent volume drops, use self.limiter() instead, however it is slower.
    def normalize(self):
        factor = 32767.0 / numpy.max(numpy.absolute(self.audiodata.flatten()))
        if factor < 1:
            # we return to 16 bit arrays
            self.audiodata = numpy.array(self.audiodata * factor, dtype=numpy.int16)

    def sequence(self, chops):
        # adjust sounds and durations
        if self.beats[4].duration < MIN_BEAT_DURATION: stride = 2
        else: stride = 1
        if self.beats[4].duration > MAX_BEAT_DURATION: multiplier = 0.5
        else: multiplier = 1
        if self.beats[4].duration * stride * multiplier > SLEIGH_THRESHOLD: sleighBellIndex = 0
        else: sleighBellIndex = 1

        # add sleigh bells on the beats
        for i in range(0,len(self.beats),stride):
            beat = self.beats[i]
            # let's put a little bit of jitter in the volume
            vol = 0.6 + random.randint(-100,100) / 1000.0
            sample = sleighBellSounds[sleighBellIndex]
            # let's stop jingling 5 seconds before the end anyhow
            if beat.start+SLEIGH_OFFSET[sleighBellIndex]+5.0 < self.duration:
                self.mix(beat.start+SLEIGH_OFFSET[sleighBellIndex], seg=sample, volume=vol)
            if multiplier == 0.5:
                self.mix(beat.start+beat.duration/2.0+SLEIGH_OFFSET[sleighBellIndex], seg=sample, volume=vol/2.0)
                
        # add signal bells on section changes
        for section in self.sections[1:]:
            sample = signalBellSounds[random.randint(0,1)]
            self.mix(start=section.start+SIGNAL_OFFSET, seg=sample, volume=0.5)
        # add other signals in case there's some silence at the beginning
        if self.endOfFadeIn > 0.5:
            sample = signalBellSounds[2]
            self.mix(start=max(0,self.endOfFadeIn-1.0), seg=sample, volume=1.0)
        # add santa walking at the end of the track
        sample = snowSantaSounds[0]
        self.mix(start=self.duration+SANTA_OFFSET, seg=sample, volume=1.0)

    def mix(self, start=None, seg=None, volume=0.3, pan=0.):
        # this assumes that the audios have the same samplerate/numchannels
        startsample = int(start * self.audiorate)
        seg = seg[0:]
        seg.data *= (volume-(pan*volume), volume+(pan*volume)) # pan and volume
        if start > 0 and self.audiodata.shape[0] - startsample > seg.data.shape[0]:
            self.audiodata[startsample:startsample+len(seg.data)] += seg.data[0:] # mix
            #numpy.clip(self.audiodata[startsample:startsample+len(seg.data)], -32767, 32767)

    def curve_int16(self, x):
        return int(numpy.power((x-LIMITER_THRESHOLD)/3276, LIMITER_COEFF) * 3276 + LIMITER_THRESHOLD)
        #return numpy.power((x-LIMITER_THRESHOLD)/(32767-LIMITER_THRESHOLD), LIMITER_COEFF) * (32767-LIMITER_THRESHOLD) + LIMITER_THRESHOLD)

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

    # simple attempt at compressing and limiting the mixed signal to avoid clipping
    # this is a bit slower than I would like (roughly 10 secs) but it works fine
    def limiter(self):
        vec_limiter = numpy.vectorize(self.limit_int16, otypes=[numpy.int16])
        self.audiodata = vec_limiter(self.audiodata)

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
    t1 = time.time()
    print 'uploading audio file...'
    #track = audio.ExistingTrack(inputFilename).analysis # This is useful once you've uploaded a track once and it's been registered
    track = audio.LocalAnalysis(inputFilename).analysis
    print "Uploaded in %.3f secs" % (time.time() - t1)

    # Get loudness.
    print 'getting loudness...'
    loudness = track.loudness
    print 'getting start of fade in...'
    endOfFadeIn = track.end_of_fade_in
    # Get beats.
    print 'getting beats...'
    beats = track.beats
    # Check that there are beats in the song
    if len(beats) < 5: 
        print 'not enough beats in this song...'
        sys.exit(-2)
    # Get sections.
    print 'getting sections...'
    sections = track.sections
    # Get metadata.
    print 'getting metadata...'
    metadata = track.metadata

    # Add the sleigh bells.
    print 'jingling...'
    Jingler(inputFilename, loudness, endOfFadeIn, beats, sections).run(outputFilename)            

    # Finalize output file.
    print 'finalizing output file...'
    write_tags(outputFilename, metadata)
    print 'Done.'


if __name__ == '__main__':
    import sys
    try :
        inputFilename = sys.argv[-2]
        outputFilename = sys.argv[-1]
    except :
        print usage
        sys.exit(-1)
    main( inputFilename, outputFilename )
