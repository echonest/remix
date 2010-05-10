#!/usr/bin/env python

__version__ = "$Revision: 0 $"
# $Source$

from distutils.core import setup, Extension
import os, glob,sys
try:
    import numpy
except:
    sys.exit("numpy is required to use remix")

# pysoundtouch
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

is_linux = False
is_mac =False
is_windows = False
major_version_string = ".".join([str(x) for x in sys.version_info[0:2]]) # 2.6, 2.5 etc

# Is this is posix platform, or is it windows?
if hasattr(os, 'uname'):
    if(os.uname()[0] == "Darwin"):
        is_mac =True
    else:
        is_linux = True
    sources += sources_gcc
    extra_compile_args=['-fcheck-new', '-O3']
else:
    is_windows = True
    sources += sources_win
    
libSoundTouch_sources = [os.path.join('external/pysoundtouch14/libsoundtouch', i) for i in sources]

soundtouch = Extension('soundtouch', sources=['external/pysoundtouch14/soundtouchmodule.cpp',] + libSoundTouch_sources, extra_compile_args = extra_compile_args, include_dirs = [numpy.get_include(), numpy.get_numarray_include()])




all_data_files = []
if(is_mac):
    all_data_files  = [('/usr/local/bin',['external/en-ffmpeg/mac/en-ffmpeg','external/youtube-dl/youtube-dl'])]
if(is_linux):
    all_data_files  = [('/usr/local/bin',['external/youtube-dl/youtube-dl'])]
if(is_windows):
    all_data_files  = [('.',['external\\en-ffmpeg\\win\\en-ffmpeg.exe','external\\youtube-dl\\youtube-dl'])]


if(is_mac or is_linux):
    dest_prefix = 'echo-nest-remix-'
    for example_dir in glob.glob('examples/*'):
        example_files = glob.glob(example_dir+'/*')
        actual_files = []
        sub_path_tuples = []
        for example_file in example_files:
            files_within_example_file = glob.glob(example_file+'/*')
            if not any(files_within_example_file):
                actual_files.append(example_file)
            else:
                sub_path_tuples.append((dest_prefix+example_file, files_within_example_file))
        all_data_files.append((dest_prefix+example_dir, actual_files))
        if any(sub_path_tuples):
            all_data_files.extend(sub_path_tuples)

if(is_windows):
    dest_prefix = "echo-nest-remix-"
    for example_dir in glob.glob('examples\\*'):
        example_files = glob.glob(example_dir+'\\*')
        actual_files = []
        sub_path_tuples = []
        for example_file in example_files:
            files_within_example_file = glob.glob(example_file+'\\*')
            if not any(files_within_example_file):
                actual_files.append(example_file)
            else:
                sub_path_tuples.append((dest_prefix+example_file, files_within_example_file))
        all_data_files.append((dest_prefix+example_dir, actual_files))
        if any(sub_path_tuples):
            all_data_files.extend(sub_path_tuples)
    

setup(name='The Echo Nest Remix API',
      ext_modules = [soundtouch],
      version='1.2',
      description='Make things with music.',
      author='Ben Lacker',
      author_email='blacker@echonest.com',
      maintainer='Brian Whitman',
      maintainer_email='brian@echonest.com',
      url='http://developer.echonest.com/',
      download_url='http://code.google.com/p/echo-nest-remix',
      data_files= all_data_files,
      package_dir={'echonest':'src/echonest', 'pyechonest':'src/pyechonest'},
      packages=['echonest', 'echonest.support', 'echonest.support.midi', 'pyechonest'],
      requires=['os',
                'urllib',
                'httplib',
                'mimetypes',
                'tempfile',
                'commands',
                'struct',
                'wave',
                'numpy',
                'Numeric'
                ]
     )
