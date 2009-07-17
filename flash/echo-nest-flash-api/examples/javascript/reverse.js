function remix (analysis) {
  var beats = analysis.beats;
  var samples = [];
  for (var i = beats.length - 1; i > 0; i--) {
    samples.push(beats[i - 1].value, beats[i].value);
  }

  return samples;
}
