# created 4/21/2010 by Jason
# http://docs.python.org/extending/building.html
from distutils.core import setup, Extension
import os
import sys

ver = ".".join([str(x) for x in sys.version_info[0:2]]) # 2.6, 2.5 etc

def get_platform_info():
    library_dir = 'libs/'
    libName = 'Dirac'
    link_args = []#['--enable-shared', '--enable-static', '-framework Carbon']
    
    if hasattr(os, 'uname'):
        if os.uname()[0] == "Darwin":
            library_dir += 'MacOSX'
            libName += 'LE'
            link_args = ['-framework Carbon']
        else:
            library_dir += 'Linux'
    else:
        library_dir += 'Windows'
    return (library_dir, libName, link_args)
    
library_dir, libName, link_args = get_platform_info()

dirac = Extension(  "dirac", 
                    sources = ['diracmodule.cpp', 'source/Dirac_LE.cpp'],
                    extra_compile_args = [],
                    include_dirs = ['source', 
                                    '/System/Library/Frameworks/Python.framework/Versions/%s/Extras/lib/python/numpy/core/include' % ver,
                                    '/System/Library/Frameworks/Python.framework/Versions/%s/Extras/lib/python/numpy/numarray' % ver,
                                    '/usr/lib/python/%s/site-packages/numpy/numarray/numpy' % ver,
                                    '/usr/lib/python/%s/site-packages/numpy/numarray' % ver,
                                    '/usr/lib/python/%s/site-packages/numpy/core/include' % ver,
                                    ],
                    libraries = [libName],
                    library_dirs = [library_dir],
                    extra_link_args = link_args,
                    depends=[__file__] # force rebuild whenever this script is changed.
                 )

setup(  name="dirac", 
        version = '0.1',
        description = 'Python interface to Dirac LE',
        author = 'Tristan Jehan',
        author_email = 'tristan@echonest.com',
        url = 'http://code.echonest.com/p/echo-nest-remix',
        long_description = '''See Short Description.''',
        ext_modules=[dirac] )
      