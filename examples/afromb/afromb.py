#!/usr/bin/env python
# encoding: utf=8

"""
afromb.py

Re-synthesize song A using the segments of song B.

By Ben Lacker, 2009-02-24.
"""
import numpy
import sys
import time
import echonest.audio as audio

usage="""
Usage:
    python afromb.py <inputfilenameA> <inputfilenameB> <outputfilename>

Example:
    python afromb.py BillieJean.mp3 CryMeARiver.mp3 BillieJeanFromCryMeARiver.mp3

"""

class AfromB(object):
    def __init__(self,input_filename_a,input_filename_b,output_filename):
        self.input_a = audio.LocalAudioFile(input_filename_a)
        self.input_b = audio.LocalAudioFile(input_filename_b)
        self.segs_a = self.input_a.analysis.segments
        self.segs_b = self.input_b.analysis.segments
        self.output_filename = output_filename

    def calculate_distances(self, a):
        distance_matrix = numpy.zeros((len(self.segs_b), 4),
                                        dtype=numpy.float32)
        pitch_distances = []
        timbre_distances = []
        loudness_distances = []
        for b in self.segs_b:
            pitch_diff = numpy.subtract(b.pitches,a.pitches)
            pitch_distances.append(numpy.sum(numpy.square(pitch_diff)))
            timbre_diff = numpy.subtract(b.timbre,a.timbre)
            timbre_distances.append(numpy.sum(numpy.square(timbre_diff)))
            loudness_diff = b.loudness_max - a.loudness_max
            loudness_distances.append(numpy.square(loudness_diff))
        distance_matrix[:,0] = pitch_distances
        distance_matrix[:,1] = timbre_distances
        distance_matrix[:,2] = loudness_distances
        distance_matrix[:,3] = range(len(self.segs_b))
        distance_matrix = self.normalize_distance_matrix(distance_matrix)
        return distance_matrix

    def normalize_distance_matrix(self, mat, mode='minmed'):
        """ Normalize a distance matrix on a per column basis.
        """
        if mode == 'minstd':
            mini = numpy.min(mat,0)
            m = numpy.subtract(mat, mini)
            std = numpy.std(mat,0)
            m = numpy.divide(m, std)
            m = numpy.divide(m, mat.shape[1])
        elif mode == 'minmed':
            mini = numpy.min(mat,0)
            m = numpy.subtract(mat, mini)
            med = numpy.median(m)
            m = numpy.divide(m, med)
            m = numpy.divide(m, mat.shape[1])
        elif mode == 'std':
            std = numpy.std(mat,0)
            m = numpy.divide(mat, std)
            m = numpy.divide(m, mat.shape[1])
        return m

    def run(self):
        dur = len(self.input_a.data) + 100000 # another two seconds
        # determine shape of new array
        if len(self.input_a.data.shape) > 1:
            new_shape = (dur, self.input_a.data.shape[1])
            new_channels = self.input_a.data.shape[1]
        else:
            new_shape = (dur,)
            new_channels = 1
        out = audio.AudioData(shape=new_shape,
                            sampleRate=self.input_b.sampleRate,
                            numChannels=new_channels)
        # find best match for each segment
        for a in self.segs_a:
            distance_matrix = self.calculate_distances(a)
            distances = [numpy.sqrt(x[0]+x[1]+x[2]) for x in distance_matrix]
            match = self.segs_b[distances.index(min(distances))]
            segment_data = self.input_b[match]
            reference_data = self.input_a[a]
            if segment_data.endindex < reference_data.endindex:
                if new_channels > 1:
                    silence_shape = (reference_data.endindex,new_channels)
                else:
                    silence_shape = (reference_data.endindex,)
                new_segment = audio.AudioData(shape=silence_shape,
                                        sampleRate=out.sampleRate,
                                        numChannels=segment_data.numChannels)
                new_segment.append(segment_data)
                segment_data = new_segment
            elif segment_data.endindex > reference_data.endindex:
                index = slice(0, int(reference_data.endindex), 1)
                segment_data = audio.AudioData(None,segment_data.data[index],
                                        sampleRate=segment_data.sampleRate)
            out.append(segment_data)
        out.encode(self.output_filename)

def main():
    try:
        input_filename_a = sys.argv[-3]
        input_filename_b = sys.argv[-2]
        output_filename = sys.argv[-1]
    except:
        print usage
        sys.exit(-1)
    AfromB(input_filename_a,input_filename_b,output_filename).run()

if __name__=='__main__':
    main()
        