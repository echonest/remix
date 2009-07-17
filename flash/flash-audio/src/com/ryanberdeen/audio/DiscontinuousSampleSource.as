/*
 * Copyright 2009 Ryan Berdeen. All rights reserved.
 * Distributed under the terms of the MIT License.
 * See accompanying file LICENSE.txt
 */

package com.ryanberdeen.audio {
  import flash.media.Sound;
  import flash.utils.ByteArray;

  /**
  * Provides samples based on an arbitrary list of sample ranges.
  */
  public class DiscontinuousSampleSource implements ISampleSource {
    private var _sampleSource:ISampleSource;
    private var _sampleRanges:Array;
    private var _length:Number;

    private var extractionRangeIndex:int;
    private var extractionRange:SampleRange;
    private var extractionPosition:Number;
    private var startPosition:Number;
    private var finished:Boolean;

    private var positionRangeIndex:int;
    private var localPosition:Number;

    private var linearPosition:Number;

    public function set sampleSource(sampleSource:ISampleSource):void {
      _sampleSource = sampleSource;
    }

    public function set sampleRanges(sampleRanges:Array):void {
      _sampleRanges = sampleRanges;

      extractionRangeIndex = 0;
      extractionRange = _sampleRanges[extractionRangeIndex];

      extractionPosition = extractionRange.start;

      startPosition = 0;

      linearPosition = 0;
      localPosition = extractionPosition;
      positionRangeIndex = 0;

      _length = 0;
      for each (var sampleRange:SampleRange in _sampleRanges) {
        _length += sampleRange.length;
      }
    }

    public function extract(target:ByteArray, length:Number, startPosition:Number = -1):Number {
      if (startPosition != -1) {
        if (startPosition != this.startPosition) {
          var newPosition:Array = seek(this.startPosition, startPosition, extractionPosition, extractionRangeIndex);
          extractionPosition = newPosition[0];
          extractionRangeIndex = newPosition[1];
          extractionRange = _sampleRanges[extractionRangeIndex];
        }
      }

      var samplesRead:int = 0;
      while (!finished && samplesRead < length) {
        var samplesLeft:int = extractionRange.end - extractionPosition;
        var samplesToRead:int = Math.min(samplesLeft, length - samplesRead);
        _sampleSource.extract(target, samplesToRead, extractionPosition);

        samplesRead += samplesToRead;
        extractionPosition += samplesToRead;
        if (extractionPosition == extractionRange.end) {
          extractionRangeIndex++;

          if (extractionRangeIndex == _sampleRanges.length) {
            finished = true;
          }
          else {
            extractionRange = _sampleRanges[extractionRangeIndex];
            extractionPosition = extractionRange.start;
          }
        }
      }

      this.startPosition = startPosition + samplesRead;
      return samplesRead;
    }

    public function toSourcePosition(position:Number):Number {
      var result:Array = seek(linearPosition, position, localPosition, positionRangeIndex);
      linearPosition = position;
      localPosition = result[0];
      positionRangeIndex = result[1];
      return result[0];
    }

    private function seek(linearStart:Number, linearEnd:Number, sourcePosition:Number, index:int):Array {
      if (linearEnd < linearStart) {
        // TODO might be faster to seek backwards and then seek forwards
        linearStart = 0;
        index = 0;
        sourcePosition = _sampleRanges[index].start;
      }

      var distance:Number = linearEnd - linearStart;

      var range:SampleRange;
      var distanceLeft:Number;
      var samplesLeftThisRange:Number;

      var samplesAdvanced:Number = 0;
      while (samplesAdvanced < distance) {
        range = _sampleRanges[index];
        samplesLeftThisRange = range.end - sourcePosition;
        distanceLeft = distance - samplesAdvanced;
        if (samplesLeftThisRange > distanceLeft) {
          sourcePosition += distanceLeft;
          samplesAdvanced += distanceLeft;
        }
        else {
          index++;
          if (index < _sampleRanges.length) {
            sourcePosition = _sampleRanges[index].start;
          }
          samplesAdvanced += samplesLeftThisRange;
        }
      }
      return [sourcePosition, index];
    }

    public function get length():Number {
      return _length;
    }

    public function get rangeIndex():int {
      return positionRangeIndex;
    }
  }
}
