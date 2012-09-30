#!/usr/bin/env python
# encoding: utf=8
"""
video.py

Framework that turns video into silly putty.

Created by Robert Ochshorn on 2008-5-30.
Refactored by Ben Lacker on 2009-6-18.
Copyright (c) 2008 The Echo Nest Corporation. All rights reserved.
"""
from numpy import *
import os
import re
import shutil
import subprocess
import sys
import tempfile

from echonest import audio
from pyechonest import config


class ImageSequence():
    def __init__(self, sequence=None, settings=None):
        "builds sequence from a filelist, or another ImageSequence object"
        self.files, self.settings = [], VideoSettings()
        if isinstance(sequence, ImageSequence) or issubclass(sequence.__class__, ImageSequence): #from ImageSequence
           self.settings, self.files = sequence.settings, sequence.files
        if isinstance(sequence, list): #from filelist
            self.files = sequence
        if settings is not None:
            self.settings = settings
        self._init()

    def _init(self):
        "extra init settings/options (can override...)"
        return
        
    def __len__(self):
        "how many frames are in this sequence?"
        return len(self.files)

    def __getitem__(self, index):
        index = self.indexvoodo(index)
        if isinstance(index, slice):
            return self.getslice(index)
        else:
            raise TypeError("must provide an argument of type 'slice'")

    def getslice(self, index):
        "returns a slice of the frames as a new instance"
        if isinstance(index.start, float):
            index = slice(int(index.start*self.settings.fps), int(index.stop*self.settings.fps), index.step)
        return self.__class__(self.files[index], self.settings)

    def indexvoodo(self, index):
        "converts index to frame from a variety of forms"
        if isinstance(index, float):
            return int(index*self.settings.fps)
        return self._indexvoodoo(index)

    def _indexvoodoo(self, index):
        #obj to slice
        if not isinstance(index, slice) and hasattr(index, "start") and hasattr(index, "duration"):
            sl =  slice(index.start, index.start+index.duration)
            return sl
        #slice of objs: return slice(start.start, start.end.start+start.end.duration)
        if isinstance(index, slice):
            if hasattr(index.start, "start") and hasattr(index.stop, "duration") and hasattr(index.stop, "start"):
                sl = slice(index.start.start, index.stop.start+index.stop.duration)
                return sl
        return index

    def __add__(self, imseq2):
        """returns an ImageSequence with the second seq appended to this
        one. uses settings of the self."""
        self.render()
        imseq2.render() #todo: should the render be applied here? is it destructive? can it render in the new sequence?
        return self.__class__(self.files + imseq2.files, self.settings)

    def duration(self):
        "duration of a clip in seconds"
        return len(self) / float(self.settings.fps)

    def frametoim(self, index):
        "return a PIL image"
        return self.__getitem__(index)

    def renderframe(self, index, dest=None, replacefileinseq=True):
        "renders frame to destination directory. can update sequence with rendered image (default)"
        if dest is None:
            #handle, dest = tempfile.mkstemp()
            dest = tempfile.NamedTemporaryFile().name
        #copy file without loading
        shutil.copyfile(self.files[index], dest)
        #symlink file...
        #os.symlink(self.files[index], dest)
        if replacefileinseq:
            self.files[index] = dest
        
    def render(self, direc=None, pre="image", replacefiles=True):
        "renders sequence to stills. can update sequence with rendered images (default)"
        if direc is None: 
            #nothing to render...
            return
        dest = None
        for i in xrange(len(self.files)):
            if direc is not None:
                dest = os.path.join(direc, pre+'%(#)06d.' % {'#':i})+self.settings.imageformat()
            self.renderframe(i, dest, replacefiles)


class EditableFrames(ImageSequence):
    "Collection of frames that can be easily edited"

    def fadein(self, frames):
        "linear fade in"
        for i in xrange(frames):
            self[i] *= (float(i)/frames) #todo: can i do this without floats?

    def fadeout(self, frames):
        "linear fade out"
        for i in xrange(frames):
            self[len(self)-i-1] *= (float(i)/frames)


