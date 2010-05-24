#!/usr/bin/env python
# encoding: utf=8
"""
slowpoke.py

Find a track that is going under the speed limit, and speed it up. 
Chooses the most familiar track it can see. Gotta go after those high-profile offenders.
This hints at some of the more advanced song search capabilities.

Go to http://beta.developer.echonest.com/song.html to see what else is possible.

by Jason Sundram, 2010-04-15.
"""
import sys
from echonest import cloud
from echonest.modify import Modify
from beta_pyechonest import song

usage = """
Usage: 
    python slowpoke.py catalog speed_limit <output_filename>
Example:
    python slowpoke.py CATALOG_NAME 55 sped_up.mp3
"""

def main(catalog, speed_limit, output_filename):
    if (speed_limit < 10):
        raise Exception("You must be in a school zone; no speedup is possible")
    
    songs = song.search(min_tempo=speed_limit-10, max_tempo=speed_limit, sort='familiarity-desc')
    if not songs:
        raise Exception("No slowpokes on the road today. Nothing to do!")
    
    track = None
    songs.reverse()
    while not track and songs:
        track = cloud.make_track(songs.pop(), catalog)
    
    if not track:
        raise Exception("Couldn't get data for any of the slowpokes. Sorry!")
    
    # Do the speedup
    st = Modify()
    faster = st.shiftTempo(track, speed_limit / track.analysis.tempo['value'])
    faster.encode(output_filename)

if __name__ == '__main__':
    try:
        catalog = sys.argv[1]
        speed_limit = int(sys.argv[2])
        output_filename = sys.argv[3]
    except:
        sys.exit(usage)
    
    main(catalog, speed_limit, output_filename)