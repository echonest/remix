package com.ryanberdeen.utils {
  import com.adobe.crypto.MD5Stream;

  import flash.events.Event;
  import flash.events.EventDispatcher;
  import flash.events.ProgressEvent;
  import flash.utils.ByteArray;
  import flash.utils.Timer;

  public class MD5Calculator extends EventDispatcher {
    private var timer:Timer;
    private var stream:MD5Stream;
    private var buffer:ByteArray;
    private var source:ByteArray;

    private var _md5:String;
    private var _delay:int;
    private var _chunkSize:int;

    private var dispatchProgressEvent:Boolean;

    public function MD5Calculator() {
      _delay = 1;
      _chunkSize = 51200;
    }

    public function set delay(delay:int):void {
      _delay = delay;
    }

    public function set chunkSize(chunkSize:int):void {
      _chunkSize = chunkSize;
    }

    public function get md5():String {
      return _md5;
    }

    public function calculate(source:ByteArray):void {
      this.source = source;

      dispatchProgressEvent = hasEventListener(ProgressEvent.PROGRESS);

      stream = new MD5Stream();
      buffer = new ByteArray();

      source.position = 0;

      timer = new Timer(_delay);;
      timer.addEventListener('timer', iterate);
      timer.start();
    }

    private function iterate(e:Event):void {
      if (source.bytesAvailable == 0) {
        timer.stop();
        timer = null;
        _md5 = stream.complete();
        stream = null;
        buffer = null;
        source = null;
        dispatchEvent(new Event(Event.COMPLETE));
        return;
      }

      var length:int = Math.min(_chunkSize, source.bytesAvailable);
      buffer.length = length;
      source.readBytes(buffer, 0, length);
      stream.update(buffer);

      if (dispatchProgressEvent) {
        var progressEvent:ProgressEvent = new ProgressEvent(ProgressEvent.PROGRESS);
        progressEvent.bytesLoaded = source.position;
        progressEvent.bytesTotal = source.length
        dispatchEvent(progressEvent);
      }
    }

    public function stop():void {
      timer.stop();
    }
  }
}
