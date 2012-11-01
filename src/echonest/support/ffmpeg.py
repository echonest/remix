import os
import sys
import numpy
import subprocess
from threading import Semaphore
from exceptionthread import ExceptionThread


def get_os():
    """returns is_linux, is_mac, is_windows"""
    if hasattr(os, 'uname'):
        if os.uname()[0] == "Darwin":
            return False, True, False
        return True, False, False
    return False, False, True


class FFMPEGStreamHandler(ExceptionThread):
    def __init__(self, infile, numChannels=2, sampleRate=44100):
        ExceptionThread.__init__(self)
        filename = None
        if type(infile) is str or type(infile) is unicode:
            filename = str(infile)

        command = "en-ffmpeg"
        if filename:
            command += " -i \"%s\"" % infile
        else:
            command += " -i pipe:0"
        if numChannels is not None:
            command += " -ac " + str(numChannels)
        if sampleRate is not None:
            command += " -ar " + str(sampleRate)
        command += " -f s16le -acodec pcm_s16le pipe:1"

        (lin, mac, win) = get_os()
        self.p = subprocess.Popen(
            command,
            shell=True,
            stdin=(None if filename else subprocess.PIPE),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            close_fds=(not win)
        )
        self.infile = infile
        self.infile.seek(0)
        self.insize = 2 ** 20
        self.__s = Semaphore(0)
        self.daemon = True
        self.running = True
        self.start()

    def __del__(self):
        self.finish()

    def run(self):
        while self.running:
            self.__s.release()
            try:
                self.p.stdin.write(self.infile.read(self.insize))
            except IOError:
                break
            self.__s.acquire()

    def finish(self):
        self.running = False
        try:
            self.p.kill()
            self.p.wait()
        except OSError:
            pass

    #   TODO: Abstract me away from 44100Hz, 2ch 16 bit
    def read(self, samples=-1):
        if not self.running:
            raise ValueError("FFMPEG has already finished!")
        self.__s.release()
        arr = numpy.fromfile(self.p.stdout,
                               dtype=numpy.int16,
                               count=samples * 2 if samples > 0 else samples)
        if samples < 0 or len(arr) < samples * 2:
            self.finish()
        arr = numpy.reshape(arr, (-1, 2))
        self.__s.acquire()
        return arr

    def feed(self, samples):
        self.__s.release()
        self.p.stdout.read(samples * 4)
        self.__s.acquire()


def ffmpeg(infile, outfile=None, overwrite=True, bitRate=None, numChannels=None, sampleRate=None, verbose=True):
    """
    Executes ffmpeg through the shell to convert or read media files.
    """
    command = "en-ffmpeg"
    if overwrite:
        command += " -y"
    command += " -i \"" + infile + "\""
    if bitRate is not None:
        command += " -ab " + str(bitRate) + "k"
    if numChannels is not None:
        command += " -ac " + str(numChannels)
    if sampleRate is not None:
        command += " -ar " + str(sampleRate)
    if outfile is not None:
        command += " \"%s\"" % outfile
    if verbose:
        print >> sys.stderr, command

    (lin, mac, win) = get_os()
    if(not win):
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
    else:
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=False)
    return_val = p.communicate()
    ffmpeg_error_check(return_val[1])
    return settings_from_ffmpeg(return_val[1])


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
        if "command not found" in line:
            raise RuntimeError(ffmpeg_install_instructions)
        for error in error_cases:
            if error in line:
                report = "\n\t".join(parse[num:])
                raise RuntimeError("ffmpeg conversion error:\n\t" + report)
