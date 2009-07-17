/*
 * Copyright 2009 Ryan Berdeen. All rights reserved.
 * Distributed under the terms of the MIT License.
 * See accompanying file LICENSE.txt
 */

package com.ryanberdeen.echonest.api.v3 {
  import flash.events.Event;
  import flash.events.EventDispatcher;
  import flash.events.HTTPStatusEvent;
  import flash.events.IOErrorEvent;
  import flash.events.ProgressEvent;
  import flash.events.SecurityErrorEvent;
  import flash.net.URLLoader;
  import flash.net.URLRequest;
  import flash.net.URLRequestHeader;
  import flash.net.URLVariables;

  /**
  * Base class for Echo Nest API classes.
  */
  public class ApiSupport {
    public static const API_VERSION:int = 3;
    /**
    * @private
    */
    protected var _baseUrl:String = 'http://developer.echonest.com/api/';

    /**
    * @private
    */
    protected var _apiKey:String;

    /**
    * The API key to use for Echo Nest API requests.
    */
    public function set apiKey(apiKey:String):void {
      _apiKey = apiKey;
    }

    /**
    * Creates a request for an Echo Nest API method call with a set of
    * parameters.
    *
    * @param method The method to call.
    * @param parameters The parameters to include in the request.
    *
    * @return The request to use to call the method.
    */
    public function createRequest(method:String, parameters:Object):URLRequest {
      var variables:URLVariables = new URLVariables;
      variables.api_key = _apiKey;
      variables.version = API_VERSION;
      for (var name:String in parameters) {
        variables[name] = parameters[name];
      }

      var request:URLRequest = new URLRequest();
      request.url = _baseUrl + method;
      request.data = variables;

      return request;
    }

    /**
    * Creates a loader with event listeners.
    *
    * <p>The following options are supported:</p>
    *
    * <table><thead><tr><th>Option</th><th>Event</th></tr></thead><tbody>
    *   <tr>
    *     <td>onComplete</td>
    *     <td><code>Event.COMPLETE</code></td>
    *   </tr>
    *   <tr>
    *     <td>onResponse</td>
    *     <td>Called with the processed response.</td>
    *   </tr>
    *   <tr>
    *     <td>onEchoNestError</td>
    *     <td>Called with an <code>EchoNestError</code> if the status code is nonzero</td>
    *   </tr>
    *   <tr>
    *     <td>onProgress</td>
    *     <td><code>ProgressEvent.PROGRESS</code></td>
    *   </tr>
    *   <tr>
    *     <td>onSecurityError</td>
    *     <td><code>SecurityErrorEvent.SECURITY_ERROR</code></td>
    *   </tr>
    *   <tr>
    *     <td>onIoError</td>
    *     <td><code>IOErrorEvent.IO_ERROR</code></td>
    *   </tr>
    *   <tr>
    *     <td>onError</td>
    *     <td><code>IOErrorEvent.IO_ERROR</code><br/> <code>SecurityErrorEvent.SECURITY_ERROR</code></td>
    *   </tr>
    *   <tr>
    *     <td>onHttpStatus</td>
    *     <td><code>HTTPStatusEvent.HTTP_STATUS</code></td>
    *   </tr>
    * </tbody></table>
    *
    * @param options The event listener options for the loader.
    * @param responseProcessor The function that processes the XML response.
    * @param responseProcessorArgs The arguments to pass to the response
    *        processor function.
    */
    public function createLoader(options:Object, responseProcessor:Function, ...responseProcessorArgs):URLLoader {
      var loader:URLLoader = new URLLoader();

      if (options.onComplete) {
        loader.addEventListener(Event.COMPLETE, options.onComplete);
      }

      if (options.onResponse) {
        loader.addEventListener(Event.COMPLETE, function(e:Event):void {
          try {
            var responseXml:XML = new XML(loader.data);
            checkStatus(responseXml);
            responseProcessorArgs.push(responseXml);
            var response:Object = responseProcessor.apply(responseProcessor, responseProcessorArgs);
            if (options.onResponseArgument) {
              options.onResponse(options.onResponseArgument, response);
            }
            else {
              options.onResponse(response);
            }
          }
          catch (e:EchoNestError) {
            if (options.onEchoNestError) {
              options.onEchoNestError(e);
            }
          }
        });
      }

      addEventListeners(options, loader);

      return loader;
    }

    /**
    * Adds the standard Echo Nest Flash API event listeners to the event
    * dispatcher.
    *
    * <p>The event dispatcher should be either a <code>URLLoader</code> or a
    * <code>FileReference</code>.</p>
    *
    * <p>This method does not add the <code>onComplete</code> or
    * <code>onResponse</code> event listeners. They are added by
    * <code>createLoader()</code>.</p>
    *
    * @private
    *
    * @param options The event listener options. See
    *        <code>createLoader()</code> for the list of available options.
    * @param dispatcher The event dispatcher to add the event listeners to.
    */
    protected function addEventListeners(options:Object, dispatcher:EventDispatcher):void {
      if (options.onProgress) {
        dispatcher.addEventListener(ProgressEvent.PROGRESS, options.onProgress);
      }

      if (options.onSecurityError) {
        dispatcher.addEventListener(SecurityErrorEvent.SECURITY_ERROR, options.onSecurityError);
      }

      if (options.onIoError) {
        dispatcher.addEventListener(IOErrorEvent.IO_ERROR, options.onIoError);
      }

      if (options.onError) {
        dispatcher.addEventListener(SecurityErrorEvent.SECURITY_ERROR, options.onError);
        dispatcher.addEventListener(IOErrorEvent.IO_ERROR, options.onError);
      }

      if (options.onHttpStatus) {
        dispatcher.addEventListener(HTTPStatusEvent.HTTP_STATUS, options.onHttpStatus);
      }
    }

    /**
    * Throws an <code>EchoNestError</code> if the status indicates an error.
    *
    * @param The XML result of an Echo Nest API call.
    *
    * @throws EchoNestError When the status code is nonzero.
    */
    public function checkStatus(response:XML):void {
      if (response.status.code != 0) {
        throw new EchoNestError(response.status.code, response.status.message);
      }
    }
  }
}