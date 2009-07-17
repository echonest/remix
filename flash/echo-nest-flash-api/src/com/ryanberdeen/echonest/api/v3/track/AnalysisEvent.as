package com.ryanberdeen.echonest.api.v3.track {
  import flash.events.Event;

  public class AnalysisEvent extends Event {
    public static const UNKNOWN:String = "unknown";
    public static const PENDING:String = "pending";
    public static const NOT_READY:String = "notReady";
    public static const COMPLETE:String = "analyzed";
    public static const ERROR:String = "error";

    public function AnalysisEvent(type:String) {
      super(type);
    }

    override public function clone():Event {
      return new AnalysisEvent(type);
    }
  }
}
