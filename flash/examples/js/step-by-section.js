// see step-by-section.py,
// Originally by Adam Lindsay, 2009-03-10.

function remix(analysis) {
    
    function areBeatNumber(beat) {
        return function(x) {
            return x.localContext()[0] == beat;
        };
    }

    var choices = 4;

    var meter = analysis.timeSignature.value;
    var fadeIn = analysis.endOfFadeIn;
    var fadeOut = analysis.startOfFadeOut;
    var sections = analysis.sections.that(overlapRange(fadeIn, fadeOut));
    var outchunks = [];

    for (var i = 0; i < sections.length; i++) {
        console.log(i);
        var section = sections[i];
        var beats = analysis.beats.that(areContainedBy(section));
        var segments = analysis.segments.that(overlap(section));
        var numBars = section.children().length;

        if (beats.length < meter) {
            continue;
        }

        var b = [];
        var segstarts = [];
        for (var m = 0; m < meter; m++) {
            b.push(beats.that(areBeatNumber(m)))
            segstarts.push(segments.that(overlapStartsOf(b[m])))
        }

        if (b.length == 0) {
            continue;
        }
        else if (b[0].length == 0) {
            continue;
        }

        var now = b[0][0];

        for (var x = 0; x < numBars * meter; x++) {
            var beat = x % meter;
            var nextBeat = (x + 1) % meter
            var nowEndSegment = segments.that(containPoint(now.end))[0]
            var nextCandidates = segstarts[nextBeat].orderedBy(timbreDistanceFrom(nowEndSegment))
            if (nextCandidates.length == 0) {
                continue;
            }
            var nextChoice = nextCandidates[Math.floor(Math.random() * (Math.min(choices, nextCandidates.length)))];
            var next = b[nextBeat].that(startDuring(nextChoice))[0];
            outchunks.push(now);
            now = next
        }
    }

    return outchunks;
}
