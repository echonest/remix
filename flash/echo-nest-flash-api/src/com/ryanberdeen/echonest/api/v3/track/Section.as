/*
 * Copyright 2009 Ryan Berdeen. All rights reserved.
 * Distributed under the terms of the MIT License.
 * See accompanying file LICENSE.txt
 */

package com.ryanberdeen.echonest.api.v3.track {
  /**
  * @see TrackApi#processSectionsResponse()
  * @see http://developer.echonest.com/docs/method/get_sections/
  */
  public class Section {
    private var _start:Number;
    private var _duration:Number;

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
  }
}
