/*
 * Copyright 2009 Ryan Berdeen. All rights reserved.
 * Distributed under the terms of the MIT License.
 * See accompanying file LICENSE.txt
 */

package com.ryanberdeen.echonest.api.v3.track {
  /**
  * @see TrackApi#processSegmentsResponse()
  * @see http://developer.echonest.com/docs/method/get_segments/
  */
  public class Segment {
    private var _start:Number;
    private var _duration:Number;
    private var _startLoudness:Number;
    private var _endLoudness:Number;
    private var _maxLoudness:Number;
    private var _maxLoudnessTimeOffset:Number;
    private var _pitches:Array;
    private var _timbre:Array;

    public function get start():Number {
      return _start;
    }

    public function set start(start:Number):void {
      _start = start;
    }

    public function get duration():Number {
      return _duration;
    }

    public function set duration(duration:Number):void {
      _duration = duration;
    }

    public function get startLoudness():Number {
      return _startLoudness;
    }

    public function set startLoudness(startLoudness:Number):void {
      _startLoudness = startLoudness;
    }

    public function get endLoudness():Number {
      return _endLoudness;
    }

    public function set endLoudness(endLoudness:Number):void {
      _endLoudness = endLoudness;
    }

    public function get maxLoudness():Number {
      return _maxLoudness;
    }

    public function set maxLoudness(maxLoudness:Number):void {
      _maxLoudness = maxLoudness;
    }

    public function get maxLoudnessTimeOffset():Number {
      return _maxLoudnessTimeOffset;
    }

    public function set maxLoudnessTimeOffset(maxLoudnessTimeOffset:Number):void {
      _maxLoudnessTimeOffset = maxLoudnessTimeOffset;
    }

    public function get pitches():Array {
      return _pitches;
    }

    public function set pitches(pitches:Array):void {
      _pitches = pitches;
    }

    public function get timbre():Array {
      return _timbre;
    }

    public function set timbre(timbre:Array):void {
      _timbre = timbre;
    }
  }
}
