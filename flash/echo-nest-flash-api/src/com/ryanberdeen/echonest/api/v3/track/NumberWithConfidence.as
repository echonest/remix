/*
 * Copyright 2009 Ryan Berdeen. All rights reserved.
 * Distributed under the terms of the MIT License.
 * See accompanying file LICENSE.txt
 */

package com.ryanberdeen.echonest.api.v3.track {
  /**
  * A number with an associated confidence value.
  */
  public class NumberWithConfidence {
    private var _value:Number;
    private var _confidence:Number;

    public function NumberWithConfidence(value:Number, confidence:Number):void {
      _value = value;
      _confidence = confidence;
    }

    public function get value():Number {
      return _value;
    }

    public function get confidence():Number {
      return _confidence;
    }

    public function toString():String {
      return value + ' (' + confidence + ')';
    }
  }
}
