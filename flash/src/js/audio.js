function AudioAnalysis(analysis) {
    extend(this, analysis);

    var duration = this.metadata.duration;

    if (this.sections) {
        this.sections = AudioQuantumList.fromSections(this.sections);
        this.sections.analysis = this;
    }
    if (this.bars) {
        this.bars = AudioQuantumList.fromEvents('bar', this.bars, duration);
        this.bars.analysis = this;
    }
    if (this.beats) {
        this.beats = AudioQuantumList.fromEvents('beat', this.beats, duration);
        this.beats.analysis = this;
    }
    if (this.tatums) {
        this.tatums = AudioQuantumList.fromEvents('tatum', this.tatums, duration);
        this.tatums.analysis = this;
    }
    if (this.segments) {
        this.segments = AudioQuantumList.fromSegments(this.segments);
        this.segments.analysis = this;
    }
}

function AudioQuantum() {
    this.start = 0;
    this.end = 0;
    this.duration = 0;
}

extend(AudioQuantum.prototype, {
    setDuration: function(duration) {
        this.duration = duration;
        this.end = this.start + duration;
    },

    setEnd: function(end) {
        this.end = end;
        this.duration = this.end - this.start;
    },

    parent: function() {
        // TODO handle error
        var uppers = this.container.analysis[AudioQuantum.parentAttributes[this.container.kind]];
        return uppers.that(selection.overlap(this))[0];
    },

    children: function() {
        // TODO handle error
        var downers = this.container.analysis[AudioQuantum.childrenAttributes[this.container.kind]];
        return downers.that(selection.areContainedBy(this));
    },

    group: function() {
        var parent = this.parent();
        if (parent) {
            return parent.children();
        }
        else {
            return this.container;
        }
    },

    localContext: function() {
        var group = this.group();
        return [group.indexOf(this), group.length];
    }
});

extend(AudioQuantum, {
    parentAttributes: {
        bar: 'sections',
        beat: 'bars',
        tatum: 'beats'
    },

    childrenAttributes: {
        section: 'bars',
        bar: 'beats',
        beat: 'tatums'
    }
});

function AudioQuantumList(kind) {
    var array = extend([], AudioQuantumList.Methods);
    array.kind = kind;
    return array;
}

AudioQuantumList.Methods = {
    that: function(filter) {
        var result = new AudioQuantumList(this.kind);

        for (var i = 0; i < this.length; i++) {
            var aq = this[i];
            if (filter(aq)) {
                result.push(aq);
            }
        }
        return result;
    },

    orderedBy: function(fn, descending) {
        var result = new AudioQuantumList(this.kind);
        result.push.apply(result, this);
        result.sort(function(a, b) {
            var aa = fn(a);
            var bb = fn(b);
            if (aa > bb) {
                return 1;
            }
            if (aa < bb) {
                return -1;
            }
            return 0;
        });
        // TODO
        if (descending) {
            result.reverse();
        }
        return result;
    }
};

extend(AudioQuantumList, {
    fromEvents: function(kind, events, duration) {
        var aqs = new AudioQuantumList(kind);

        var previousAq = new AudioQuantum();
        previousAq.start = 0;
        for (var i = 0; i < events.length; i++) {
            var event = events[i];
            var aq = new AudioQuantum();

            aq.start = aq.value = event.value;
            aq.confidence = event.confidence;
            aq.container = aqs;
            aqs.push(aq);

            previousAq.setEnd(aq.start);
            previousAq = aq;
        }
        // TODO audio.py duplicates the duration of the second-to-last event
        previousAq.setEnd(duration);
        return aqs;
    },

    fromSections: function(sections) {
        var aqs = new AudioQuantumList('section');
        for (var i = 0; i < sections.length; i++) {
            var section = sections[i];
            var aq = new AudioQuantum();

            aq.start = section.start;
            aq.setDuration(section.duration);
            aq.container = aqs;
            aqs.push(aq);
        }
        return aqs;
    },

    fromSegments: function(segments) {
        var aqs = new AudioQuantumList('segment');
        for (var i = 0; i < segments.length; i++) {
            var segment = segments[i];
            var aq = new AudioQuantum();

            aq.start = aq.value = segment.start;
            aq.setDuration(segment.duration);
            aq.pitches = segment.pitches;
            aq.timbre = segment.timbre;
            aq.loudnessBegin = segment.startLoudness;
            aq.loudnessMax = segment.maxLoudness;
            aq.timeLoudnessMax = segment.maxLoudnessTimeOffset;
            aq.loudnessEnd = segment.endLoudness;
            aq.container = aqs;
            aqs.push(aq);
        }
        return aqs;
    }
});
