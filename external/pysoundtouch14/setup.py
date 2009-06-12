#!/bin/env python
# LGPL via Soundtouch (LGPL)
# Based on http://trac2.assembla.com/pkaudio/wiki/pysoundtouch 
# but updated for soundtouch 1.4, python 2.5/2.6, numpy by blacker@echonest.com, brian@echonest.com 6/2009

import os
from distutils.core import setup, Extension

sources = ['AAFilter.cpp',
           'FIFOSampleBuffer.cpp',
           'FIRFilter.cpp',
           'RateTransposer.cpp',
           'SoundTouch.cpp',
           'TDStretch.cpp',
           'BPMDetect.cpp',
           'PeakFinder.cpp',
           'mmx_optimized.cpp',
           'sse_optimized.cpp'
           ]

sources_gcc = ['cpu_detect_x86_gcc.cpp',
               ]

sources_win = ['cpu_detect_x86_win.cpp',
               '3dnow_win.cpp',
               ]

extra_compile_args = []
# Is this is posix platform, or is it windows?
if hasattr(os, 'uname'):
    sources += sources_gcc
    extra_compile_args=['-fcheck-new', '-O3', 
                        '-I', '/System/Library/Frameworks/Python.framework/Versions/2.5/Extras/lib/python/numpy/core/include',    # mac
                        '-I', '/System/Library/Frameworks/Python.framework/Versions/2.5/Extras/lib/python/numpy/numarray',        # mac
			            '-I', '/usr/lib/python2.5/site-packages/numpy/numarray/numpy']                                            # lin
else:
    sources += sources_win
    extra_compile_args=['-IC:\Python26\Lib\site-packages\\numpy\\numarray','-IC:\Python26\Lib\site-packages\\numpy\core\include'] # win
    
libSoundTouch_sources = [os.path.join('libsoundtouch', i) for i in sources]

soundtouch = Extension('soundtouch', sources=['soundtouchmodule.cpp',] + libSoundTouch_sources, extra_compile_args = extra_compile_args)

setup(name = 'soundtouch',
      version = '0.2',
      description = 'Python libSoundTouch interface',
      author = 'Patrick Kidd Stinson, Brian Whitman, Ben Lacker',
      author_email = 'brian@echonest.com',
      url='http://code.echonest.com/p/echo-nest-remix',
      ext_modules = [soundtouch])

