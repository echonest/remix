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
	import flash.events.EventDispatcher;
	import flash.events.IOErrorEvent;
	import flash.net.FileReference;
	import flash.net.URLLoader;
	import flash.net.URLLoaderDataFormat;
	import flash.net.URLRequest;
	import flash.utils.ByteArray;
	

	
	
	[Event(name="complete", type="flash.events.Event")]
	internal class MP3Parser extends EventDispatcher
	{
		private var mp3Data:ByteArray;
		private var loader:URLLoader;
		private var currentPosition:uint;
		private var sampleRate:uint;
		private var channels:uint;
		private var version:uint;
		private static var bitRates:Array=[-1,32,40,48,56,64,80,96,112,128,160,192,224,256,320,-1,-1,8,16,24,32,40,48,56,64,80,96,112,128,144,160,-1];
		private static var versions:Array=[2.5,-1,2,1];
		private static var samplingRates:Array=[44100,48000,32000];
		public function MP3Parser()
		{
			
			loader=new URLLoader();
			loader.dataFormat=URLLoaderDataFormat.BINARY;
			loader.addEventListener(Event.COMPLETE,loaderCompleteHandler);
			
			
		}
		internal function load(url:String):void
		{
			var req:URLRequest=new URLRequest(url);
			loader.load(req);
		}
		internal function loadFileRef(fileRef:FileReference):void
		{
			fileRef.addEventListener(Event.COMPLETE,loaderCompleteHandler);
			fileRef.addEventListener(IOErrorEvent.IO_ERROR,errorHandler);
			//fileRef.addEventListener(Event.COMPLETE,loaderCompleteHandler);
			fileRef.load();
		}
		private function errorHandler(ev:IOErrorEvent):void
		{
			trace("error\n"+ev.text);
		}
		private function loaderCompleteHandler(ev:Event):void
		{
			mp3Data=ev.currentTarget.data as ByteArray;
			currentPosition=getFirstHeaderPosition();
			dispatchEvent(ev);
		}
		private function getFirstHeaderPosition():uint
		{
			mp3Data.position=0;
			
			
			while(mp3Data.position<mp3Data.length)
			{
				var readPosition:uint=mp3Data.position;
				var str:String=mp3Data.readMultiByte(3,"us-ascii");
				
				
				if(str=="ID3") //here's an id3v2 header. fuck that for a laugh. skipping
				{
					mp3Data.position+=3;
					var b3:int=(mp3Data.readByte()&0x7F)<<21;
					var b2:int=(mp3Data.readByte()&0x7F)<<14;
					var b1:int=(mp3Data.readByte()&0x7F)<<7;
					var b0:int=mp3Data.readByte()&0x7F;
					var headerLength:int=b0+b1+b2+b3;
					var newPosition:int=mp3Data.position+headerLength;
					trace("Found id3v2 header, length "+headerLength.toString(16)+" bytes. Moving to "+newPosition.toString(16));
					mp3Data.position=newPosition;
					readPosition=newPosition;
				}
				else
				{
					mp3Data.position=readPosition;
				}
				
				var val:uint=mp3Data.readInt();
				
				if(isValidHeader(val))
				{
					parseHeader(val);
					mp3Data.position=readPosition+getFrameSize(val);
					if(isValidHeader(mp3Data.readInt()))
					{
						return readPosition;
					}
					
				}

			}
			throw(new Error("Could not locate first header. This isn't an MP3 file"));
		}
		internal function getNextFrame():ByteArraySegment
		{
			mp3Data.position=currentPosition;
			var headerByte:uint;
			var frameSize:uint;	
			while(true)
			{
				if(currentPosition>(mp3Data.length-4))
				{
					trace("passed eof");
					return null;
				}
				headerByte=mp3Data.readInt();
				if(isValidHeader(headerByte))
				{
					frameSize=getFrameSize(headerByte);
					if(frameSize!=0xffffffff)
					{
						break;
					}
				}
				currentPosition=mp3Data.position;
				
			}

			mp3Data.position=currentPosition;
			
			if((currentPosition+frameSize)>mp3Data.length)
			{
				return null;
			}
			
			currentPosition+=frameSize;
			return new ByteArraySegment(mp3Data,mp3Data.position,frameSize);
		}
		internal function writeSwfFormatByte(byteArray:ByteArray):void
		{
			var sampleRateIndex:uint=4-(44100/sampleRate);
			byteArray.writeByte((2<<4)+(sampleRateIndex<<2)+(1<<1)+(channels-1));
		}
		private function parseHeader(headerBytes:uint):void
		{
			var channelMode:uint=getModeIndex(headerBytes);
			version=getVersionIndex(headerBytes);
			var samplingRate:uint=getFrequencyIndex(headerBytes);
			channels=(channelMode>2)?1:2;
			var actualVersion:Number=versions[version];
			var samplingRates:Array=[44100,48000,32000];
			sampleRate=samplingRates[samplingRate];
			switch(actualVersion)
			{
				case 2:
					sampleRate/=2;
					break;
				case 2.5:
					sampleRate/=4;
			}
			
		}
		private function getFrameSize(headerBytes:uint):uint
		{
			
			
			var version:uint=getVersionIndex(headerBytes);
			var bitRate:uint=getBitrateIndex(headerBytes);
			var samplingRate:uint=getFrequencyIndex(headerBytes);
			var padding:uint=getPaddingBit(headerBytes);
			var channelMode:uint=getModeIndex(headerBytes);
			var actualVersion:Number=versions[version];
			var sampleRate:uint=samplingRates[samplingRate];
			if(sampleRate!=this.sampleRate||this.version!=version)
			{
				return 0xffffffff;
			}
			switch(actualVersion)
			{
				case 2:
					sampleRate/=2;
					break;
				case 2.5:
					sampleRate/=4;
			}
			var bitRatesYIndex:uint=((actualVersion==1)?0:1)*bitRates.length/2;
			var actualBitRate:uint=bitRates[bitRatesYIndex+bitRate]*1000;			
			var frameLength:uint=(((actualVersion==1?144:72)*actualBitRate)/sampleRate)+padding;
			return frameLength;
			
		}
		
	 	private function isValidHeader(headerBits:uint):Boolean 
	    {
	        return (((getFrameSync(headerBits)      & 2047)==2047) &&
	                ((getVersionIndex(headerBits)   &    3)!=   1) &&
	                ((getLayerIndex(headerBits)     &    3)!=   0) && 
	                ((getBitrateIndex(headerBits)   &   15)!=   0) &&
	                ((getBitrateIndex(headerBits)   &   15)!=  15) &&
	                ((getFrequencyIndex(headerBits) &    3)!=   3) &&
	                ((getEmphasisIndex(headerBits)  &    3)!=   2)    );
	    }
	
	    private function getFrameSync(headerBits:uint):uint     
	    {
	        return uint((headerBits>>21) & 2047); 
	    }
	
	    private function getVersionIndex(headerBits:uint):uint  
	    { 
	        return uint((headerBits>>19) & 3);  
	    }
	
	    private function getLayerIndex(headerBits:uint):uint    
	    { 
	        return uint((headerBits>>17) & 3);  
	    }
	
	    private function getBitrateIndex(headerBits:uint):uint  
	    { 
	        return uint((headerBits>>12) & 15); 
	    }
	
	    private function getFrequencyIndex(headerBits:uint):uint
	    { 
	        return uint((headerBits>>10) & 3);  
	    }
	
	    private function getPaddingBit(headerBits:uint):uint    
	    { 
	        return uint((headerBits>>9) & 1);  
	    }
	
	    private function getModeIndex(headerBits:uint):uint     
	    { 
	        return uint((headerBits>>6) & 3);  
	    }
	
	    private function getEmphasisIndex(headerBits:uint):uint
	    { 
	        return uint(headerBits & 3);  
	    }
		
	}
}