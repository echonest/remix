#!/usr/bin/env python

__version__ = "$Revision: 0 $"
# $Source$

from distutils.core import setup, Extension
import os, glob
import numpy

def get_os():
    """returns is_linux, is_mac, is_windows"""
    if hasattr(os, 'uname'):
        if os.uname()[0] == "Darwin":
            return False, True, False
        return True, False, False
    return False, False, True
    
is_linux, is_mac, is_windows = get_os()

def get_action():
    cAction = os.path.join('external', 'cAction')   
    return Extension("cAction",
                        sources = [os.path.join(cAction, 'actionmodule.cpp')],
                        extra_compile_args = ['-Wno-unused'],
                        include_dirs = [numpy.get_include(), numpy.get_numarray_include()],
                     )
    
def get_dirac():
    link_args = ['-framework', 'Carbon'] if is_mac else []
    
    pydirac = os.path.join('external', 'pydirac225')
    lib_sources = [os.path.join(pydirac,'diracmodule.cpp'), os.path.join(pydirac, 'source', 'Dirac_LE.cpp')]
    
    platform = os.uname()[0] if hasattr(os, 'uname') else 'Windows'
    libname = 'Dirac64' if platform == 'Linux' and os.uname()[-1] == 'x86_64' else 'Dirac'
    return Extension(   'dirac',
                        sources = lib_sources,
                        extra_compile_args = ['-Wno-unused'],
                        include_dirs = ['source', numpy.get_include(), numpy.get_numarray_include()],
                        libraries = [libname],
                        library_dirs = [os.path.join(pydirac, 'libs', platform)],
                        extra_link_args = link_args,
                     )

def get_soundtouch():
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
    
    extra_compile_args = []
    
    if is_linux or is_mac:
        sources += ['cpu_detect_x86_gcc.cpp']
        extra_compile_args=['-fcheck-new', '-O3', '-Wno-unused']
    else:
        sources += ['cpu_detect_x86_win.cpp', '3dnow_win.cpp']
    pysoundtouch = os.path.join('external','pysoundtouch14','libsoundtouch')
    lib_sources = [os.path.join(pysoundtouch, i) for i in sources]
    lib_sources += [os.path.join('external','pysoundtouch14','soundtouchmodule.cpp')]
    return Extension(   'soundtouch', 
                        sources = lib_sources,
                        extra_compile_args = extra_compile_args, 
                        include_dirs = [numpy.get_include(), numpy.get_numarray_include()]
                    )

all_data_files = []
if is_mac:
    all_data_files  = [('/usr/local/bin',['external/en-ffmpeg/mac/en-ffmpeg','external/youtube-dl/youtube-dl'])]
if is_linux:
    all_data_files  = [('/usr/local/bin',['external/youtube-dl/youtube-dl'])]
if is_windows:
    all_data_files  = [('.',['external\\en-ffmpeg\\win\\en-ffmpeg.exe',
                             'external\\youtube-dl\\youtube-dl',
                             'external\\pydirac225\\libs\\Windows\\DiracLE.dll'])]


dest_prefix = 'echo-nest-remix-'
for example_dir in glob.glob(os.path.join('examples', '*')):
    example_files = glob.glob(os.path.join(example_dir, '*'))
    actual_files = []
    sub_path_tuples = []
    for example_file in example_files:
        files_within_example_file = glob.glob(os.path.join(example_file, '*'))
        if not any(files_within_example_file):
            actual_files.append(example_file)
        else:
            sub_path_tuples.append((dest_prefix+example_file, files_within_example_file))
    all_data_files.append((dest_prefix + example_dir, actual_files))
    if any(sub_path_tuples):
        all_data_files.extend(sub_path_tuples)


setup(name='The Echo Nest Remix API',
      ext_modules = [get_soundtouch(), get_dirac(), get_action()],
      version='1.3b',
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
