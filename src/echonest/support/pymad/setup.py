#!/usr/bin/env python

"""Setup script for the MAD module distribution."""

import os, re, sys, string

from distutils.core import setup
from distutils.extension import Extension

VERSION_MAJOR = 0
VERSION_MINOR = 6
pymad_version = str(VERSION_MAJOR) + "." + str(VERSION_MINOR)

def get_setup():
    data = {}
    r = re.compile(r'(\S+)\s*=\s*(.+)')
    
    if not os.path.isfile('Setup'):
        print "No 'Setup' file. Perhaps you need to run the configure script."
        sys.exit(1)
        
    f = open('Setup', 'r')
        
    for line in f.readlines():
        m = r.search(line)
        if not m:
            print "Error in setup file:", line
            sys.exit(1)
        key = m.group(1)
        val = m.group(2)
        data[key] = val
        
    return data

data = get_setup()

defines = [('VERSION_MAJOR', VERSION_MAJOR),
           ('VERSION_MINOR', VERSION_MINOR),
           ('VERSION', '"%s"' % pymad_version)]

if data['endian'] == "big":
    defines.append(('BIGENDIAN', 1))

madmodule = Extension(
    name='madmodule',
    sources=['src/madmodule.c', 'src/pymadfile.c', 'src/xing.c'],
    define_macros = defines,
    include_dirs=[data['mad_include_dir']],
    library_dirs=[data['mad_lib_dir']],
    libraries=string.split(data['mad_libs']))

setup ( # Distribution metadata
    name = "pymad",
    version = pymad_version,
    description = "A wrapper for the MAD libraries.",
    author = "Jamie Wilkinson",
    author_email = "jaq@spacepants.org",
    url = "http://spacepants.org/src/pymad/",
    license = "GPL",
    
    ext_modules = [madmodule])
