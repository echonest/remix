/*
 * Copyright 2009 Ryan Berdeen. All rights reserved.
 * Distributed under the terms of the MIT License.
 * See accompanying file LICENSE.txt
 */

package com.ryanberdeen.echonest.api.v3 {
  /**
  * Represents an Echo Nest API response with a nonzero status code.
  */
  public class EchoNestError extends Error {
    private var _code:int;
    private var _description:String;

    public function EchoNestError(code:int, description:String):void {
      super(code + ': ' + description);
      _code = code;
      _description = description;
    }

    /**
    * The status message returned by the Echo Nest API.
    */
    public function get description():String {
      return _description;
    }

    /**
    * The status code returned by the Echo Nest API.
    */
    public function get code():int {
      return _code;
    }

    public function createEvent():EchoNestErrorEvent {
      return new EchoNestErrorEvent(EchoNestErrorEvent.ECHO_NEST_ERROR, _code, _description);
    }
  }
}
