#!/usr/bin/env python
# encoding: utf-8
"""
modify.py

Created by Ben Lacker on 2009-06-12.
"""
from echonest.audio import *
import numpy
import soundtouch

class Modify(soundtouch.SoundTouch):
    def __init__(self, sampleRate=44100, numChannels=1, blockSize = 10000):
        self.setSampleRate(sampleRate)
        self.setChannels(numChannels)
        self.sampleRate = sampleRate
        self.numChannels = numChannels
        self.blockSize = blockSize

    def doInBlocks(self, f, in_data, arg):
        # For now, make everything mono. We'll deal with channels later
        if in_data.ndim > 1:
            in_data = in_data[:, 0]
        collect = []
        if len(in_data) > self.blockSize:
            for x in range(len(in_data)/self.blockSize):
                start = x * self.blockSize
                data = in_data[start:start + self.blockSize -1]
                collect.append(self.processAudio(f, data, arg))
            data = in_data[-1*(len(in_data) % self.blockSize):]
            collect.append(self.processAudio(f, data, arg))
        else:
            collect.append(self.processAudio(f, in_data, arg))
        return assemble(collect, numChannels=self.numChannels, sampleRate=self.sampleRate)

    def processAudio(self, f, data, arg):
        f(arg)
        self.putSamples(data)
        out_data = numpy.array(numpy.zeros((len(data)*2,), dtype=numpy.float32))
        out_samples = self.receiveSamples(out_data)
        new_ad = AudioData(ndarray=out_data[:out_samples], shape=(out_samples, ), 
                    sampleRate=self.sampleRate, numChannels=self.numChannels)
        return new_ad

    def shiftRate(self, audio_data, ratio=1):
        if not isinstance(audio_data, AudioData):
            raise TypeError('First argument must be an AudioData object.')
        if not (isinstance(ratio, int) or isinstance(ratio, float)):
            raise ValueError('Ratio must be an int or float.')
        if (ratio < 0) or (ratio > 10):
            raise ValueError('Ratio must be between 0 and 10.')
        return self.doInBlocks(self.setRate, audio_data.data, ratio)

    def shiftTempo(self, audio_data, ratio):
        if not isinstance(audio_data, AudioData):
            raise TypeError('First argument must be an AudioData object.')
        if not (isinstance(ratio, int) or isinstance(ratio, float)):
            raise ValueError('Ratio must be an int or float.')
        if (ratio < 0) or (ratio > 10):
            raise ValueError('Ratio must be between 0 and 10.')
        return self.doInBlocks(self.setTempo, audio_data.data, ratio)

    def shiftRateChange(self, audio_data, percent):
        if not isinstance(audio_data, AudioData):
            raise TypeError('First argument must be an AudioData object.')
        if not (isinstance(percent, int) or isinstance(percent, float)):
            raise ValueError('Percent must be an int or float.')
        if (percent < -50) or (percent > 100):
            raise ValueError('Percent must be between -50 and 100.')
        return self.doInBlocks(self.setRateChange, audio_data.data, percent)

    def shiftTempoChange(self, audio_data, percent):
        if not isinstance(audio_data, AudioData):
            raise TypeError('First argument must be an AudioData object.')
        if not (isinstance(percent, int) or isinstance(percent, float)):
            raise ValueError('Percent must be an int or float.')
        if (percent < -50) or (percent > 100):
            raise ValueError('Percent must be between -50 and 100.')
        return self.doInBlocks(self.setTempoChange, audio_data.data, percent)

    def shiftPitchSemiTones(self, audio_data, semitones=0):
        if not isinstance(audio_data, AudioData):
            raise TypeError('First argument must be an AudioData object.')
        if not isinstance(semitones, int):
            raise TypeError('Second argument must be an integer.')
        # I think this is right, but maybe it has to be between -12 and 12?
        if abs(semitones) > 60:
            raise ValueError('Semitones argument must be an int between -60 and 60.')
        return self.doInBlocks(self.setPitchSemiTones, audio_data.data, semitones)

    def shiftPitchOctaves(self, audio_data, octaves=0):
        if not isinstance(audio_data, AudioData):
            raise TypeError('First argument must be an AudioData object.')
        if not (isinstance(octaves, int) or isinstance(octaves, float)):
            raise ValueError('Octaves must be an int or float.')
        if abs(octaves) > 5:
            raise ValueError('Octaves argument must be between -5 and 5.')
        # what are the limits? Nothing in soundtouch documentation...
        return self.doInBlocks(self.setPitchOctaves, audio_data.data, octaves)
    
    def shiftPitch(self, audio_data, ratio=1):
        if not isinstance(audio_data, AudioData):
            raise TypeError('First argument must be an AudioData object.')
        if not (isinstance(ratio, int) or isinstance(ratio, float)):
            raise ValueError('Ratio must be an int or float.')
        if (ratio < 0) or (ratio > 10):
            raise ValueError('Ratio must be between 0 and 10.')
        return self.doInBlocks(self.setPitch, audio_data.data, ratio)

