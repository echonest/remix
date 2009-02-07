#! /usr/bin/python

import sys

sys.path.insert(0, "build/lib.linux-ppc-2.3")

import mad, StringIO

data = StringIO.StringIO(open("foo.mp3","r").read())
m = mad.MadFile(data)
print "MadFile returned"
for x in (1,2): pass
print "got here"

