#! /usr/bin/env python

import sys, os.path

sys.path.insert(0, "build/lib.linux-ppc-2.3")

import socket, urlparse
import mad, ao

def madradio(url):
    scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
    try:
        host, port = netloc.split(':')
    except ValueError:
        host, port = netloc, 80
    if not path:
        path = '/'
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, int(port)))
    sock.send('GET %s HTTP/1.0\r\n\r\n' % path)
    reply = sock.recv(1500)
    #print repr(reply)
    file = sock.makefile()
    mf = mad.MadFile(file)
    print "bitrate %lu bps" % mf.bitrate()
    print "samplerate %d Hz" % mf.samplerate()
    dev = ao.AudioDevice('oss', bits=16, rate=mf.samplerate())
    while True:
        buffy = mf.read()
        if buffy is None:
            break
        dev.play(buffy, len(buffy))

if __name__ == '__main__':
    import sys
    try:
        url = sys.argv[1]
    except IndexError:
        #url = 'http://62.67.195.6:8000' # lounge-radio.com
        url = 'http://63.241.4.18:8069' # xtcradio.com
    madradio(url)
