// from Paul's Infinite Jukebox source.  I would like to extract things out of this
// First, it'd be nice to just do good old one
// upload a track, do the remix, play using webaudio, offer a dl link
// Even simpler:  static track on the server, do the remix live with webaudio
// so first I need webaudio to work

function createJRemixer(context, apiKey, jquery) {
    var baseUri = 'http://developer.echonest.com/api/v4/';
    var $ = jquery;


    var remixer = {

        searchTrack: function( artist, title, callback) {
            var url = "http://localhost:8383/TrackServer/search?callback=?";
            $.getJSON(url, { artist: artist, title:title}, function(data) {
                callback(data);
            });
        },


        fetchSound : function(audioURL, callback) {
            var request = new XMLHttpRequest();

            trace("fetchSound " + audioURL);
            request.open("GET", audioURL, true);
            request.responseType = "arraybuffer";
            this.request = request;

            request.onload = function() {
                var buffer = context.createBuffer(request.response, false);
                callback(true, buffer);
            }

            request.onerror = function(e) {
                callback(false, null);
            }
            request.send();
        },


        fetchAnalyzedTrack : function( trackID, audioURL, callback) {
            var track = {
                id : trackID,
                audio: audioURL,
                status : null,
                info : null,
                analysis : null,
                buffer : null,
            };

            function fetchTrackInfo(trackID) {
                var request = new XMLHttpRequest();

                trace("fetchTrackInfo " + trackID);
                request.open('GET', baseUri + 'track/profile?api_key=' 
                    + apiKey + '&format=json&id=' + trackID 
                    + '&bucket=audio_summary&callback=' + new Date().getTime());

                var that = this;
                request.onload = function (e) {
                    var result = JSON.parse(request.responseText);
                    track.info = result.response.track
                    fetchAnalysis(track.info.audio_summary.analysis_url);
                };

                request.onerror = function (e) {
                    checkReady(false, "fetching track info");
                }
                request.send();
            }


            function fetchTrackInfoFromTrackServer(trackID) {
                if (typeof trackID === 'string') {
                    var url = "http://localhost:8383/TrackServer/info?callback=?";
                    $.getJSON(url, { trid: trackID}, function(data) {
                        if (data.status === 'ok') {
                            track.info = data.info;
                            track.analysis = data.analysis;
                            checkReady(true, "fetchTrackInfoFromTrackServer");
                        }
                        else {
                            checkReady(false, "fetchTrackInfoFromTrackServer");
                        }
                    });
                } else {
                    track.info = {};
                    track.analysis = trackID;
                    checkReady(true, "fetchPreanalyzedTrackInfoFromTrackServer");
                }
            }

            function fetchAnalysis(url, callback) {
                var url = track.id + ".js";
                var request = new XMLHttpRequest();
                request.open('GET', url);
                request.onload = function (e) {
                    track.analysis = JSON.parse(request.responseText);
                    checkReady(true, "fetchAnalysis2 " + url);
                }
                request.onerror = function (e) {
                    checkReady(false, "fetching analysis");
                }
                request.send();
            }

            function fetchAudio(url) {
                var request = new XMLHttpRequest();

                trace("fetchAudio " + url);
                request.open("GET", url, true);
                request.responseType = "arraybuffer";
                this.request = request;

                request.onload = function() {
                    track.buffer = context.createBuffer(request.response, false);
                    checkReady(true, "fetching audio");
                }

                request.onerror = function(e) {
                    checkReady(false, "fetching Audio");
                }
                request.send();
            }


            function checkReady(ok, txt) {

                trace("checkReady " + ok + " " + txt);
                if (track.status != null) {
                    return;
                }

                if (!ok) {
                    track.status = 'error: ' + txt;
                    callback(track);
                }

                if (track.info != null && track.analysis != null && track.buffer != null) {
                    track.status = 'ok';
                    preprocessTrack(track);
                    callback(track);
                }
            }


            function preprocessTrack(track) {
                trace('preprocessTrack');
                var types = ['sections', 'bars', 'beats', 'tatums', 'segments'];

                
                for (var i in types) {
                    var type = types[i];
                    trace('preprocessTrack ' + type);
                    for (var j in track.analysis[type]) {
                        var qlist = track.analysis[type]

                        j = parseInt(j)

                        var q = qlist[j]
                        q.track = track;
                        q.which = j;
                        if (j > 0) {
                            q.prev = qlist[j-1];
                        } else {
                            q.prev = null
                        }
                        
                        if (j < qlist.length - 1) {
                            q.next = qlist[j+1];
                        } else {
                            q.next = null
                        }
                    }
                }

                connectQuanta(track, 'sections', 'bars');
                connectQuanta(track, 'bars', 'beats');
                connectQuanta(track, 'beats', 'tatums');
                connectQuanta(track, 'tatums', 'segments');

                connectFirstOverlappingSegment(track, 'bars');
                connectFirstOverlappingSegment(track, 'beats');
                connectFirstOverlappingSegment(track, 'tatums');

                connectAllOverlappingSegments(track, 'bars');
                connectAllOverlappingSegments(track, 'beats');
                connectAllOverlappingSegments(track, 'tatums');

                filterSegments(track);
            }

            function filterSegments(track) {
                var threshold = .3;
                var fsegs = [];
                fsegs.push(track.analysis.segments[0]);
                for (var i = 1; i < track.analysis.segments.length; i++) {
                    var seg = track.analysis.segments[i];
                    var last = fsegs[fsegs.length - 1];
                    if (isSimilar(seg, last) && seg.confidence < threshold) {
                        fsegs[fsegs.length -1].duration += seg.duration;
                    } else {
                        fsegs.push(seg);
                    }
                }
                track.analysis.fsegments = fsegs;
            }

            function isSimilar(seg1, seg2) {
                var threshold = 1;
                var distance = timbral_distance(seg1, seg2);
                return (distance < threshold);
            }

            function connectQuanta(track, parent, child) {
                var last = 0;
                var qparents = track.analysis[parent];
                var qchildren = track.analysis[child];

                for (var i in qparents) {
                    var qparent = qparents[i]
                    qparent.children = [];

                    for (var j = last; j < qchildren.length; j++) {
                        var qchild = qchildren[j];
                        qchild.indexInParent = 0;
                        if (qchild.start >= qparent.start 
                                    && qchild.start < qparent.start + qparent.duration) {
                            qchild.parent = qparent;
                            qchild.indexInParent = qparent.children.length;
                            qparent.children.push(qchild);
                            last = j;
                        } else if (qchild.start > qparent.start) {
                            break;
                        }
                    }
                }
            }

            // connects a quanta with the first overlapping segment
            function connectFirstOverlappingSegment(track, quanta_name) {
                var last = 0;
                var quanta = track.analysis[quanta_name];
                var segs = track.analysis.segments;

                for (var i = 0; i < quanta.length; i++) {
                    var q = quanta[i]

                    for (var j = last; j < segs.length; j++) {
                        var qseg = segs[j];
                        if (qseg.start >= q.start) {
                        //if (qseg.start <= q.start && (qseg.start + qseg.duration) > q.start) {
                            q.oseg = qseg;
                            last = j;
                            break
                        } 
                    }
                }
            }

            function connectAllOverlappingSegments(track, quanta_name) {
                var last = 0;
                var quanta = track.analysis[quanta_name];
                var segs = track.analysis.segments;

                for (var i = 0; i < quanta.length; i++) {
                    var q = quanta[i]
                    q.overlappingSegments = [];

                    for (var j = last; j < segs.length; j++) {
                        var qseg = segs[j];
                        // seg starts before quantum so no
                        if ((qseg.start + qseg.duration) < q.start) {
                            continue;
                        }
                        // seg starts after quantum so no
                        if (qseg.start > (q.start + q.duration)) {
                            break;
                        }
                        last = j;
                        q.overlappingSegments.push(qseg);
                    }
                }
            }

            fetchTrackInfoFromTrackServer(trackID);
            fetchAudio(audioURL);
        },

        getPlayer : function() {
            var queueTime = 0;
            var audioGain = context.createGainNode();
            audioGain.gain.value = .9;
            audioGain.connect(context.destination);

            function queuePlay(when, q) {
                audioGain.gain.value = 1;
                if (isAudioBuffer(q)) {
                    var audioSource = context.createBufferSource();
                    audioSource.buffer = q;
                    audioSource.connect(audioGain);
                    audioSource.noteOn(when);
                    return when;
                } else if ($.isArray(q)) {
                    for (var i in q) {
                        when = queuePlay(when, q[i]);
                    }
                    return when;
                } else if (isQuantum(q)) {
                    q.audioSource = context.createBufferSource();
                    q.audioSource.buffer = q.track.buffer;
                    q.audioSource.connect(audioGain);
                    q.audioSource.noteGrainOn(when, q.start, q.duration);
                    return when + q.duration;
                } else {
                    error("can't play " + q);
                    return when;
                }
            }

            function error(s) {
                console.log(s);
            }

            var player = {
                play: function(q) {
                    queuePlay(0, q);
                },

                addCallback: function(callback) {
                },

                queue: function(q) {
                    var now = context.currentTime;
                    if (now > queueTime) {
                        queueTime = now;
                    } 
                    queueTime = queuePlay(queueTime, q);
                },

                queueRest: function(duration) {
                    queueTime += duration;
                },

                stop: function(q) {
                    if (q === undefined) {
                        audioGain.gain.value = 0;
                        audioGain.disconnect();
                    } else {
                        if ('audioSource' in q) {
                            if (q.audioSource != null) {
                                q.audioSource.noteOff(0);
                            }
                        }
                    }
                },

                curTime: function() {
                    return context.currentTime;
                }
            }
            return player;
        }
    };

    function isQuantum(a) {
        return 'start' in a && 'duration' in a;
    }

    function isAudioBuffer(a) {
        return 'getChannelData' in a;
    }

    function trace(text) {
        if (false) {
            console.log(text);
        }
    }

    return remixer;
}
