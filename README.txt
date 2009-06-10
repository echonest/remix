I. Mac OS X installation instructions
II. Debian Linux installation instructions
III. Windows installation instructions

=====

I. MAC OS X INSTALLATION INSTRUCTIONS:

 * Download and unzip "echo-next-remix-1.1.zip" from http://code.google.com/p/echo-nest-remix/downloads/list.

 * Or, you can checkout the source code at http://code.google.com/p/echo-nest-remix/source/checkout. 

 * If you don't already have FFmpeg installed (try typing "ffmpeg" into a Terminal window), download and install the FFmpeg binaries (the following instructions were adapted from this tutorial [http://www.macosxhints.com/article.php?story=20061220082125312&mode=print]):
          o Download the FFmpeg binary from [http://static.echonest.com/ffmpeg-osx.zip]
          o Unzip ffmpeg-osx.zip. Copy the contents (the file "ffmpeg") to the folder /usr/local/bin
          o Open Terminal. It can be found in the Applications/Utilities folder.
          o Execute the following in Terminal:

            sudo chown root:wheel /usr/local/bin/ffmpeg
            sudo chmod 755 /usr/local/bin/ffmpeg

          o Now you have a working version of FFmpeg. 

 * Register for an Echo Nest Developer account at The Developer Nest [http://developer.echonest.com/]. You will receive an API Key. 

 * Navigate to the folder where you downloaded the Echo Nest Remix API distribution and unzipped it. e.g. 

> cd ~/Downloads/echo-nest-remix-dist/

 * Using any text editor, open the file src/echonest/web/config.py and replace the text "Replace this text with your API Key" with the API Key you received when you registered for an Echo Nest Developer account. Save this file. 

 * In Terminal, navigate to the folder where you downloaded and unzipped the Echo Nest Remix API distribution. Execute: 

> python sudo setup.py install

 * Then navigate to the folder examples/one/ and run the example: 

> cd examples/one/
> python one.py any_mp3_file_you_have.mp3 output.mp3

=====

II. DEBIAN LINUX INSTALLATION INSTRUCTIONS:

 * You need ffmpeg and at least Python 2.5. Your distribution probably already has both. If not,

> apt-get install ffmpeg python2.5 subversion

 * (Note that your version of ffmpeg might not have all the codecs due to patent & etc issues. If you want them, try out the Debian FFmpeg installer [http://code.google.com/p/debian-ffmpeg-installer/].)

 * After that, simply check out the Echo Nest Remix API trunk or download the release package.

> cd ~
> svn checkout http://echo-nest-remix.googlecode.com/svn/trunk/ echo-nest-remix-read-only

Get an API key at the EN developer site. Edit your API key in ~/echonest-remix-read-only/src/echonest/web/config.py

Install remix

> cd ~/echo-nest-remix-read-only/
> sudo python setup.py install

 * After the party, it's the after party:

> cd ~/echo-nest-remix-read-only/examples/drums
> python drums.py  HereComesTheSun.mp3 breaks/AmenBrother.wav HereComesTheDrums.mp3 64 4 0.6

=====

III. WINDOWS INSTALLATION INSTRUCTIONS:

You need Python, ffmpeg and NumPy installed. You may already have these installed.

 * If you don't have Python 2.5 or greater installed (try typing "python" in a cmd window) download Python 2.6.2 for Windows [http://www.python.org/ftp/python/2.6.2/python-2.6.2.msi] and run the installer.

 * Make sure you add C:\Python26 (or whatever drive you installed it to) to your PATH environment variable. [http://www.python.org/doc/faq/windows/#how-do-i-run-a-python-program-under-windows] After doing this step log out and log back in to make sure the PATH is set.

 * If you don't have ffmpeg installed download a build of ffmpeg for Windows. (try typing "ffmpeg" in a cmd window) [http://static.echonest.com/ffmpeg-r17988-komeil.cab] (This is a cached copy of this build [http://komeil.spaces.live.com/blog/cns!11E09A8750032F2C!614.entry], but any build is fine.) Unpack the ffmpeg.exe and move it to C:\Python26 (or whatever drive you installed Python to.)

 * If you don't have NumPy installed (open python and type "import numpy" to see)  download and run the Windows Python 2.6 Numpy "Superpack". [http://sourceforge.net/project/downloading.php?group_id=1369&filename=numpy-1.3.0-win32-superpack-python2.6.exe&a=90023264]

 * Go to the start menu, then Run, then type "cmd"

 * cd to where you downloaded the Echo Nest Remix API distribution and unzipped it. e.g.

cd Desktop\echo-nest-remix\

 * using any text editor (except for Notepad, it will not show the line endings properly), open the file src\echonest\web\config.py and replace the text "Replace this text with your API Key" with the API Key you received when you registered for an Echo Nest Developer account at The Developer Nest [http://developer.echonest.com]. Save the file.

 * From the root the downloaded Remix folder, type

python setup.py install

 * Then cd to examples\one\ and run 

python one.py any_mp3_file_you_have.mp3 output.mp3
