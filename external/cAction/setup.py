# created 5/11/2010 by Jason
from distutils.core import setup, Extension
import os, sys
import numpy

cAction = Extension("cAction",
                    sources = ['actionmodule.cpp'],
                    extra_compile_args = [],
                    include_dirs = [numpy.get_include(), numpy.get_numarray_include()],
                    depends=[__file__] # force rebuild whenever this script is changed.
                 )

setup(  name="cAction", 
        version = '0.1',
        description = 'c implementation of algorithms from action.py',
        author = 'Jason Sundram',
        author_email = 'jason@echonest.com',
        url = 'http://code.echonest.com/p/echo-nest-remix',
        ext_modules=[cAction], 
        requires=['numpy']
     )

