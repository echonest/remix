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
    python afromb.py <inputfilenameA> <inputfilenameB> <outputfilename> <Mix> [env]

Example:
    python afromb.py BillieJean.mp3 CryMeARiver.mp3 BillieJeanFromCryMeARiver.mp3 0.9 env

The 'env' flag applies the volume envelopes of the segments of A to those
from B.

Mix is a number 0-1 that determines the relative mix of the resynthesized
song and the original input A. i.e. a mix value of 0.9 yields an output that
is mostly the resynthesized version.

"""

class AfromB(object):
    def __init__(self, input_filename_a, input_filename_b, output_filename):
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
        loudmax_distances = []
        for b in self.segs_b:
            pitch_diff = numpy.subtract(b.pitches,a.pitches)
            pitch_distances.append(numpy.sum(numpy.square(pitch_diff)))
            timbre_diff = numpy.subtract(b.timbre,a.timbre)
            timbre_distances.append(numpy.sum(numpy.square(timbre_diff)))
            loudmax_diff = b.loudness_begin - a.loudness_begin
            loudmax_distances.append(numpy.square(loudmax_diff))
        distance_matrix[:,0] = pitch_distances
        distance_matrix[:,1] = timbre_distances
        distance_matrix[:,2] = loudmax_distances
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

    def run(self, mix=0.5, envelope=False):
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
        for a in self.segs_a:
            seg_index = a.absolute_context()[0]
            # find best match from segs in B
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
                new_segment.endindex = len(new_segment)
                segment_data = new_segment
            elif segment_data.endindex > reference_data.endindex:
                index = slice(0, int(reference_data.endindex), 1)
                segment_data = audio.AudioData(None,segment_data.data[index],
                                        sampleRate=segment_data.sampleRate)
            if envelope:
                # db -> voltage ratio http://www.mogami.com/e/cad/db.html
                linear_max_volume = pow(10.0,a.loudness_max/20.0)
                linear_start_volume = pow(10.0,a.loudness_begin/20.0)
                if(seg_index == len(self.segs_a)-1): # if this is the last segment
                    linear_next_start_volume = 0
                else:
                    linear_next_start_volume = pow(10.0,self.segs_a[seg_index+1].loudness_begin/20.0)
                    pass
                when_max_volume = a.time_loudness_max
                # Count # of ticks I wait doing volume ramp so I can fix up rounding errors later.
                ss = 0
                # Set volume of this segment. Start at the start volume, ramp up to the max volume , then ramp back down to the next start volume.
                cur_vol = float(linear_start_volume)
                # Do the ramp up to max from start
                samps_to_max_loudness_from_here = int(segment_data.sampleRate * when_max_volume)
                if(samps_to_max_loudness_from_here > 0):
                    how_much_volume_to_increase_per_samp = float(linear_max_volume - linear_start_volume)/float(samps_to_max_loudness_from_here)
                    for samps in xrange(samps_to_max_loudness_from_here):
                        try:
                            segment_data.data[ss] *= cur_vol
                        except IndexError:
                            pass
                        cur_vol = cur_vol + how_much_volume_to_increase_per_samp
                        ss = ss + 1
                # Now ramp down from max to start of next seg
                samps_to_next_segment_from_here = int(segment_data.sampleRate * (a.duration-when_max_volume))
                if(samps_to_next_segment_from_here > 0):
                    how_much_volume_to_decrease_per_samp = float(linear_max_volume - linear_next_start_volume)/float(samps_to_next_segment_from_here)
                    for samps in xrange(samps_to_next_segment_from_here):
                        cur_vol = cur_vol - how_much_volume_to_decrease_per_samp
                        try:
                            segment_data.data[ss] *= cur_vol
                        except IndexError:
                            pass
                        ss = ss + 1
            mixed_data = audio.mix(segment_data,reference_data,mix=mix)
            out.append(mixed_data)
        out.encode(self.output_filename)

def main():
    try:
        input_filename_a = sys.argv[1]
        input_filename_b = sys.argv[2]
        output_filename = sys.argv[3]
        mix = sys.argv[4]
        if len(sys.argv) == 6:
            env = True
        else:
            env = False
    except:
        print usage
        sys.exit(-1)
    AfromB(input_filename_a, input_filename_b, output_filename).run(mix=mix,
                                                                envelope=env)

if __name__=='__main__':
    tic = time.time()
    main()
    toc = time.time()
    print "Elapsed time: %.3f sec" % float(toc-tic)
