#!/usr/bin/env python

__version__ = "$Revision: 0 $"
# $Source$

from distutils.core import setup

setup(name='echonest',
      version='1.0',
      description='Python interface to The Echo Nest web APIs.',
      author='Joshua Lifton',
      author_email='lifton@echonest.com',
      maintainer='Brian Whitman',
      maintainer_email='brian@echonest.com',
      url='http://developer.echonest.com/',
      download_url='http://code.google.com/',
      package_dir={'echonest':'src/echonest'},
      packages=['echonest', 'echonest.web', 'echonest.support', 'echonest.support.midi'],
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
