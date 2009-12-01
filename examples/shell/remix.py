#!/usr/bin/env python
# encoding: utf-8
"""
shell.py

Created by Adam on 2009-11-22.
Copyright (c) 2009 . All rights reserved.
"""

import sys
import cmd
import os.path
import subprocess
import tempfile
import glob
import types
from optparse import OptionParser

from echonest.audio import *
from echonest.audio import AudioQuantumList as aql
from echonest.audio import AudioQuantum as aq
from echonest.selection import *
from echonest.sorting import *


USAGE = '''
%prog [options] [filename]

Optional filename pre-loads the file.
'''

def main(argv=None):
    if argv is None:
        argv = sys.argv
    parser = OptionParser(usage=USAGE)
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="try to suppress messages")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose")
    
    (options, args) = parser.parse_args()
    
    r = Remix()
    r.options = options
    r.args = args
    r.cmdloop()

class Remix(cmd.Cmd):
    """Loop while keeping track of the last thing."""
    
    prompt = "(no file) > "
    currfile = None
    currfilename = ""
    cwd = ""
    env = dict()
    renderable = None
    renderablename = ""
    options = dict()
    args = list()
    
    def do_EOF(self, line):
        return True
    
    def preloop(self):
        if self.args:
            self.do_load(self.args[0])
        self.cwd  = os.getcwd()
    
    def postloop(self):
        print
    
    def default(self, line):
        """execute a command"""
        self.execute(line)
    
    def do_play(self, line):
        """plays the current buffer or a given filename"""
        if not line:
            if self.renderable and not self.renderablename:
                foo, line = tempfile.mkstemp(".wav")
                self.renderablename = line
                self.renderable.encode(self.renderablename)
            elif self.renderablename:
                line = self.renderablename
        if not line:
            print "nothing to play"
            return
        CMD = ["qlmanage", '-p', line]
        pid=subprocess.Popen(CMD, stderr=subprocess.PIPE).pid
        
    def do_load(self, path):
        """loads the requested file (or directory)"""
        if os.path.isdir(path):
            self.cwd = os.path.abspath(path)
            os.chdir(self.cwd)
        else:
            try:
                self.currfile = LocalAudioFile(path, verbose=self.options.verbose)
            except:
                print "unable to load %s" % path
                return
            self.currfilename = os.path.abspath(path)
            self.prompt = "%s > " % os.path.basename(self.currfilename)
            self.renderable = self.currfile
            self.renderablename = self.currfilename
            self.env['segments'] = self.currfile.analysis.segments
            self.env['sections'] = self.currfile.analysis.sections
            self.env['beats'] = self.currfile.analysis.beats
            self.env['bars'] = self.currfile.analysis.bars
            self.env['tatums'] = self.currfile.analysis.tatums
            self.env['analysis'] = self.currfile.analysis
            self.env['_'] = None
    
    def complete_load(self, text, line, begidx, endidx):
        l = line.split(None, 1)[1]
        wav = [os.path.basename(f) for f in glob.glob("%s*.wav" % l)]
        mp3 = [os.path.basename(f) for f in glob.glob("%s*.mp3" % l)]
        dirs = [os.path.basename(d) + '/' for d in glob.glob("%s*" % l) if os.path.isdir(d)]
        return mp3 + wav + dirs
    
    def do_save(self, line):
        """saves to the designated filename in the current directory"""
        if not line:
            print "missing filename"
            return
        if not self.renderable:
            print "nothing to save"
        self.renderable.encode(line)
        print "saved as " + os.path.abspath(os.path.join(os.getcwd(), line))
    
    def execute(self, rawcmd):
        try:
            result = eval(rawcmd, globals(), self.env)
        except:
            print "syntax error"
            return
        if isinstance(result, tuple) or isinstance(result, dict) or isinstance(result, types.StringTypes):
            print result
            return
        try:
            if not isinstance(result, AudioRenderable):
                self.renderable = AudioQuantumList(result, source=self.currfile)
                self.renderable.attach(None)
            else:
                self.renderable = result
            self.renderablename = ""
            self.env['_'] = self.renderable
        except TypeError:
            print result


if __name__ == "__main__":
    sys.exit(main())
    # Remix().cmdloop()
