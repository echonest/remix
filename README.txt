Greetings, intrepid coder.  This is the readme file for the Python
'echonest' package, an interface to the Echo Nest Remix API.  This
will help you easily upload data to the Echo Nest Remix web service
and easily manipulate what you get back.



INSTALLATION:

From the directory where you found this readme file, execute the
following:

  sudo python setup.py install

This will install the echonest package and make it available through
the usual means:

  import echonest

The echonest.audio module requires that 'ffmpeg' also be installed.
On Ubuntu and other Debian-based systems, ffmpeg can be installed
using:

  sudo aptitude install ffmpeg



EXAMPLES:

The 'examples' directory contains some examples of how to use the
echonest package.  The examples are not installed as packages, but can
be run as normal Python scripts.  For example:

  python reverse.py

and

  python cowbell.py

will both print out detailed usage instructions.  The examples may
require you to install additional Python packages.




FEEDBACK:

All feedback and participation is welcome.  Contact us through the
Google Code project page.
