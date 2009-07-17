package com.ryanberdeen.echonest.api.v3.track.utils {
  import flash.events.Event;

  public class TrackLoaderEvent extends Event {
    public static const LOADING_SOUND:String = "loadingSound";
    public static const SOUND_LOADED:String = "soundLoaded";
    public static const CALCULATING_MD5:String = "calculatingMd5";
    public static const MD5_CALCULATED:String = "md5Calculated";
    public static const UPLOADING_FILE:String = "uploadingFile";
    public static const FILE_UPLOADED:String = "fileUploaded";
    public static const CHECKING_ANALYSIS:String = "checkingAnalysis";
    public static const LOADING_ANALYSIS:String = "loadingAnalysis";

    public function TrackLoaderEvent(type:String) {
      super(type);
    }

    override public function clone():Event {
      return new TrackLoaderEvent(type);
    }
  }
}
