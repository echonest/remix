// see reverse.py

function remix (analysis) {
    var chunks = analysis.beats;
    var result = [];

    for (var i = 0; i < chunks.length; i++) {
        result.unshift(chunks[i]);
    }

    return result;
}
