package {
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.events.MouseEvent;
	import flash.net.FileFilter;
	import flash.net.FileReference;
	
	import org.audiofx.mp3.MP3FileReferenceLoader;
	import org.audiofx.mp3.MP3SoundEvent;

	public class MP3FileReferenceTest extends Sprite
	{
		private var loader:MP3FileReferenceLoader;
		private var fileReference:FileReference;
		public function MP3FileReferenceTest()
		{
			loader=new MP3FileReferenceLoader();
			loader.addEventListener(MP3SoundEvent.COMPLETE,mp3LoaderCompleteHandler);
			fileReference=new FileReference();
			fileReference.addEventListener(Event.SELECT,fileReferenceSelectHandler);
			stage.addEventListener(MouseEvent.CLICK,clickHandler);
		}
		private function clickHandler(ev:MouseEvent):void
		{
			fileReference.browse([new FileFilter("mp3 files","*.mp3")]);
		}
		private function fileReferenceSelectHandler(ev:Event):void
		{
			loader.getSound(fileReference);
		}
		private function mp3LoaderCompleteHandler(ev:MP3SoundEvent):void
		{
			ev.sound.play();
		}
	}
}
