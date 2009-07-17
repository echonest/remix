/*
 * Copyright 2009 Ryan Berdeen. All rights reserved.
 * Distributed under the terms of the MIT License.
 * See accompanying file LICENSE.txt
 */

package com.ryanberdeen.audio {
  import flash.events.Event;
  import flash.events.EventDispatcher;
  import flash.events.SampleDataEvent;
  import flash.media.Sound;
  import flash.media.SoundChannel;
  import flash.utils.ByteArray;

  public class SampleSourcePlayer extends EventDispatcher {
    private static const SAMPLE_BUFFER_SIZE:int = 8192;
    private var _sampleSource:ISampleSource;
    private var outputSound:Sound;
    private var soundChannel:SoundChannel;
    private var playing:Boolean;

    public function SampleSourcePlayer():void {
      outputSound = new Sound();

      outputSound.addEventListener(SampleDataEvent.SAMPLE_DATA, function(e:SampleDataEvent):void {
        _sampleSource.extract(e.data, SAMPLE_BUFFER_SIZE);
      });
    }

    public function set sampleSource(sampleSource:ISampleSource):void {
      _sampleSource = sampleSource;
    }

    public function start():void {
      if (soundChannel != null) {
        soundChannel.removeEventListener(Event.SOUND_COMPLETE, soundCompleteHandler);
      }

      soundChannel = outputSound.play();
      soundChannel.addEventListener(Event.SOUND_COMPLETE, soundCompleteHandler);
      playing = true;
    }

    public function stop():void {
      if (playing) {
        soundChannel.stop();
        playing = false;
      }
    }

    public function get position():Number {
      return Math.floor(soundChannel.position * 44.1);
    }

    public function get sourcePosition():Number {
      return _sampleSource.toSourcePosition(position);
    }

    public function get sourceLength():Number {
      return _sampleSource.length;
    }

    private function soundCompleteHandler(e:Event):void {
      dispatchEvent(new Event(Event.SOUND_COMPLETE));
    }
  }
}
