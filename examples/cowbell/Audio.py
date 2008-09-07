#!/usr/bin/env python
# encoding: utf=8
"""
Audio.py

Framework that turns audio into silly putty.

Created by Robert Ochshorn on 2008-6-06.
"""

import numpy, os, tempfile, commands, Numeric, struct, wave

class AudioSegment():

    def __init__(self, ndarray=None, shape=None,samplerate=44100,numchannels=2):
        self.samplerate = samplerate
        self.numchannels = numchannels
        
        if shape is None and isinstance(ndarray, numpy.ndarray):
            self.data = numpy.zeros(ndarray.shape, dtype=numpy.int16)
        elif shape is not None:
            self.data = numpy.zeros(shape, dtype=numpy.int16)
        else:
            self.data = None
        self.endindex = 0
        if ndarray is not None:
            self.endindex = len(ndarray)
            self.data[0:self.endindex] = ndarray

    def __getitem__(self, index):
        "returns individual frame or the entire slice as an AudioSegment"
        index = self.indexvoodo(index)
        if isinstance(index, slice):
            return self.getslice(index)
        else:
            return self.getsample(index)

    def getslice(self, index):
        if isinstance(index.start, float):
            index = slice(int(index.start*self.samplerate), int(index.stop*self.samplerate), index.step)
        return AudioSegment(self.data[index],samplerate=self.samplerate)

    def getsample(self, index):
        if isinstance(index, int):
            return self.data[index]
        else:
            #let the numpy array interface be clever
            return AudioSegment(self.data[index])

    def indexvoodo(self, index):
        "converts index to sample from a variety of forms"
        if isinstance(index, float):
            return int(index*self.samplerate) #todo: SETTINGS
        return self._indexvoodoo(index)

    def _indexvoodoo(self, index):
        return index

    def __add__(self, as2):
        if self.data is None:
            return AudioSegment(as2.data.copy())
        elif as2.data is None:
            return AudioSegment(self.data.copy())
        else:
            return AudioSegment(numpy.concatenate((self.data,as2.data)))

    def append(self, as2):
        "add as2 at the endpos of this AudioSegment"
        self.data[self.endindex:self.endindex+len(as2)] = as2.data[0:]
        self.endindex += len(as2)

    def __len__(self):
        if self.data is not None:
            return len(self.data)
        else:
            return 0

    def save(self, filename=None):
        "save sound to a wave file"

        if filename is None:
            foo,filename = tempfile.mkstemp(".wav")

        ###BASED ON SCIPY SVN (http://projects.scipy.org/pipermail/scipy-svn/2007-August/001189.html)###
        fid = open(filename, 'wb')
        fid.write('RIFF')
        fid.write('\x00\x00\x00\x00')
        fid.write('WAVE')
        # fmt chunk
        fid.write('fmt ')
        if self.data.ndim == 1:
            noc = 1
        else:
            noc = self.data.shape[1]
        bits = self.data.dtype.itemsize * 8
        sbytes = self.samplerate*(bits / 8)*noc
        ba = noc * (bits / 8)
        fid.write(struct.pack('lhHLLHH', 16, 1, noc, self.samplerate, sbytes, ba, bits))
        # data chunk
        fid.write('data')
        fid.write(struct.pack('l', self.data.nbytes))
        self.data.tofile(fid)
        # Determine file size and place it in correct
        #  position at start of the file. 
        size = fid.tell()
        fid.seek(4)
        fid.write(struct.pack('l', size-8))
        fid.close()

        return filename

def load(file, datatype=numpy.int16, samples=None, channels=None):
    "make AudioSegment from file"
    if samples is None or channels is None:
        #force samplerate and num channels to 44100 hz, 2
        samples, channels = 44100, 2
        foo, dest = tempfile.mkstemp(".wav")
        cmd = "ffmpeg -y -i \""+file+"\" -ar "+str(samples)+" -ac "+str(channels)+" "+dest
        print cmd
        parsestring = commands.getstatusoutput(cmd)
        parsestring = commands.getstatusoutput("ffmpeg -i "+dest)
        samples, channels = audiosettingsfromffmpeg(parsestring[1])
        file = dest

    w = wave.open(file, 'r')
    raw = w.readframes(w.getnframes())
    
    sampleSize = w.getnframes()*channels
    data = Numeric.array(map(int,struct.unpack("%sh" %sampleSize,raw)),Numeric.Int16)

    numpyarr = numpy.array(data, dtype=numpy.int16)
    #reshape if stereo
    if channels == 2:
        numpyarr = numpy.reshape(numpyarr, (w.getnframes(), 2))
    
    return AudioSegment(numpyarr,samplerate=samples,numchannels=channels)

def audiosettingsfromffmpeg(parsestring):
    parse = parsestring.split('\n')
    freq, chans = 44100, 2
    for line in parse:
        if "Stream #0" in line and "Audio" in line:
            segs = line.split(", ")
            for s in segs:
                if "Hz" in s:
                    print "FOUND: "+str(s.split(" ")[0])
                    freq = int(s.split(" ")[0])
                elif "stereo" in s:
                    print "STEREO"
                    chans = 2
                elif "mono" in s:
                    print "MONO"
                    chans = 1

    return freq, chans



class LazyAudioFile(AudioSegment):
    "lazy extension of AudioSegment that gets segments from a wavefile as needed"

    def __init__(self, file, samplerate=44100, numchannels=2):
        self.samplerate = samplerate
        self.numchannels = numchannels
        self.file = wave.open(file, 'r')

    def __len__(self):
        return self.file.getnframes()
    
    def getsample(self, index):
        return self.getslice(slice(index, index+1))[0]

    def getslice(self, index):
        print index.start, index.stop
        self.file.setpos(index.start)
        samplesize = (index.stop-index.start)
        raw = self.file.readframes(samplesize)
        samplesize*=self.numchannels
        data = Numeric.array(map(int,struct.unpack("%sh" %samplesize,raw)),Numeric.Int16)
        numpyarr = numpy.array(data, dtype=numpy.int16)
        #reshape if stereo
        if self.numchannels == 2:
            numpyarr = numpy.reshape(numpyarr, (samplesize/2, 2))
        return AudioSegment(numpyarr,samplerate=self.samplerate,numchannels=self.numchannels)
