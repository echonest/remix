package com.ryanberdeen.audio {
  public class SampleRange {
    private var _start:Number;
    private var _end:Number;

    public function SampleRange(start:Number, end:Number):void {
      _start = start;
      _end = end;
    }

    public function get start():Number {
      return _start;
    }

    public function get end():Number {
      return _end;
    }

    public function get length():Number {
      return _end - _start;
    }
  }
}
