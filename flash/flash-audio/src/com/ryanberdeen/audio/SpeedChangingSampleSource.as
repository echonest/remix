/*
 * Copyright 2009 Ryan Berdeen. All rights reserved.
 * Distributed under the terms of the MIT License.
 * See accompanying file LICENSE.txt
 */

package com.ryanberdeen.audio {
  import flash.media.Sound;
  import flash.utils.ByteArray;

  /**
  * Varies the playback rate.
  **/
  public class SpeedChangingSampleSource implements ISampleSource {
    private var _sampleSource:ISampleSource;
    private var _playbackSpeed:Number = 1;
    private var _phase:Number = 0;

    public function set sampleSource(sampleSource:ISampleSource):void {
      _sampleSource = sampleSource;
    }

    /**
    * The speed at which to play back the samples.
    *
    * <p>If this value is changed while playing, <code>length</code> and
    * <code>toSourcePosition()</code> will be inaccurate</p>
    */
    public function set playbackSpeed(playbackSpeed:Number):void {
      if (playbackSpeed < 0) {
        throw new ArgumentError('Playback speed must be positive');
      }
      _playbackSpeed = playbackSpeed;
    }

    public function extract(target:ByteArray, length:Number, startPosition:Number = -1):Number {
      var p:int;

      var loadedSamples:ByteArray = new ByteArray();
      var sourceStartPosition:int = startPosition == -1 ? int(_phase) : startPosition * _playbackSpeed;

      _sampleSource.extract(loadedSamples, int(length * _playbackSpeed), sourceStartPosition);
      loadedSamples.position = 0;

      while (loadedSamples.bytesAvailable > 0) {
        p = int(_phase - sourceStartPosition) * 8;

        if (p < loadedSamples.length - 8 && target.length <= length * 8) {
          loadedSamples.position = p;

          target.writeBytes(loadedSamples, p, 8);
        }
        else {
          loadedSamples.position = loadedSamples.length;
        }

        _phase += _playbackSpeed;
      }

      return target.length / 8;
    }

    public function toSourcePosition(position:Number):Number {
      return _sampleSource.toSourcePosition(position * _playbackSpeed);
    }

    public function get length():Number {
      return _sampleSource.length * _playbackSpeed;
    }
  }
}
