Welcome to The Echo Nest Remix API installer.

This will install Python libraries that let you do great things with music and video. The libraries will be installed in your Python site-packages folder and will be available system-wide.

You'll probably want to start with example scripts.

On the Mac these are placed in /usr/share/local/echo-nest-remix-examples.

On Windows these are placed in your Python root folder: C:\Python26.

You will need an API key set up to use this software. Register for a key at http://developer.echonest.com/ .

Then either (1) set the environment variable ECHO_NEST_API_KEY to be your key, or (2) put the lines

from pyechonest import config
config.ECHO_NEST_API_KEY="your key" 

at the top of any scripts you run.

Please see more information and documentation at

http://code.google.com/p/echo-nest-remix

