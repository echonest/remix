/*
 * Copyright 2009 Ryan Berdeen. All rights reserved.
 * Distributed under the terms of the MIT License.
 * See accompanying file LICENSE.txt
 */

package com.ryanberdeen.echonest.api.v3.track {
  import com.ryanberdeen.echonest.api.v3.ApiSupport;
  import com.ryanberdeen.echonest.api.v3.EchoNestError;

  import flash.events.DataEvent;
  import flash.events.Event;
  import flash.net.FileReference;
  import flash.net.URLLoader;
  import flash.net.URLRequest;
  import flash.net.URLRequestMethod;
  import flash.utils.ByteArray;

  /**
  * Methods to interact with the Echo Nest track API.
  *
  * <p>All of the API methods in this class accept basically the same
  * parameters. The <code>parameters</code> parameter contains the parameters
  * to pass to the Echo Nest method. For most methods, this will be
  * <strong><code>id</code></strong> or <strong><code>md5</code></strong>.
  * The <code>api_key</code> and <code>version</code> parameters will always be
  * set.</p>
  *
  * <p>The <code>loaderOptions</code> parameter contains the event listeners
  * for the loading process. Most importantly, the
  * <strong><code>onResponse</code></strong> method will be called with the
  * results of the API method. See the <code>ApiSupport.createLoader()</code>
  * method for a description of the loader options.</p>
  *
  * <p>For a description of the response formats, see the various
  * <code>process...Response()</code> methods.</p>
  *
  * <p>Be sure to set the <code>apiKey</code> property before calling any API
  * methods.</p>
  *
  * @example This example shows how to retrieve the modality of a track.
  *
  * <listing version="3.0">
  * var trackApi:TrackApi = new TrackApi();
  * trackApi.apiKey = 'EJ1B4BFNYQOC56SGF';
  *
  * trackApi.getMode({id: 'music://id.echonest.com/~/TR/TRLFPPE11C3F10749F'}, {
  *   onResponse: function(mode:Array):void {
  *     trace('Mode: ' + mode[0] +', confidence: ' + mode[1]);  // Mode: 1, confidence: 1
  *   }
  * });
  * </listing>
  */
  public class TrackApi extends ApiSupport {
    public static const BARS:String = "bars";
    public static const BEATS:String = "beats";
    public static const DURATION:String = "duration";
    public static const END_OF_FADE_IN:String = "endOfFadeIn";
    public static const KEY:String = "key";
    public static const LOUDNESS:String = "loudness";
    public static const METADATA:String = "metadata";
    public static const MODE:String = "mode";
    public static const SECTIONS:String = "sections";
    public static const SEGMENTS:String = "segments";
    public static const START_OF_FADE_OUT:String = "startOfFadeOut";
    public static const TATUMS:String = "tatums";
    public static const TEMPO:String = "tempo";
    public static const TIME_SIGNATURE:String = "timeSignature";

    public static const ALL_PROPERTIES:Array = [
      BARS,
      BEATS,
      DURATION,
      END_OF_FADE_IN,
      KEY,
      LOUDNESS,
      METADATA,
      MODE,
      SECTIONS,
      SEGMENTS,
      START_OF_FADE_OUT,
      TATUMS,
      TEMPO,
      TIME_SIGNATURE
    ];

    /**
    * Adds the standard Echo Nest Flash API event listeners to a file
    * reference.
    *
    * @param options The event listener options. See
    *        <code>createLoader()</code> for the list of available options.
    * @param dispatcher The file reference to add the event listeners to.
    */
    public function addFileReferenceEventListeners(options:Object, fileReference:FileReference, responseProcessor:Function, ...responseProcessorArgs):void {
      if (options.onComplete) {
        fileReference.addEventListener(Event.COMPLETE, options.onComplete);
      }

      if (options.onResponse) {
        fileReference.addEventListener(DataEvent.UPLOAD_COMPLETE_DATA, function(e:DataEvent):void {
          try {
            var responseXml:XML = new XML(e.data);
            checkStatus(responseXml);
            responseProcessorArgs.push(responseXml);
            var response:Object = responseProcessor.apply(responseProcessor, responseProcessorArgs);
            options.onResponse(response);
          }
          catch (e:EchoNestError) {
            if (options.onEchoNestError) {
              options.onEchoNestError(e);
            }
          }
        });
      }

      addEventListeners(options, fileReference);
    }

    /**
    * Processes the response from the <code>upload</code> API method.
    *
    * <p><strong>Response Format</strong></p>
    *
    * <p>Returns:</p>
    *
    * <pre>
    * {
    *   id:    String(id),
    *   md5:   String(md5),
    *   ready: Boolean(ready)
    * }
    * </pre>
    *
    * @param response The response to process.
    *
    * @return The result of processing the response.
    *
    * @see #upload()
    * @see #uploadFileData()
    */
    public function processUploadResponse(response:XML):Object {
      var track:XMLList = response.track;
      return {
        id: track.@id.toString(),
        md5: track.@md5.toString(),
        ready: track.@ready == 'true'
      }
    }

    /**
    * Processes the response from an Echo Nest API method that returns a list
    * of numbers with confidence values.
    *
    * <p><strong>Response Format</strong></p>
    *
    * <p>Returns an array of <code>NumberWithConfidence</code>.</p>
    *
    * @param name The element name of the list items.
    * @param response The response to process.
    *
    * @return The result of processing the response.
    *
    * @see #getSimpleAnalysisList()
    */
    public function processSimpleAnalysisListResponse(name:String, response:XML):Array {
      var result:Array = [];

      for each (var item:XML in response.analysis[name]) {
        result.push(new NumberWithConfidence(Number(item), Number(item.@confidence)));
      }

      return result;
    }

    /**
    * Invokes an Echo Nest API method that returns a list of numbers with
    * confidence values.
    *
    * @param name The singular name of the type of item to get. For example, for
    *        <code>get_bars</code>, the name is <code>bar</code>.
    * @param parameters The parameters to include in the API request.
    * @param loaderOptions The event listener options for the loader.
    *
    * @return The <code>URLLoader</code> being used to perform the API call.
    *
    * @see com.ryanberdeen.echonest.api.v3.ApiSupport#createRequest()
    * @see com.ryanberdeen.echonest.api.v3.ApiSupport#createLoader()
    * @see #processSimpleAnalysisListResponse()
    */
    public function getSimpleAnalysisList(name:String, parameters:Object, loaderOptions:Object):URLLoader {
      var request:URLRequest = createRequest('get_' + name + 's', parameters);
      var loader:URLLoader = createLoader(loaderOptions, processSimpleAnalysisListResponse, name);
      loader.load(request);
      return loader;
    }

    /**
    * Processes the response from an Echo Nest API method that returns a
    * number.
    *
    * <p><strong>Response Format</strong></p>
    *
    * <p>Returns a <code>Number</code>.</p>
    *
    * @param name The name of the element containing the result value.
    * @param response The response to process.
    *
    * @return The result of processing the response.
    *
    * @see #getNumber()
    */
    public function processNumberResponse(name:String, response:XML):Number {
      return Number(response.analysis[name]);
    }

    /**
    * Invokes an Echo Nest API method that returns a number.
    *
    * @param name The name of the type of item to get. For example for
    *        <code>get_duration</code>, the name is <code>duration</code>.
    * @param parameters The parameters to include in the API request.
    * @param loaderOptions The event listener options for the loader.
    *
    * @return The <code>URLLoader</code> being used to perform the API call.
    *
    * @see com.ryanberdeen.echonest.api.v3.ApiSupport#createRequest()
    * @see com.ryanberdeen.echonest.api.v3.ApiSupport#createLoader()
    * @see #processNumberResponse()
    */
    public function getNumber(name:String, parameters:Object, loaderOptions:Object):URLLoader {
      var request:URLRequest = createRequest('get_' + name, parameters);
      var loader:URLLoader = createLoader(loaderOptions, processNumberResponse, name);
      loader.load(request);
      return loader;
    }

    /**
    * Processes the response from an Echo Nest API method that returns a number
    * with a confidence value.
    *
    * <p><strong>Response Format</strong></p>
    *
    * <p>Returns a <code>NumberWithConfidence</code>.</p>
    *
    * @param name The name of the element containing the result value.
    * @param response The response to process.
    *
    * @see #getNumberWithConfidence()
    *
    * @return The result of processing the response.
    */
    public function processNumberWithConfidenceResponse(name:String, response:XML):NumberWithConfidence {
      var item:XMLList = response.analysis[name];
      return new NumberWithConfidence(Number(item), Number(item.@confidence));
    }

    /**
    * Invokes an Echo Nest API method that returns a number with a confidence
    * value.
    *
    * @param name The name of the type of item to get. For example for
    *        <code>get_duration</code>, the name is <code>duration</code>.
    * @param parameters The parameters to include in the API request.
    * @param loaderOptions The event listener options for the loader.
    *
    * @return The <code>URLLoader</code> being used to perform the API call.
    *
    * @see com.ryanberdeen.echonest.api.v3.ApiSupport#createRequest()
    * @see com.ryanberdeen.echonest.api.v3.ApiSupport#createLoader()
    * @see #processNumberWithConfidenceResponse()
    */
    public function getNumberWithConfidence(name:String, parameters:Object, loaderOptions:Object):URLLoader {
      var request:URLRequest = createRequest('get_' + name, parameters);
      var loader:URLLoader = createLoader(loaderOptions, processNumberWithConfidenceResponse, name);
      loader.load(request);
      return loader;
    }

    /**
    * Processes the response from the <code>get_metadata</code> API method.
    *
    * <p><strong>Response Format</strong></p>
    *
    * <p>Returns:</p>
    *
    * <pre>
    * {
    *   bitrate:    Number(bitrate),
    *   duration:   Number(duration),
    *   samplerate: Number(samplerate),
    *   status:     String(status),
    *   artist:     String(artist),
    *   release:    String(release),
    *   title:      String(title)
    * }
    * </pre>
    *
    * <p>Any additional tags present in the XML will be included in the
    * response object as strings.</p>
    *
    * @param response The response to process.
    *
    * @return The result of processing the response.
    *
    * @see #getMetadata()
    */
    public function processMetadataResponse(response:XML):Object {
      var analysis:XMLList = response.analysis.copy();

      var result:Object = {};
      // add documented numeric values
      for each(var name:String in ['duration', 'samplerate', 'bitrate']) {
        result[name] = Number(analysis[name]);
        delete analysis[name];
      }

      // add all remaining values as strings
      for each (var item:XML in analysis.children()) {
        result[item.name()] = String(item);
      }
      return result;
    }

    /**
    * Processes the response from the <code>get_sections</code> API method.
    *
    * <p><strong>Response Format</strong></p>
    *
    * <p>Returns an array of <code>Section</code>.</p>
    *
    * @param response The response to process.
    *
    * @return The result of processing the response.
    *
    * @see #getSections()
    * @see Section
    */
    public function processSectionsResponse(response:XML):Array {
      var result:Array = [];

      for each (var sectionXml:XML in response.analysis.section) {
        var section:Section = new Section();
        section.start = Number(sectionXml.@start);
        section.duration = Number(sectionXml.@duration);
        result.push(section);
      }

      return result;
    }

    /**
    * Processes the response from the <code>get_segments</code> API method.
    *
    * <p><strong>Response Format</strong></p>
    *
    * <p>Returns an array of <code>Segment</code>.</p>
    *
    * @param response The response to process.
    *
    * @return The result of processing the response.
    *
    * @see #getSegments()
    * @see Segment
    */
    public function processSegmentsResponse(response:XML):Array {
      var result:Array = [];
      var previousSegment:Segment = new Segment();  // this is never used, but eliminates an if in the loop

      var segmentXml:XML;
      for each (segmentXml in response.analysis.segment) {
        var segment:Segment = new Segment();

        segment.start = segmentXml.@start;
        segment.duration = segmentXml.@duration;

        segment.startLoudness = segmentXml.loudness.dB[0];
        previousSegment.endLoudness = segmentXml.startLoudness;

        var maxLoudnessXml:XML = segmentXml.loudness.dB[1];
        segment.maxLoudness = Number(maxLoudnessXml);
        segment.maxLoudnessTimeOffset = maxLoudnessXml.@time;

        var pitches:Array = [];
        for each (var pitch:XML in segmentXml.pitches.pitch) {
          pitches.push(Number(pitch));
        }
        segment.pitches = pitches;

        var timbre:Array = [];
        for each (var coeff:XML in segmentXml.timbre.coeff) {
          timbre.push(Number(coeff));
        }

        segment.timbre = timbre;

        previousSegment = segment;
        result.push(segment);
      }

      previousSegment.endLoudness = segmentXml.loudness.dB[2];

      return result;
    }

    /**
    * Invokes the Echo Nest <code>get_bars</code> API method.
    *
    * @param parameters The parameters to include in the API request.
    * @param loaderOptions The event listener options for the loader.
    *
    * @return The <code>URLLoader</code> being used to perform the API call.
    *
    * @see #getSimpleAnalysisList()
    * @see http://developer.echonest.com/docs/method/get_bars/
    */
    public function getBars(parameters:Object, loaderOptions:Object):URLLoader {
      return getSimpleAnalysisList('bar', parameters, loaderOptions);
    }

    /**
    * Invokes the Echo Nest <code>get_beats</code> API method.
    *
    * @param parameters The parameters to include in the API request.
    * @param loaderOptions The event listener options for the loader.
    *
    * @return The <code>URLLoader</code> being used to perform the API call.
    *
    * @see #getSimpleAnalysisList()
    * @see http://developer.echonest.com/docs/method/get_beats/
    */
    public function getBeats(parameters:Object, loaderOptions:Object):URLLoader {
      return getSimpleAnalysisList('beat', parameters, loaderOptions);
    }

    /**
    * Invokes the Echo Nest <code>get_duration</code> API method.
    *
    * @param parameters The parameters to include in the API request.
    * @param loaderOptions The event listener options for the loader.
    *
    * @return The <code>URLLoader</code> being used to perform the API call.
    *
    * @see #getNumber()
    * @see http://developer.echonest.com/docs/method/get_duration/
    */
    public function getDuration(parameters:Object, loaderOptions:Object):URLLoader {
      return getNumber('duration', parameters, loaderOptions);
    }

    /**
    * Invokes the Echo Nest <code>get_end_of_fade_in</code> API method.
    *
    * @param parameters The parameters to include in the API request.
    * @param loaderOptions The event listener options for the loader.
    *
    * @return The <code>URLLoader</code> being used to perform the API call.
    *
    * @see #getNumber()
    * @see http://developer.echonest.com/docs/method/get_end_of_fade_in/
    */
    public function getEndOfFadeIn(parameters:Object, loaderOptions:Object):URLLoader {
      return getNumber('end_of_fade_in', parameters, loaderOptions);
    }

    /**
    * Invokes the Echo Nest <code>get_key</code> API method.
    *
    * @param parameters The parameters to include in the API request.
    * @param loaderOptions The event listener options for the loader.
    *
    * @return The <code>URLLoader</code> being used to perform the API call.
    *
    * @see #getNumberWithConfidence()
    * @see http://developer.echonest.com/docs/method/get_key/
    */
    public function getKey(parameters:Object, loaderOptions:Object):URLLoader {
      return getNumberWithConfidence('key', parameters, loaderOptions);
    }

    /**
    * Invokes the Echo Nest <code>get_loudness</code> API method.
    *
    * @param parameters The parameters to include in the API request.
    * @param loaderOptions The event listener options for the loader.
    *
    * @return The <code>URLLoader</code> being used to perform the API call.
    *
    * @see #getNumber()
    * @see http://developer.echonest.com/docs/method/get_loudness/
    */
    public function getLoudness(parameters:Object, loaderOptions:Object):URLLoader {
      return getNumber('loudness', parameters, loaderOptions);
    }

    /**
    * Invokes the Echo Nest <code>get_metadata</code> API method.
    *
    * @param parameters The parameters to include in the API request.
    * @param loaderOptions The event listener options for the loader.
    *
    * @return The <code>URLLoader</code> being used to perform the API call.
    *
    * @see #processMetadataResponse()
    * @see http://developer.echonest.com/docs/method/get_metadata/
    */
    public function getMetadata(parameters:Object, loaderOptions:Object):URLLoader {
      var request:URLRequest = createRequest('get_metadata', parameters);
      var loader:URLLoader = createLoader(loaderOptions, processMetadataResponse);
      loader.load(request);
      return loader;
    }

    /**
    * Invokes the Echo Nest <code>get_mode</code> API method.
    *
    * @param parameters The parameters to include in the API request.
    * @param loaderOptions The event listener options for the loader.
    *
    * @return The <code>URLLoader</code> being used to perform the API call.
    *
    * @see #getNumberWithConfidence()
    * @see http://developer.echonest.com/docs/method/get_mode/
    */
    public function getMode(parameters:Object, loaderOptions:Object):URLLoader {
      return getNumberWithConfidence('mode', parameters, loaderOptions);
    }

    /**
    * Invokes the Echo Nest <code>get_sections</code> API method.
    *
    * @param parameters The parameters to include in the API request.
    * @param loaderOptions The event listener options for the loader.
    *
    * @return The <code>URLLoader</code> being used to perform the API call.
    *
    * @see #processSectionsResponse()
    * @see http://developer.echonest.com/docs/method/get_sections/
    */
    public function getSections(parameters:Object, loaderOptions:Object):URLLoader {
      var request:URLRequest = createRequest('get_sections', parameters);
      var loader:URLLoader = createLoader(loaderOptions, processSectionsResponse);
      loader.load(request);
      return loader;
    }

    /**
    * Invokes the Echo Nest <code>get_segments</code> API method.
    *
    * @param parameters The parameters to include in the API request.
    * @param loaderOptions The event listener options for the loader.
    *
    * @return The <code>URLLoader</code> being used to perform the API call.
    *
    * @see #processSegmentsResponse()
    * @see http://developer.echonest.com/docs/method/get_segments/
    */
    public function getSegments(parameters:Object, loaderOptions:Object):URLLoader {
      var request:URLRequest = createRequest('get_segments', parameters);
      var loader:URLLoader = createLoader(loaderOptions, processSegmentsResponse);
      loader.load(request);
      return loader;
    }

    /**
    * Invokes the Echo Nest <code>get_start_of_fade_out</code> API method.
    *
    * @param parameters The parameters to include in the API request.
    * @param loaderOptions The event listener options for the loader.
    *
    * @return The <code>URLLoader</code> being used to perform the API call.
    *
    * @see #getNumber()
    * @see http://developer.echonest.com/docs/method/get_start_of_fade_out/
    */
    public function getStartOfFadeOut(parameters:Object, loaderOptions:Object):URLLoader {
      return getNumber('start_of_fade_out', parameters, loaderOptions);
    }

    /**
    * Invokes the Echo Nest <code>get_tatums</code> API method.
    *
    * @param parameters The parameters to include in the API request.
    * @param loaderOptions The event listener options for the loader.
    *
    * @return The <code>URLLoader</code> being used to perform the API call.
    *
    * @see #getSimpleAnalysisList()
    * @see http://developer.echonest.com/docs/method/get_tatums/
    */
    public function getTatums(parameters:Object, loaderOptions:Object):URLLoader {
      return getSimpleAnalysisList('tatum', parameters, loaderOptions);
    }

    /**
    * Invokes the Echo Nest <code>get_tempo</code> API method.
    *
    * @param parameters The parameters to include in the API request.
    * @param loaderOptions The event listener options for the loader.
    *
    * @return The <code>URLLoader</code> being used to perform the API call.
    *
    * @see #getNumberWithConfidence()
    * @see http://developer.echonest.com/docs/method/get_tempo/
    */
    public function getTempo(parameters:Object, loaderOptions:Object):URLLoader {
      return getNumberWithConfidence('tempo', parameters, loaderOptions);
    }

    /**
    * Invokes the Echo Nest <code>get_time_signature</code> API method.
    *
    * @param parameters The parameters to include in the API request.
    * @param loaderOptions The event listener options for the loader.
    *
    * @return The <code>URLLoader</code> being used to perform the API call.
    *
    * @see #getNumberWithConfidence()
    * @see http://developer.echonest.com/docs/method/get_time_signature/
    */
    public function getTimeSignature(parameters:Object, loaderOptions:Object):URLLoader {
      return getNumberWithConfidence('time_signature', parameters, loaderOptions);
    }

    /**
    * Invokes the Echo Nest <code>upload</code> API method with a file
    * reference.
    *
    * <p>The <code>parameters</code> object must include a <code>file</code>
    * property, which must be a <code>FileReference</code> that may be
    * <code>upload()</code>ed.</p>
    *
    * @param parameters The parameters to include in the API request.
    * @param loaderOptions The event listener options for the loader.
    *
    * @see com.ryanberdeen.echonest.api.v3.ApiSupport#createRequest()
    * @see #processUploadResponse()
    * @see http://developer.echonest.com/docs/method/upload/
    */
    public function uploadFileReference(parameters:Object, loaderOptions:Object):void {
      var fileReference:FileReference = parameters.file;
      delete parameters.file;

      addFileReferenceEventListeners(loaderOptions, fileReference, processUploadResponse);
      var request:URLRequest = createRequest('upload', parameters);
      fileReference.upload(request, 'file');
    }

    /**
    * Invokes the Echo Nest <code>upload</code> API method.
    *
    * <p>This method is for uploads using the <code>url</code> parameter.
    * To upload a file, use <code>uploadFileReference()</code>.
    *
    * @param parameters The parameters to include in the API request.
    * @param loaderOptions The event listener options for the loader.
    *
    * @return The <code>URLLoader</code> being used to perform the API call.
    *
    * @see com.ryanberdeen.echonest.api.v3.ApiSupport#createRequest()
    * @see com.ryanberdeen.echonest.api.v3.ApiSupport#createLoader()
    * @see #processUploadResponse()
    * @see http://developer.echonest.com/docs/method/upload/
    */
    public function upload(parameters:Object, loaderOptions:Object):URLLoader {
      var request:URLRequest = createRequest('upload', parameters);
      request.method = URLRequestMethod.POST;
      var loader:URLLoader = createLoader(loaderOptions, processUploadResponse);
      loader.load(request);
      return loader;
    }
  }
}
