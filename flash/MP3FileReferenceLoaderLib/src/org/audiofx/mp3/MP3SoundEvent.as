/*
Copyright (c) 2008 Christopher Martin-Sperry (audiofx.org@gmail.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/

package org.audiofx.mp3
{
	import flash.events.Event;
	import flash.media.Sound;

	/**
	 * Event type used by <code>MP3FileReferenceLoader</code>
	 * @author spender
	 * @see org.audiofx.mp3.MP3FileReferenceLoader
	 */
	public class MP3SoundEvent extends Event
	{
		/**
		 * A loaded Sound instance. Can call <code>play</code> or <code>extract</code> to get at the audio 
		 */
		public var sound:Sound;
		
		/**
		 *  Used to signal the loading of a sound by the <code>MP3FileReferenceLoader</code> following a call to <code>MP3FileReferenceLoader.getSound</code>
		 *	@eventType complete
		 *  @see org.audiofx.mp3.MP3FileReferenceLoader
		 */
		public static const COMPLETE:String="complete";
		public function MP3SoundEvent(type:String, sound:Sound, bubbles:Boolean=false, cancelable:Boolean=false)
		{
			super(type, bubbles, cancelable);
			this.sound=sound;
		}
		
	}
}