class VideoSettings():
    "simple container for video settings"
    def __init__(self):
        self.fps = None #SS.MM
        self.size = None #(w,h)
        self.aspect = None #(x,y) -> x:y
        self.bitrate = None #kb/s
        self.uncompressed = False

    def __str__(self):
        "format as ffmpeg commandline settings"
        cmd = ""
        if self.bitrate is not None:
            #bitrate
            cmd += " -b "+str(self.bitrate)+"k"
        if self.fps is not None:
            #framerate
            cmd += " -r "+str(self.fps)
        if self.size is not None:
            #size
            cmd += " -s "+str(self.size[0])+"x"+str(self.size[1])
        if self.aspect is not None:
            #aspect
            cmd += " -aspect "+str(self.aspect[0])+":"+str(self.aspect[1])
        return cmd

    def imageformat(self):
        "return a string indicating to PIL the image format"
        if self.uncompressed:
            return "ppm"
        else:
            return "jpeg"


class SynchronizedAV():
    "SynchronizedAV has audio and video; cuts return new SynchronizedAV objects"

    def __init__(self, audio=None, video=None):
        self.audio = audio
        self.video = video

    def __getitem__(self, index):
        "Returns a slice as synchronized AV"
        if isinstance(index, slice):
            return self.getslice(index)
        else:
            print >> sys.stderr, "WARNING: frame-based sampling not supported for synchronized AV"
            return None
    
    def getslice(self, index):
        return SynchronizedAV(audio=self.audio[index], video=self.video[index])
    
    def save(self, filename):
        audio_filename = filename + '.wav'
        audioout = self.audio.encode(audio_filename, mp3=False)
        self.video.render()
        res = sequencetomovie(filename, self.video, audioout)
        os.remove(audio_filename)
        return res
    
    def saveAsBundle(self, outdir):
        videodir = os.path.join(outdir, "video")
        videofile = os.path.join(outdir, "source.flv")
        audiofile = os.path.join(outdir, "audio.wav")
        os.makedirs(videodir)
        # audio.wav
        audioout = self.audio.encode(audiofile, mp3=False)
        # video frames (some may be symlinked)
        self.video.render(dir=videodir)
        # video file
        print sequencetomovie(videofile, self.video, audioout)


def loadav(videofile, verbose=True):
    foo, audio_file = tempfile.mkstemp(".mp3")        
    cmd = "en-ffmpeg -y -i \"" + videofile + "\" " + audio_file
    if verbose:
        print >> sys.stderr, cmd
    out = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    res = out.communicate()
    ffmpeg_error_check(res[1])
    a = audio.LocalAudioFile(audio_file)
    v = sequencefrommov(videofile)
    return SynchronizedAV(audio=a, video=v)


def loadavfrombundle(dir):
    # video
    videopath = os.path.join(dir, "video")
    videosettings = VideoSettings()
    videosettings.fps = 25
    videosettings.size = (320, 240)
    video = sequencefromdir(videopath, settings=videosettings)
    # audio
    audiopath = os.path.join(dir, "audio.wav")
    analysispath = os.path.join(dir, "analysis.xml")
    myaudio = audio.LocalAudioFile(audiopath, analysis=analysispath, samplerate=22050, numchannels=1)
    return SynchronizedAV(audio=myaudio, video=video)


