package com.ryanberdeen.echonest.api.v3.track.utils {
  import com.ryanberdeen.echonest.api.v3.EchoNestError;
  import com.ryanberdeen.echonest.api.v3.EchoNestErrorEvent;
  import com.ryanberdeen.echonest.api.v3.track.AnalysisEvent;
  import com.ryanberdeen.echonest.api.v3.track.AnalysisLoader;
  import com.ryanberdeen.echonest.api.v3.track.TrackApi;
  import com.ryanberdeen.utils.MD5Calculator;

  import flash.events.Event;
  import flash.events.EventDispatcher;
  import flash.events.IOErrorEvent;
  import flash.events.SecurityErrorEvent;
  import flash.media.Sound;
  import flash.net.FileReference;

  import org.audiofx.mp3.MP3FileReferenceLoader;
  import org.audiofx.mp3.MP3SoundEvent;

  public class TrackLoader extends EventDispatcher {
    private var trackApi:TrackApi;

    private var _fileReference:FileReference;
    private var mp3Loader:MP3FileReferenceLoader;
    private var _md5Calculator:MD5Calculator;
    private var _analysisLoader:AnalysisLoader;

    private var _alwaysUpload:Boolean;

    private var _sound:Sound;

    private var _md5:String;
    private var _id:String;

    public function TrackLoader(trackApi:TrackApi) {
      this.trackApi = trackApi;
      _fileReference = new FileReference();
      _md5Calculator = new MD5Calculator();
      _analysisLoader = new AnalysisLoader(trackApi);
      _alwaysUpload = false;
    }

    public function set alwaysUpload(alwaysUpload:Boolean):void {
      _alwaysUpload = alwaysUpload;
    }

    public function get fileReference():FileReference {
      return _fileReference;
    }

    public function get md5Calculator():MD5Calculator {
      return _md5Calculator;
    }

    public function get analysisLoader():AnalysisLoader {
      return _analysisLoader;
    }

    public function get sound():Sound {
      return _sound;
    }

    public function load(...properties):void {
      _analysisLoader.properties = properties;
      _fileReference.addEventListener(Event.SELECT, fileReferenceSelectHandler);
      _fileReference.browse();
    }

    private function fileReferenceSelectHandler(e:Event):void {
      dispatchEvent(new TrackLoaderEvent(TrackLoaderEvent.LOADING_SOUND));
      mp3Loader = new MP3FileReferenceLoader();
      mp3Loader.addEventListener(Event.COMPLETE, soundLoadCompleteHandler);
      mp3Loader.getSound(_fileReference);
    }

    private function soundLoadCompleteHandler(e:MP3SoundEvent):void {
      _sound = e.sound;
      dispatchEvent(new TrackLoaderEvent(TrackLoaderEvent.SOUND_LOADED));
      mp3Loader.removeEventListener(Event.COMPLETE, soundLoadCompleteHandler);

      if (_alwaysUpload) {
        uploadFile();
      }
      else {
        calculateMd5();
      }
    }

    private function calculateMd5():void {
      dispatchEvent(new TrackLoaderEvent(TrackLoaderEvent.CALCULATING_MD5));
      _md5Calculator.addEventListener(Event.COMPLETE, md5CompleteHandler);
      _md5Calculator.calculate(_fileReference.data);
    }

    private function md5CompleteHandler(e:Event):void {
      dispatchEvent(new TrackLoaderEvent(TrackLoaderEvent.MD5_CALCULATED));
      _md5 = _md5Calculator.md5;
      _md5Calculator = null;

      dispatchEvent(new TrackLoaderEvent(TrackLoaderEvent.CHECKING_ANALYSIS));
      loadAnalysis({md5: _md5});
    }

    private function uploadFile():void {
      dispatchEvent(new TrackLoaderEvent(TrackLoaderEvent.UPLOADING_FILE));
      trackApi.uploadFileReference({file: _fileReference, wait: "N"}, {
        onResponse: function(track:Object):void {
          _id = track.id;
          dispatchEvent(new TrackLoaderEvent(TrackLoaderEvent.FILE_UPLOADED));
          dispatchEvent(new TrackLoaderEvent(TrackLoaderEvent.LOADING_ANALYSIS));
          loadAnalysis({id: _id});
        },
        onEchoNestError: function(error:EchoNestError):void {
          dispatchEvent(error.createEvent());
        },
        onError: dispatchEvent
      });
    }

    private function loadAnalysis(parameters:Object):void {
      _analysisLoader.addEventListener(AnalysisEvent.UNKNOWN, analysisUnknownHandler);
      _analysisLoader.load(parameters);
    }

    private function analysisUnknownHandler(e:Event):void {
      uploadFile();
      dispatchEvent(e);
    }
  }
}
