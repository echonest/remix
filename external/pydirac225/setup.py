# created 4/21/2010 by Jason
# http://docs.python.org/extending/building.html
from distutils.core import setup, Extension
import os
import numpy

platform = os.uname()[0] if hasattr(os, 'uname') else 'Windows'
link_args = ['-framework', 'Carbon'] if platform == 'Darwin' else []

dirac = Extension(  "dirac",
                    sources = ['diracmodule.cpp', 'source/Dirac_LE.cpp'],
                    extra_compile_args = [],
                    include_dirs = ['source', numpy.get_include(), numpy.get_numarray_include()],
                    libraries = ['Dirac'],
                    library_dirs = [os.path.join('libs', platform)],
                    extra_link_args = link_args,
                    depends=[__file__] # force rebuild whenever this script is changed.
                 )

setup(  name="dirac", 
        version = '0.1',
        description = 'Python interface to Dirac LE',
        author = 'Tristan Jehan',
        author_email = 'tristan@echonest.com',
        url = 'http://code.echonest.com/p/echo-nest-remix',
        ext_modules=[dirac], 
        requires=['numpy']
     )
      