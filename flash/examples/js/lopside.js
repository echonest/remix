// see lopside.py,
// Originally by Adam Lindsay, 2009-01-19.

function remix (analysis) {
    var bars = analysis.bars;
    var result = [];
    var tatums = false;

    for (var i = 0; i < bars.length; i++) {
        var children = bars[i].children();
        result.push.apply(result, children.slice(0, children.length - 1));
        if (tatums) {
            var lastTatums = children[children.length - 1].children();
            result.push.apply(result, lastTatums.slice(0, Math.floor(lastTatums.length / 2)));
        }
    }

    return result;
}
