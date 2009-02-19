INTRODUCTION
============

Greetings, intrepid coder.  This is the readme file for the Python
'echonest' package, an interface to the Echo Nest Remix API.  This
will help you easily upload data to the Echo Nest Remix web service
and easily manipulate what you get back.


INSTALLATION
============

1. Install the MAD libraries. Get them here:

  http://www.underbit.com/products/mad/

2. Install the lame libraries. Get them here:

  http://spaghetticode.org/lame/

3. Install the pymad package from the Echo Nest Remix distribution.
From echo-nest-remix/src/echonest/support/pymad, execute:

  python config_unix.py

This will locate the mad libraries on your system. You may need to
pass the script a --prefix value if you've installed your mad stuff
someplace weird. Then execute:

  python setup.py build
  sudo python setup.py install

4. Install the python-lame package from the Echo Nest Remix
distribution. From echo-nest-remix/src/echonest/support/python-lame,
execute:

  python setup.py build
  sudo python setup.py install


5. From the directory where you found this readme file, execute:

  sudo python setup.py install

This will install the echonest package and make it available through
the usual means:

  import echonest

6. Optionally install ffmpeg (this is not needed at the moment, but
will be soon). There are a few ways to install the ffmpeg binaries
on your system with the first, unpacking the file form the FFmpegX
distribution, being the easiest.

  -Download FFMpegX and extract the binary:
  
    http://www.macosxhints.com/article.php?story=20061220082125312&mode=print

  -You can also use DarwinPorts if you have that installed:

    http://ffmpeg.darwinports.com/

  -Fink has a binary package for ffmpeg:

    http://pdb.finkproject.org/pdb/package.php/ffmpeg

  -Most complicated but most control: install ffmpeg from source.

    http://stephenjungels.com/jungels.net/articles/ffmpeg-howto.html

When this step is completed, opening Terminal and typing "ffmpeg"
should show you a usage screen.

On Ubuntu and other Debian-based systems, ffmpeg can be installed
using:

  sudo aptitude install ffmpeg



EXAMPLES
========

The 'examples' directory contains some examples of how to use the
echonest package.  The examples are not installed as packages, but can
be run as normal Python scripts.  For example:

  python reverse.py

and

  python cowbell.py

will both print out detailed usage instructions.


FEEDBACK
========

All feedback and participation is welcome.  Contact us through the
Google Code project page.
