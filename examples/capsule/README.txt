== capsule.py ==

capsule.py beat matches parts of several songs into a single mp3. Given a transition duration, and an inter-transition duration, the program searches for the best order, the closest transition patterns, and apply beat alignment, time-stretching and crossfading into a single audio stream output. The result is a music collage with smooth transitions acting as the glue. Note that beat alignment is independent of downbeats during pattern search: it is optimal in the sense of timbral pattern matching, which may be perceptually tricky in the case of different styles. Therefore downbeats (first beat of the bar) don't necessarily align. Transitions can start anywhere in the track, and for any duration: it is up to the developer to apply additional constraints on top of the core engine of capsule to create less predictable and more interesting results. 

An earlier version of Capsule powers http://thisismyjam.com.


== Usage ==

Usage: capsule.py [options] <list of mp3s>

Options:
  -h, --help            show this help message and exit
  -t TRANSITION, --transition=TRANSITION
                        transition (in seconds) default=8
  -i INTER, --inter=INTER
                        section that's not transitioning (in seconds)
                        default=8
  -o, --order           automatically order tracks
  -e, --equalize        automatically adjust volumes
  -v, --verbose         show results on screen
  -p PDB, --pdb=PDB     dummy; here for not crashing when using nose


== Examples ==

After installing your Echo Nest API Key, try the following in your terminal:
$ python capsule.py ../music/BillieJean.mp3 ../music/EverythingIsOnTheOne.mp3
It'll combine into capsule.mp3, 8 seconds (default) of BillieJean.mp3 with 8 seconds of EverythingIsOnTheOne.mp3 via 8 seconds (default) of beat-matched transition.

To change the transition and inter transition paramaters use the options -t and -i, e.g.,
$ python capsule.py -t 4 -i 20 ../music/BillieJean.mp3 ../music/EverythingIsOnTheOne.mp3
makes a quicker 4-second transition with longer 20-second inter-transition excerpts of the tracks.
Note that every track that doesn't fit the parameter constraints will simply be rejected from the mix.

Option -o allows you to automatically order the tracks, currently by tempo:
$ python capsule.py -o ../music/BillieJean.mp3 ../music/EverythingIsOnTheOne.mp3
plays EverythingIsOnTheOne.mp3 first.

Option -v allows you to see details about what is going on during computation.
$ python capsule.py -o -v ../music/BillieJean.mp3 ../music/EverythingIsOnTheOne.mp3
displays the following time of action, action name, time parameters, duration, and title.

00:00	  Fade in	    100.421	-> 100.671	 (0.250)	Everything Is On The One
00:00	  Playback	    100.671	-> 108.671	 (8.000)	Everything Is On The One
00:08	  Crossmatch	108.671	-> 232.107	 (7.502)	Everything Is On The One -> Billie Jean
00:15	  Playback	    232.107	-> 240.297	 (8.190)	Billie Jean
00:23	  Fade out	    240.297	-> 246.297	 (6.000)	Billie Jean

Note that every capsule starts with a 250 ms quick fade in and ends with a 6-second fade out.

With option -e you can equalize the relative volume between tracks.
$ python capsule.py -o -e -v ../music/BillieJean.mp3 ../music/EverythingIsOnTheOne.mp3
pushes the gain of the first track by 33% and the second track by 10%

Vol = 133%	Everything Is On The One
Vol = 110%	Billie Jean
