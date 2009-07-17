/*
 * Copyright 2009 Ryan Berdeen. All rights reserved.
 * Distributed under the terms of the MIT License.
 * See accompanying file LICENSE.txt
 */

package com.ryanberdeen.audio {
  import flash.utils.ByteArray;

  /**
  * An abstraction over the <code>Sound.extract()</code> method.
  */
  public interface ISampleSource {
    function extract(target:ByteArray, length:Number, startPosition:Number = -1):Number;

    /**
    * Converts a linear sample offset to a source sample offset.
    */
    function toSourcePosition(position:Number):Number;

    /**
    * The number of samples in the source.
    */
    function get length():Number;
  }
}
