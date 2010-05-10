# created 4/21/2010 by Jason
# http://docs.python.org/extending/building.html
from distutils.core import setup, Extension
import os
import sys
try:
    import numpy
except Exception:
    sys.exit("numpy is required for use of pydirac")

ver = ".".join([str(x) for x in sys.version_info[0:2]]) # 2.6, 2.5 etc

def get_numpy_includes():
    gets = [numpy.get_include, numpy.get_numarray_include, numpy.get_numpy_include]
    includes = []
    for f in gets:
        try:
            includes.append(f())
        except Exception:
            pass
    return includes
    
def get_platform_info():
    library_dir = 'libs/'
    libName = 'Dirac'
    link_args = []
    src_dir = ['source']
    includes = get_numpy_includes()
    
    if hasattr(os, 'uname'):
        if os.uname()[0] == "Darwin":
            library_dir += 'MacOSX'
            libName += 'LE'
            link_args.append('-framework Carbon')
            # prefix = '/System/Library/Frameworks/Python.framework/Versions/%s/Extras/lib/python/numpy/' % ver
            # includes = [prefix + s for s in ['core/include', 'numarray']]
        else:            
            library_dir += 'Linux'
            prefix = '/usr/lib/python/%s/site-packages/numpy/' % ver
            #includes = [prefix + s for s in ['core/include', 'numarray', 'numarray/numpy']]
    else:
        library_dir += 'Windows'
    return (src_dir + includes, library_dir, libName, link_args )

includes, library_dir, libName, link_args = get_platform_info()

dirac = Extension(  "dirac", 
                    sources = ['diracmodule.cpp', 'source/Dirac_LE.cpp'],
                    extra_compile_args = [],
                    include_dirs = includes,
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
      