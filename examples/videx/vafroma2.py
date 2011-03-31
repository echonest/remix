#!/usr/bin/env python
# encoding: utf=8

"""
vafroma2.py

Re-synthesize video A using the segments of song A.
Same as vafroma.py, but avoids re-using segments.

By Ben Lacker, P. Lamere
"""
import numpy
import sys
import time
import echonest.audio as audio
import echonest.video as video
import echonest.modify as modify

usage="""
Usage:
    python vafroma2.py <input_filename>

Example:
    python vafroma2.py BillieJeanMusicVideo.mp4
"""


dur_weight = 1000
#dur_weight = 100
timbre_weight = .001
pitch_weight = 10
loudness_weight = 1

class AfromA(object):
    def __init__(self, input_filename, output_filename):
        self.av = video.loadav(input_filename)
        self.segs = self.av.audio.analysis.segments
        self.output_filename = output_filename

    def get_distance_from(self, seg):
        distances = []
        for a in self.segs:
            ddur = numpy.square(seg.duration - a.duration)
            dloud = numpy.square(seg.loudness_max - a.loudness_max)

            timbre_diff = numpy.subtract(seg.timbre, a.timbre)
            dtimbre = (numpy.sum(numpy.square(timbre_diff)))

            pitch_diff = numpy.subtract(seg.pitches, a.pitches)
            dpitch = (numpy.sum(numpy.square(pitch_diff)))

            #print dur_weight * ddur, timbre_weight * dtimbre, \
            #      pitch_weight * dpitch, loudness_weight * dloud
            distance =    dur_weight * ddur \
                        + loudness_weight * dloud \
                        + timbre_weight * dtimbre \
                        + pitch_weight * dpitch;
            distances.append(distance)

        return distances
            

    def run(self):
        st = modify.Modify()
        collect = audio.AudioQuantumList()
        used = []
        for a in self.segs:
            seg_index = a.absolute_context()[0]

            distances = self.get_distance_from(a)

            distances[seg_index] = sys.maxint
            for u in used:
                distances[u] = sys.maxint

            match_index = distances.index(min(distances))
            match = self.segs[match_index]
            print seg_index, match_index
            # make the length of the new seg match the length
            # of the old seg
            collect.append(match)
            used.append(match_index)
        out = video.getpieces(self.av, collect)
        out.save(self.output_filename)

def main():
    try:
        input_filename = sys.argv[1]
        if len(sys.argv) > 2:
            output_filename = sys.argv[2]
        else:
            output_filename = "aa2_" + input_filename
    except:
        print usage
        sys.exit(-1)
    AfromA(input_filename, output_filename).run()


if __name__=='__main__':
    tic = time.time()
    main()
    toc = time.time()
    print "Elapsed time: %.3f sec" % float(toc-tic)