def loadavfromyoutube(url, verbose=True):
    """returns an editable sequence from a youtube video"""
    #todo: cache youtube videos?
    foo, yt_file = tempfile.mkstemp()        
    # https://github.com/rg3/youtube-dl/
    cmd = "youtube-dl -o " + "temp.video" + " " + url
    if verbose:
        print >> sys.stderr, cmd
    print "Downloading video..."
    out = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    (res, err) = out.communicate()
    print res, err

    # hack around the /tmp/ issue
    cmd = "mv -f temp.video yt_file"
    out = subprocess.Popen(['mv', '-f', 'temp.video', yt_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    (res, err) = out.communicate()
    return loadav(yt_file)


def youtubedl(url, verbose=True):
    """downloads a video from youtube and returns the file object"""
    foo, yt_file = tempfile.mkstemp()        
    # https://github.com/rg3/youtube-dl/
    cmd = "youtube-dl -o " + yt_file + " " + url
    if verbose:
        print >> sys.stderr, cmd
    out = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    res = out.communicate()
    return yt_file


def getpieces(video, segs):
    a = audio.getpieces(video.audio, segs)
    newv = EditableFrames(settings=video.video.settings)
    for s in segs:
        newv += video.video[s]
    return SynchronizedAV(audio=a, video=newv)


def sequencefromyoutube(url, settings=None, dir=None, pre="frame-", verbose=True):
    """returns an editable sequence from a youtube video"""
    #todo: cache youtube videos?
    foo, yt_file = tempfile.mkstemp()
    # http://bitbucket.org/rg3/youtube-dl
    cmd = "youtube-dl -o " + yt_file + " " + url
    if verbose:
        print >> sys.stderr, cmd
    out = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out.communicate()
    return sequencefrommov(yt_file, settings, dir, pre)


def sequencefromdir(dir, ext=None, settings=None):
    """returns an image sequence with lexographically-ordered images from
    a directory"""
    listing = os.listdir(dir)
    #remove files without the chosen extension
    if ext is not None:
        listing = filter(lambda x: x.split(".")[-1]==ext, listing)
    listing.sort()
    #full file paths, please
    listing = map(lambda x: os.path.join(dir, x), listing)
    return EditableFrames(listing, settings)


def sequencefrommov(mov, settings=None, direc=None, pre="frame-", verbose=True):
    """full-quality video import from stills. will save frames to
    tempspace if no directory is given"""
    if direc is None:
        #make directory for jpegs
        direc = tempfile.mkdtemp()
    format = "jpeg"
    if settings is not None:
        format = settings.imageformat()
    cmd = "en-ffmpeg -i " + mov + " -an -sameq " + os.path.join(direc, pre + "%06d." + format)
    if verbose:
        print >> sys.stderr, cmd
    out = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    res = out.communicate()
    ffmpeg_error_check(res[1])
    settings = settingsfromffmpeg(res[1])
    seq =  sequencefromdir(direc, format, settings)
    #parse ffmpeg output for to find framerate and image size
    #todo: did this actually happen? errorcheck ffmpeg...
    return seq


def sequencetomovie(outfile, seq, audio=None, verbose=True):
    "renders sequence to a movie file, perhaps with an audio track"
    direc = tempfile.mkdtemp()
    seq.render(direc, "image-", False)
    cmd = "en-ffmpeg -y " + str(seq.settings) + " -i " + os.path.join(direc, "image-%06d." + seq.settings.imageformat())
    if audio:
        cmd += " -i " + audio
    cmd += " -sameq " + outfile
    if verbose:
        print >> sys.stderr, cmd
    out = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    res = out.communicate()
    ffmpeg_error_check(res[1])


def convertmov(infile, outfile=None, settings=None, verbose=True):
    """
    Converts a movie file to a new movie file with different settings.
    """
    if settings is None:
        settings = VideoSettings()
        settings.fps = 29.97
        settings.size = (320, 180)
        settings.bitrate = 200
    if not isinstance(settings, VideoSettings):
        raise TypeError("settings arg must be a VideoSettings object")
    if outfile is None:
        foo, outfile = tempfile.mkstemp(".flv")
    cmd = "en-ffmpeg -y -i " + infile + " " + str(settings) + " -sameq " + outfile
    if verbose:
        print >> sys.stderr, cmd
    out = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    res = out.communicate()
    ffmpeg_error_check(res[1])
    return outfile


def settingsfromffmpeg(parsestring):
    """takes ffmpeg output and returns a VideoSettings object mimicking
    the input video"""
    settings = VideoSettings()
    parse = parsestring.split('\n')
    for line in parse:
        if "Stream #0.0" in line and "Video" in line:
            segs = line.split(", ")
            for seg in segs:
                if re.match("\d*x\d*", seg):
                    #dimensions found
                    settings.size = map(int, seg.split(" ")[0].split('x'))
                    if "DAR " in seg:
                        #display aspect ratio
                        start = seg.index("DAR ")+4
                        end = seg.index("]", start)
                        settings.aspect = map(int, seg[start:end].split(":"))
                elif re.match("(\d*\.)?\d+[\s]((fps)|(tbr)|(tbc)).*", seg):
                    #fps found
                    #todo: what's the difference between tb(r) and tb(c)?
                    settings.fps = float(seg.split(' ')[0])
                elif re.match("\d*.*kb.*s", seg):
                    #bitrate found. assume we want the same bitrate
                    settings.bitrate = int(seg[:seg.index(" ")])
    return settings

def ffmpeg_error_check(parsestring):
    parse = parsestring.split('\n')
    for num, line in enumerate(parse):
        if "Unknown format" in line or "error occur" in line:
            raise RuntimeError("en-ffmpeg conversion error:\n\t" + "\n\t".join(parse[num:]))

