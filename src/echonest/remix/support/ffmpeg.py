import os
import sys
import time
import numpy
import logging
import tempfile
import subprocess
import cStringIO
from exceptionthread import ExceptionThread

log = logging.getLogger(__name__)

def get_os():
    """returns is_linux, is_mac, is_windows"""
    if hasattr(os, 'uname'):
        if os.uname()[0] == "Darwin":
            return False, True, False
        return True, False, False
    return False, False, True

def ensure_valid(filename):
    command = "en-ffmpeg -i %s -acodec copy -f null -" % filename

    if os.path.getsize(filename) == 0:
        raise ValueError("Input file contains 0 bytes")

    log.info("Calling ffmpeg: %s", command)

    o = subprocess.call(command.split(),
                        stdout=open(os.devnull, 'wb'),
                        stderr=open(os.devnull, 'wb'))
    if o == 0:
        return True
    else:
        raise ValueError("FFMPEG failed to read the file (%d)" % o)


def ffmpeg(infile, outfile=None, overwrite=True, bitRate=None,
          numChannels=None, sampleRate=None, verbose=True, lastTry=False):
    """
    Executes ffmpeg through the shell to convert or read media files.
    If passed a file object, give it to FFMPEG via pipe. Otherwise, allow
    FFMPEG to read the file from disk.

    If `outfile` is passed in, this will return the sampling frequency and
    number of channels in the output file. Otherwise, it will return an
    ndarray object filled with the raw PCM data.
    """
    start = time.time()
    filename = None
    if type(infile) is str or type(infile) is unicode:
        filename = str(infile)

    command = "en-ffmpeg"
    if filename:
        command += " -i \"%s\"" % infile
    else:
        command += " -i pipe:0"

    if overwrite:
        command += " -y"

    if bitRate is not None:
        command += " -ab " + str(bitRate) + "k"

    if numChannels is not None:
        command += " -ac " + str(numChannels)
    else:
        command += " -ac 2"

    if sampleRate is not None:
        command += " -ar " + str(sampleRate)
    else:
        command += " -ar 44100" 

    if outfile is not None:
        command += " \"%s\"" % outfile
    else:
        command += " pipe:1"
    if verbose:
        print >> sys.stderr, command

    (lin, mac, win) = get_os()
    p = subprocess.Popen(
            command,
            shell=True,
            stdin=(None if filename else subprocess.PIPE),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            close_fds=(not win)
    )

    if filename:
        f, e = p.communicate()
    else:
        try:
            infile.seek(0)
        except:  # if the file is not seekable
            pass
        f, e = p.communicate(infile.read())
        try:
            infile.seek(0)
        except:  # if the file is not seekable
            pass
    #   If FFMPEG couldn't read that, let's write to a temp file
    #   For some reason, this always seems to work from file (but not pipe)
    if 'Could not find codec parameters' in e and not lastTry:
        log.warning("FFMPEG couldn't find codec parameters - writing to temp file.")
        fd, name = tempfile.mkstemp('.audio')
        handle = os.fdopen(fd, 'w')
        infile.seek(0)
        handle.write(infile.read())
        handle.close()
        r = ffmpeg(name,
                   bitRate=bitRate,
                   numChannels=numChannels,
                   sampleRate=sampleRate,
                   verbose=verbose,
                   lastTry=True)
        log.info("Unlinking temp file at %s...", name)
        os.unlink(name)
        return r

    ffmpeg_error_check(e)
    mid = time.time()
    log.info("Decoded in %ss.", (mid - start))
    if outfile:
        return settings_from_ffmpeg(e)
    else:
        return numpy.frombuffer(f, dtype=numpy.int16).reshape((-1, 2))


def ffmpeg_downconvert(infile, lastTry=False):
    """
    Downconvert the given filename (or file-like) object to 32kbps MP3 for analysis.
    Works well if the original file is too large to upload to the Analyze API.
    """
    start = time.time()

    filename = None
    if type(infile) is str or type(infile) is unicode:
        filename = str(infile)

    command = "en-ffmpeg" \
            + (" -i \"%s\"" % infile if filename else " -i pipe:0") \
            + " -b 32k -f mp3 pipe:1"
    log.info("Calling ffmpeg: %s", command)

    (lin, mac, win) = get_os()
    p = subprocess.Popen(
        command,
        shell=True,
        stdin=(None if filename else subprocess.PIPE),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        close_fds=(not win)
    )
    if filename:
        f, e = p.communicate()
    else:
        infile.seek(0)
        f, e = p.communicate(infile.read())
        infile.seek(0)

    if 'Could not find codec parameters' in e and not lastTry:
        log.warning("FFMPEG couldn't find codec parameters - writing to temp file.")
        fd, name = tempfile.mkstemp('.')
        handle = os.fdopen(fd, 'w')
        infile.seek(0)
        handle.write(infile.read())
        handle.close()
        r = ffmpeg_downconvert(name, lastTry=True)
        log.info("Unlinking temp file at %s...", name)
        os.unlink(name)
        return r
    ffmpeg_error_check(e)

    io = cStringIO.StringIO(f)
    end = time.time()
    io.seek(0, os.SEEK_END)
    bytesize = io.tell()
    io.seek(0)
    log.info("Transcoded to 32kbps mp3 in %ss. Final size: %s bytes.",
             (end - start), bytesize)
    return io


def settings_from_ffmpeg(parsestring):
    """
    Parses the output of ffmpeg to determine sample rate and frequency of
    an audio file.
    """
    parse = parsestring.split('\n')
    freq, chans = 44100, 2
    for line in parse:
        if "Stream #0" in line and "Audio" in line:
            segs = line.split(", ")
            for s in segs:
                if "Hz" in s:
                    #print "Found: "+str(s.split(" ")[0])+"Hz"
                    freq = int(s.split(" ")[0])
                elif "stereo" in s:
                    #print "stereo"
                    chans = 2
                elif "mono" in s:
                    #print "mono"
                    chans = 1
    return freq, chans

ffmpeg_install_instructions = """
en-ffmpeg not found! Please make sure ffmpeg is installed and create a link as follows:
    sudo ln -s `which ffmpeg` /usr/local/bin/en-ffmpeg
"""

def ffmpeg_error_check(parsestring):
    "Looks for known errors in the ffmpeg output"
    parse = parsestring.split('\n')
    error_cases = ["Unknown format",        # ffmpeg can't figure out format of input file
                   "error occur",           # an error occurred
                   "Could not open",        # user doesn't have permission to access file
                   "not found"              # could not find encoder for output file
                   "Invalid data",          # bad input data
                   "Could not find codec",  # corrupted, incomplete, or otherwise bad file
                    ]
    for num, line in enumerate(parse):
        if "command not found" in line or "en-ffmpeg: not found" in line:
            raise RuntimeError(ffmpeg_install_instructions)
        for error in error_cases:
            if error in line:
                report = "\n\t".join(parse[num:])
                raise RuntimeError("ffmpeg conversion error:\n\t" + report)
