#!/usr/bin/env python

__version__ = "2.4.0"

# Monkeypatch so that easy_install can install en-ffmpeg and youtube-dl
try:
    from setuptools.sandbox import DirectorySandbox

    def faux_violation(*args):
        pass
    DirectorySandbox._violation = faux_violation
except ImportError:
    pass

import sys
import os
import subprocess
import glob
from distutils.core import setup, Extension
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
    compile_args = [] if is_windows else ['-Wno-unused']
    return Extension("cAction",
                        sources = [os.path.join(cAction, 'actionmodule.cpp')],
                        extra_compile_args = compile_args,
                        include_dirs = [numpy.get_include()],
                     )


def get_dirac():
    link_args = ['-framework', 'Carbon'] if is_mac else []
    compile_args = [] if is_windows else ['-Wno-unused', '-Wno-error=format-security']

    pydirac = os.path.join('external', 'pydirac225')
    lib_sources = [os.path.join(pydirac, 'diracmodule.cpp'), os.path.join(pydirac, 'source', 'Dirac_LE.cpp')]

    platform = os.uname()[0] if hasattr(os, 'uname') else 'Windows'
    libname = 'Dirac64' if platform == 'Linux' and os.uname()[-1] == 'x86_64' else 'Dirac'
    return Extension('dirac',
                    sources = lib_sources,
                    extra_compile_args = compile_args,
                     include_dirs = ['source', numpy.get_include()],
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

    if is_linux:
        sources += ['cpu_detect_x86_gcc.cpp']
        extra_compile_args = ['-O3', '-Wno-unused', '-Wno-error=format-security']
    elif is_mac:
        sources += ['cpu_detect_x86_gcc.cpp']
        extra_compile_args = ['-O3', '-Wno-unused', '-Wno-error=format-security']
    elif is_windows:
        sources += ['cpu_detect_x86_win.cpp', '3dnow_win.cpp']
    pysoundtouch = os.path.join('external', 'pysoundtouch14', 'libsoundtouch')
    lib_sources = [os.path.join(pysoundtouch, i) for i in sources]
    lib_sources += [os.path.join('external', 'pysoundtouch14', 'soundtouchmodule.cpp')]
    return Extension('soundtouch',
                     sources = lib_sources,
                     extra_compile_args = extra_compile_args,
                     include_dirs = [numpy.get_include()]
    )


all_data_files = []

if is_mac or is_linux:
    # If we're in a virtualenv:
    if 'real_prefix' in dir(sys):
        data_path = os.path.join(sys.prefix, "local/bin")
    else:
        data_path = '/usr/local/bin'
if is_mac:
    all_data_files  = [(data_path, ['external/en-ffmpeg/mac/en-ffmpeg', 'external/youtube-dl/youtube-dl'])]
if is_linux:
    all_data_files  = [(data_path, ['external/youtube-dl/youtube-dl'])]

if is_windows:
    all_data_files  = [('.', ['external\\en-ffmpeg\\win\\en-ffmpeg.exe',
                             'external\\youtube-dl\\youtube-dl',
                             'external\\pydirac225\\libs\\Windows\\DiracLE.dll'])]


# Set the path to the examples:
if is_windows:
    dest_prefix = 'echo-nest-remix-'
else:
    # If we're in a virtualenv:
    if 'real_prefix' in dir(sys):
        dest_prefix = os.path.join(sys.prefix, "local/share/echo-nest-remix-")
    else:
        dest_prefix = '/usr/local/share/echo-nest-remix-'


for example_dir in glob.glob(os.path.join('examples', '*')):
    example_files = glob.glob(os.path.join(example_dir, '*'))
    actual_files = []
    sub_path_tuples = []
    for example_file in example_files:
        files_within_example_file = glob.glob(os.path.join(example_file, '*'))
        if not any(files_within_example_file):
            actual_files.append(example_file)
        else:
            sub_path_tuples.append((dest_prefix + example_file, files_within_example_file))
    all_data_files.append((dest_prefix + example_dir, actual_files))
    if any(sub_path_tuples):
        all_data_files.extend(sub_path_tuples)


setup(name='remix',
      ext_modules = [get_soundtouch(), get_dirac(), get_action()],
      version=__version__,
      description='The internet synthesizer. Make things with music.',
      author='The Echo Nest',
      author_email='brian@echonest.com',
      maintainer='Brian Whitman',
      maintainer_email='brian@echonest.com',
      url='http://developer.echonest.com/',
      download_url='http://static.echonest.com/remix/packages/remix-%s.tar.gz' % __version__,
      license='New BSD',
      data_files= all_data_files,
      package_dir={'echonest':'src/echonest', 'pyechonest':'pyechonest/pyechonest'},
      packages=['echonest', 'echonest.remix', 'echonest.remix.support', 'echonest.remix.support.midi', 'pyechonest'],
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

# Hack for pip install, to get correct permissions for en-ffmpeg and youtube-dl
try:
    if is_mac:
        os.chmod(os.path.join(data_path, 'en-ffmpeg'), 0755)
        os.chmod(os.path.join(data_path, 'youtube-dl'), 0755)
    if is_linux:
        os.chmod(os.path.join(data_path, 'youtube-dl'), 0755)
except OSError:
    pass

# Hack to fix ownership of example files, when installing with sudo
# This does not need to be done on a virtualenv install
# And, if we do setup.py develop, the files might not be there
if is_mac or is_linux and 'real_prefix' not in dir(sys) and 'install' in sys.argv:
    example_path = dest_prefix + 'examples/'
    if os.path.exists(example_path):
        res = subprocess.Popen(['logname'], stdout=subprocess.PIPE).communicate()[0]
        user_name = res.strip()
        group_id = os.getpgrp()
        res = subprocess.call(['chown', '-R', '%s:%s' % (user_name, group_id), example_path])
