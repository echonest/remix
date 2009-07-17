package com.ryanberdeen.echonest.api.v3.track {
  import com.ryanberdeen.echonest.api.v3.EchoNestError;
  import com.ryanberdeen.echonest.api.v3.EchoNestErrorEvent;

  import flash.events.Event;
  import flash.events.EventDispatcher;
  import flash.net.URLLoader;
  import flash.utils.Timer;

  public class AnalysisLoader extends EventDispatcher {
    private var trackApi:TrackApi;
    private var timer:Timer;
    private var apiLoaders:Array;
    private var apiLoadersComplete:int;

    private var parameters:Object;
    private var _properties:Object;

    private var _analysis:Object;

    public function AnalysisLoader(trackApi:TrackApi):void {
      this.trackApi = trackApi;
      _properties = TrackApi.ALL_PROPERTIES;
      apiLoaders = [];
      _analysis = {};
    }

    public function get analysis():Object {
      return _analysis;
    }

    public function set properties(properties:Array):void {
      if (properties == null || properties.length == 0) {
        _properties = TrackApi.ALL_PROPERTIES;
      }
      else {
        _properties = properties;
      }
    }

    public function load(parameters:Object):void {
      this.parameters = parameters;
      getMetadata();
    }

    public function reload():void {
      // TODO exception if currently loading
      getMetadata();
    }

    private function waitForAnalysis(delay:int):void {
      timer = new Timer(delay, 1);
      timer.addEventListener('timer', function(e:Event):void {
        timer = null;
        getMetadata();
      });
      timer.start();
    }

    private function getMetadata():void {
      trackApi.getMetadata(parameters, {
        onResponse: metadataResponseHandler,
        onEchoNestError: metadataEchoNestErrorHandler,
        onError: errorHandler
      });
    }

    private function metadataResponseHandler(metadata:Object):void {
      if (metadata.status == 'PENDING') {
        // try again in 5 seconds
        dispatchEvent(new AnalysisEvent(AnalysisEvent.PENDING));
        waitForAnalysis(5000);
        return;
      }
      else if (metadata.status == 'COMPLETE') {
        dispatchEvent(new AnalysisEvent(AnalysisEvent.COMPLETE));
        loadAnalysis();
      }
      else if (metadata.status == 'UNKNOWN') {
        dispatchEvent(new AnalysisEvent(AnalysisEvent.UNKNOWN));
      }
      else {
        dispatchEvent(new AnalysisEvent(AnalysisEvent.ERROR));
      }
      analysis.metadata = metadata;
    }

    private function metadataEchoNestErrorHandler(e:EchoNestError):void {
      if (e.code == 11) { // Analysis not ready (please try again in a few minutes)
        dispatchEvent(new AnalysisEvent(AnalysisEvent.NOT_READY));
        // try again in 15 seconds
        waitForAnalysis(15000);
      }
      else {
        echoNestErrorHandler(e);
      }
    }

    private function loadAnalysis():void {
      apiLoadersComplete = 0;

      for each (var propertyName:String in _properties) {
        var methodName:String = "get" + propertyName.substring(0, 1).toUpperCase() + propertyName.substring(1);
        var apiLoader:URLLoader = trackApi[methodName](parameters, {
            onResponse: responseHandler,
            onResponseArgument: propertyName,
            onEchoNestError: echoNestErrorHandler,
            onError: errorHandler
          }
        );
        apiLoaders.push(apiLoader);
      }
    }

    private function errorHandler(event:Event):void {
      dispatchEvent(event);
    }

    private function echoNestErrorHandler(error:EchoNestError):void {
      dispatchEvent(error.createEvent());
    }

    private function responseHandler(propertyName:String, response:Object):void {
      _analysis[propertyName] = response;
      apiLoadersComplete++;
      if (apiLoadersComplete == apiLoaders.length) {
        analysisLoadedHandler();
      }
    }

    private function analysisLoadedHandler():void {
      dispatchEvent(new Event(Event.COMPLETE));
    }
  }
}
