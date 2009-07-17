package com.ryanberdeen.echonest.api.v3 {
  import flash.events.ErrorEvent;
  import flash.events.Event;

  public class EchoNestErrorEvent extends ErrorEvent {
    public static const ECHO_NEST_ERROR:String = "echoNestError";

    private var _code:int;
    private var _message:String;

    public function EchoNestErrorEvent(type:String, code:int, message:String) {
      super(type, bubbles, cancelable, (code + ': ' + message));
      _code = code;
      _message = message;
    }

    public function get code():int {
      return _code;
    }

    public function get message():String {
      return _message;
    }

    override public function clone():Event {
      return new EchoNestErrorEvent(type, code, message);
    }
  }
}
