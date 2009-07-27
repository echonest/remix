/**
* Selection filters.
*
* The functions in this module each return *another* function that takes
* one argument, an `AudioQuantum`, and returns an `AudioQuantum` or `false`.
*
* By convention, all of these functions are named to be verb phrases that
* agree with a plural noun in a restrictive clause introduced by `that`,
* as in::
*
*     analysis.segments.that(fallOnThe(1))
*/
var selection = {
    /**
    * Returns a function that tests if its input `AudioQuantum` lies
    * between the *start* and *end* parameters.
    */
    areContainedByRange: function(start, end) {
        return function(x) {
            return x.start >= start && x.end <= end;
        };
    },

    /**
    * Returns a function that tests if its input `AudioQuantum` lies
    * within the interval of the parameter *aq* `AudioQuantum`,
    */
    areContainedBy: function(aq) {
        return function(x) {
            return x.start >= aq.start && x.end <= aq.end;
        };
    },

    /**
    * Returns a function that tests if its input `AudioQuantum` overlaps
    * in any way the interval between the parameters *start* and *end*.
    */
    overlapRange: function(start, end) {
        return function(x) {
            return x.end > start && x.start < end;
        };
    },

    /**
    * Returns a function that tests if its input `AudioQuantum` overlaps
    * in any way the parameter *aq* `AudioQuantum`.
    */
    overlap: function(aq) {
        return function(x) {
            return x.end > aq.start && x.start < aq.end;
        };
    },


    /**
    * Returns a function that tests if its input `AudioQuantum`\'s `end`
    * lies in the interval between the parameters *start* and *end*.
    */
    endDuringRange: function(start, end) {
        return function(x) {
            return x.end > start && x.end <= end;
        };
    },

    /**
    * Returns a function that tests if its input `AudioQuantum`\'s `end`
    * lies anywhere during the parameter *aq* `AudioQuantum`.
    */
    endDuring: function(aq) {
        return function(x) {
            return x.end > aq.start && x.end <= aq.end;
        };
    },

    /**
    * Returns a function that tests if its input `AudioQuantum`\'s `start`
    * lies in the interval between the parameters *start* and *end*.
    */
    startDuringRange: function(start, end) {
        return function(x) {
            return x.start >= start && x.start < end;
        };
    },

    /**
    * Returns a function that tests if its input `AudioQuantum`\'s `start`
    * lies anywhere during the parameter *aq* `AudioQuantum`.
    */
    startDuring: function(aq) {
        return function(x) {
            return x.start >= aq.start && x.start < aq.end;
        };
    },

    /**
    * Returns a function that tests if its input `AudioQuantum` contains
    * the input parameter *point*, a time offset, in seconds.
    */
    containPoint: function(point) {
        return function(x) {
            return point > x.start && point < x.end;
        };
    },

    /**
    * Returns a function that tests if its input `AudioQuantum` has
    * a `pitch`\[*pitchmax*] such that it is greater or equal to all
    * other values in its `pitch` vector.
    */
    havePitchMax: function(pitchmax) {
        return function(x) {
            return selection._isMaxPitch(pitchmax, x.pitches);
        };
    },

    /**
    * Returns a function that tests if its input `AudioQuantum` has
    * a maximum `pitch`\[*p*] such that it is greater or equal to all
    * other values in its `pitch` vector, and *p* is in `List` parameter
    * *pitchesmax*.
    */
    havePitchesMax: function(pitchesmax) {
        return function(x) {
            var pitches = x.pitches;
            for (var i = 0; i < pitchesmax.length; i++) {
                if (selection._isMaxPitch(pitchesmax[i], x.pitches)) {
                    return true;
                }
            }
            return false;
        };
    },

    /**
    * Returns a function that tests if its input `AudioQuantum` lies
    * immediately before the parameter *aq* `AudioQuantum`. That is,
    * if the tested `AudioQuantum`\'s `end` == *aq*.start .
    */
    lieImmediatelyBefore: function(aq) {
        return function(x) {
            return x.end == aq.start;
        };
    },

    /**
    * Returns a function that tests if its input `AudioQuantum` lies
    * immediately after the parameter *aq* `AudioQuantum`. That is,
    * if the tested `AudioQuantum`\'s `start` == *aq*.end .
    */
    lieImmediatelyAfter: function(aq) {
        return function(x) {
            return x.start == aq.end;
        };
    },

    /**
    * Returns a function that tests if its input `AudioQuantum` has
    * a (one-indexed) ordinality within its `group`\() that is equal
    * to parameter *beatNumber*.
    */
    fallOnThe: function(beatNumber) {
        return function(x) {
            return x.localContext()[0] == (beatNumber - 1);
        };
    },

/* The following take AudioQuantumLists as input arguments: */

    /**
    * Returns a function that tests if its input `AudioQuantum` contains
    * the `end` of any of the parameter *aqs*, a `List` of
    * `AudioQuantum`\s.
    */
    overlapEndsOf: function(aqs) {
        return function(x) {
            for (var i = 0; i < aqs.length; i++) {
                var aq = aqs[i];
                if (x.start <= aq.end && x.end >= aq.end) {
                    return true;
                }
            }
            return false;
        };
    },

    /**
    * Returns a function that tests if its input `AudioQuantum` contains
    * the `start` of any of the parameter *aqs*, a `List` of
    * `AudioQuantum`\s.
    */
    overlapStartsOf: function(aqs) {
        return function(x) {
            for (var i = 0; i < aqs.length; i++) {
                var aq = aqs[i];
                if (x.start <= aq.start && x.end >= aq.start) {
                    return true;
                }
            }
            return false;
        };
    },

    /**
    * Returns a function that tests if its input `AudioQuantum` has
    * its `start` lie in any of the parameter *aqs*, a `List` of
    * `AudioQuantum`\s.
    */
    startDuringAny: function(aqs) {
        return function(x) {
            for (var i = 0; i < aqs.length; i++) {
                var aq = aqs[i];
                if (aq.start <= x.start && aq.end >= aq.start) {
                    return true;
                }
            }
            return false;
        };
    },

    _isMaxPitch: function(pitchmax, pitches) {
        var max = pitches[pitchmax];
        for (var i = 0; i < pitches.length; i++) {
            if (pitches[i] > max) {
                return false;
            }
        }
        return true;
    }
};
