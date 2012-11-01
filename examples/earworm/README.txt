== earworm.py ==

earworm.py allows to seamlessly extend and shrink the length of a song without affecting its tempo, by jumping strategically backward or forward into it. It is based on a graph representation of beat-synchronous pattern self-similarities, i.e., "close-enough" structural repetitions. The algorithm is tuned to:

- minimize the numbers of "loops"
- never loop twice in the same exact location
- end up as close as possible to the requested duration without any time-stretching or cropping
- take into account timbre and pitch similarities
- smooth transparent jumps and transitions
- efficient graph representation useful for structure visualization, and other song manipulations
- also find and construct loops of arbitrary lengths for infinite looping

It is up to the developer to modify the algorithm and choose alternative default parameters for other use cases.


== Usage ==

Usage: earworm.py [options] <one_single_mp3>

Options:
  -h, --help            show this help message and exit
  -d DURATION, --duration=DURATION
                        target duration (argument in seconds) default=600
  -m MINIMUM, --minimum=MINIMUM
                        minimal loop size (in beats) default=8
  -i, --infinite        generate an infinite loop (wav file)
  -l, --length          length must be accurate
  -k, --pickle          output graph as a pickle object
  -g, --graph           output graph as a gml text file
  -p, --plot            output graph as png image
  -f, --force           force (re)computing the graph
  -S, --shortest        output the shortest loop (wav file)
  -L, --longest         output the longest loop (wav file)
  -v, --verbose         show results on screen


== Examples ==

After installing your Echo Nest API Key, you can try the script in the terminal, e.g.:
$ python earworm.py ../music/BillieJean.mp3
generates a 600 second (default) version of Billie Jean called BillieJean_600.mp3

Option -d allows you to request the length:
$ python earworm.py -d 1200 ../music/BillieJean.mp3
generates a close to 20 min long version of Billie Jean: 20 min and 883 milliseconds to be exact.

By adding the option -l:
$ python earworm.py -d 1200 -l ../music/BillieJean.mp3
you get the exact 20 min long version of Billie Jean! What happens is that a fade out is started early in order to finish at 20 min worth of audio samples precisely.

The option -m takes an integer parameter: the minimum number of beats, e.g.:
$ python earworm.py -d 1200 -l -m 16 ../music/BillieJean.mp3
to eliminate jumps that are shorter than 16 beats in length. That allows to avoid immediate typically more noticeable repetitions. Default is 8 beats.

Note that if you request a short duration, e.g. 30 seconds:
$ python earworm.py -d 30 ../music/BillieJean.mp3
the representation may not allow for such a short path from beginning to end, and will output the shortest path found, given the constraints.

Use the option -v to visualize where jumps are created:
$ python earworm.py -v ../music/BillieJean.mp3
outputs the following pointers, showing time of action, action name, time parameters, duration, and title:

00:00	  Playback	0.000	-> 99.824	 (99.824)	Billie Jean
01:39	  Jump		99.824	-> 92.117	 (0.515)	Billie Jean
01:40	  Playback	92.117	-> 139.847	 (47.730)	Billie Jean
02:28	  Jump		139.847	-> 33.586	 (0.512)	Billie Jean
02:28	  Playback	33.586	-> 251.584	 (217.998)	Billie Jean
06:06	  Jump		251.584	-> 243.896	 (0.510)	Billie Jean
06:07	  Playback	243.896	-> 271.556	 (27.660)	Billie Jean
06:34	  Jump		271.556	-> 87.510	 (0.516)	Billie Jean
06:35	  Playback	87.510	-> 294.452	 (206.941)	Billie Jean

along with a long list of links from a beat marker, to other beat offsets:

0 [4, 120]
1 [4, 88]
2 [4]
3 [4]
4 [88, 4]
5 [88]
...
527 [-8, -168, -72, -360]
528 [-8, -168, -360]
529 [-8, -360, -168]
530 [-8]
531 [-8, -80]
532 [-8, -80]

In this case, beat 0 is structurally similar to 4 beats and 120 beats forward. Beat 532 is similar to 8 beats and 80 beats earlier.

You can cache the graph representation that may take time to compute, with option -k:
$ python earworm.py -k ../music/BillieJean.mp3
That'll save a graph pickle file called BillieJean.mp3.graph.gpkl which will be loaded the next time you call this song.

The infinite option -i outputs a loopable wav file (for sample precision) rather than an mp3:
$ python earworm.py -i ../music/BillieJean.mp3
generates a close to 600 second long "loop" called BillieJean_600_loop.wav that may be heard from a player with proper "loop mode" capabilities for infinite seamless playing. For that reason, the file doesn't start at the very beginning or finish at the very end of the original file.

For convenience, the shortest or longest single loops can be generated respectively via -S and -L
$ python earworm.py -S ../music/BillieJean.mp3
makes an 8 second loopable file called BillieJean_8_shortest.mp3, and
$ python earworm.py -L ../music/BillieJean.mp3
makes an 184 second loopable file BillieJean_184_longest.mp3

It is possible to combine -m and -S to find the shortest loop with at least -m beats, e.g.,
$ python earworm.py -S -m 32 ../music/BillieJean.mp3
makes a single loop of 16 seconds (32 beats of about 500 ms) BillieJean_16_shortest.mp3

