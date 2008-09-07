import Audio, lame, mad, os, numpy, random, tempfile, time

# constants
COWBELL_THRESHOLD = 0.85
COWBELL_OFFSET = -0.005

# samples
soundsPath = "sounds/"

cowbellSounds = map(lambda x: Audio.load(os.path.join(soundsPath, "cowbell%s.wav" % x), samples=44100, channels=2), range(5))
walkenSounds = map(lambda x: Audio.load(os.path.join(soundsPath, "walken%s.wav" % x), samples=44100, channels=2), range(16))
trill = Audio.load(os.path.join(soundsPath, "trill.wav"), samples=44100, channels=2)

class Cowbell:
    def __init__(self, audio, beats, sections):
        mf = mad.MadFile(audio)
        self.audiodata = numpy.array(mf.readall(), dtype=numpy.int16)
        
        # normalize audio (to avoid clipping) while array is at its simplest
        t1 = time.time()
        self.audiodata *= 0.5
        print "NORMALIZED AUDIO IN %g SECONDS" % (time.time() - t1)
        
        # data needs to be in stereo, so fake it for mono MP3s
        if mf.mode() == 0:
            self.audiodata = numpy.repeat(self.audiodata, 2)
        self.audiodata = self.audiodata.reshape(len(self.audiodata) / 2, 2)
        
        self.audiorate = mf.samplerate()    
        self.audiochannels = 2
        
        self.beats = beats
        self.sections = sections
    
    def run(self, cowbell_intensity, walken_intensity, out=None):
        if cowbell_intensity != -1:
            self.cowbell_intensity = cowbell_intensity
            self.walken_intensity = walken_intensity
        
        # sequence and mix
        t1 = time.time()
        sequence = self.sequence(cowbellSounds)
        print "SEQUENCED AND MIXED IN %g SECONDS" % (time.time() - t1)
        
        # save
        t1 = time.time()
        path = self.encode(out)
        print "ENCODED IN %g SECONDS" % (time.time() - t1)
        
        return path

    def sequence(self, chops):
        # define mappings
        def linear(input, in1, in2, out1, out2):
            return ((input-in1) / (in2-in1)) * (out2-out1) + out1

        def exp(input, in1, in2, out1, out2, coeff):
            if (input <= in1):
                return out1
            if (input >= in2):
                return out2
            return pow( ((input-in1) / (in2-in1)) , coeff ) * (out2-out1) + out1

        # add cowbells on the beats
        for beat in self.beats:
            volume = linear(self.cowbell_intensity, 0, 1, 0.1, 0.3)

            # mix in cowbell on beat
            if self.cowbell_intensity == 1:
                self.mix(beat['start']+COWBELL_OFFSET, seg=cowbellSounds[random.randint(0,1)], volume=volume)
            else:
                self.mix(beat['start']+COWBELL_OFFSET, seg=cowbellSounds[random.randint(2,4)], volume=volume)

            # divide beat into quarters
            quarters = (numpy.arange(1,4) * beat['duration']) / 4. + beat['start']
            
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

            self.mix(start=section+COWBELL_OFFSET, seg=sample, volume=volume)
    
    def mix(self, start=None, seg=None, volume=0.3, pan=0.):
        # this assumes that the audios have the same frequency/numchannels

        startsample = int(start * self.audiorate)
        seg = seg[0:]
        seg.data *= (volume-(pan*volume), volume+(pan*volume)) # pan + volume

        if self.audiodata.shape[0] - startsample > seg.data.shape[0]:
            self.audiodata[startsample:startsample+len(seg.data)] += seg.data[0:] # mix
    
    def encode(self, out):
        if out is None:
            handle, mp3_path = tempfile.mkstemp(".mp3")
        else:
            mp3_path = out
        
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
        
        return mp3_path
