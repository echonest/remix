package com.ryanberdeen.soundtouch {
  import com.ryanberdeen.audio.ISampleSource;
  import flash.media.Sound;
  import flash.utils.ByteArray;
  public class StretchSS implements ISampleSource {
    private var stretch:Stretch;
    public function StretchSS(sound:Sound, tempo:Number):void {
      stretch = new Stretch();
      //stretch.setParameters(44100, 30, 75, Stretch.DEFAULT_OVERLAP_MS);
      stretch.sound = sound;
      stretch.tempo = tempo;
    }
    
    public function set tempo(tempo:int):void {
      stretch.tempo = tempo;
    }
    
    public function extract(target:ByteArray, length:Number, startPosition:Number = -1):Number {
      return stretch.process(target);
    }

    public function toSourcePosition(position:Number):Number {
      return -1;
    }
    
    public function get length():Number {
      return -1;
    }
  }
}
