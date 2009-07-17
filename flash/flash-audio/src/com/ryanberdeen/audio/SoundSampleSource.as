/*
 * Copyright 2009 Ryan Berdeen. All rights reserved.
 * Distributed under the terms of the MIT License.
 * See accompanying file LICENSE.txt
 */

package com.ryanberdeen.audio {
  import flash.media.Sound;
  import flash.utils.ByteArray;

  /**
  * <code>ISampleSource</code> that provides samples unaltered from a
  * <code>Sound</code>.
  */
  public class SoundSampleSource implements ISampleSource {
    private var sound:Sound;
    private var startPosition:Number;
    private var _length:Number;

    public function SoundSampleSource(sound:Sound):void {
      this.sound = sound;
      startPosition = 0;
      _length = Math.ceil(sound.length * 44.1);
    }

    public function extract(target:ByteArray, length:Number, startPosition:Number = -1):Number {
      if (startPosition == -1) {
        startPosition = this.startPosition;
      }
      var result:Number = sound.extract(target, length, startPosition);
      this.startPosition = startPosition + length;
      return result;
    }

    public function toSourcePosition(position:Number):Number {
      return position;
    }

    public function get length():Number {
      return _length;
    }
  }
}
