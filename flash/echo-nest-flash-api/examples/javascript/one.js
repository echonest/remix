function remix (analysis) {
  var bars = analysis.bars;
  var beats = analysis.beats;
  var beatIndex = 0;
  var samples = [];

  for (var i = 0; i < bars.length; i++) {
    while (beatIndex < beats.length - 1 &&
           beats[beatIndex].value != bars[i].value) {
      beatIndex++;
    }

    samples.push(
      beats[beatIndex].value,
      beats[beatIndex + 1].value
    );
  }

  return samples;
}
