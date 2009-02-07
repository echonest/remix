#!/usr/bin/env python

#
#   Copyright (c) 2001-2002 Alexander Leidinger. All rights reserved.
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions
#   are met:
#
#   1. Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#   2. Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#
#   THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
#   ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#   ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
#   FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#   DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
#   OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#   HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#   LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
#   OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
#

# $Id: gen_docs.py,v 1.1 2002/10/15 18:24:53 aleidinger Exp $

import lame

mp3 = lame.init()

print 'Contents:'
print ' - API reference (lame module)'
print ' - API reference (mp3 object)'
print ' - API description'
print
print 'API reference (lame module):'
for entity in dir(lame):
    print '  ' +  str(type(eval('lame.' + entity))) + '\tlame.' + entity
print
print 'API reference (mp3 object):'
for entity in dir(mp3):
    print '  ' +  str(type(eval('mp3.' + entity))) + '\tmp3.' + entity
print
print 'API description:'
help(lame)
for entity in dir(mp3):
    print 'mp3.' + entity + '(...)'
    print eval('mp3.' + entity + '.__doc__')
    print

