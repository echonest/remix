////////////////////////////////////////////////////////////////////////////////
//
// License :
//
//  SoundTouch audio processing library
//  Copyright (c) Olli Parviainen
//
//  This library is free software; you can redistribute it and/or
//  modify it under the terms of the GNU Lesser General Public
//  License as published by the Free Software Foundation; either
//  version 2.1 of the License, or (at your option) any later version.
//
//  This library is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
//  Lesser General Public License for more details.
//
//  You should have received a copy of the GNU Lesser General Public
//  License along with this library; if not, write to the Free Software
//  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
//
////////////////////////////////////////////////////////////////////////////////

package com.ryanberdeen.soundtouch {
  import flash.media.Sound;
  import flash.utils.ByteArray;

  public class Stretch {
    // Default values for sound processing parameters:

    /// Default length of a single processing sequence, in milliseconds. This determines to how
    /// long sequences the original sound is chopped in the time-stretch algorithm.
    ///
    /// The larger this value is, the lesser sequences are used in processing. In principle
    /// a bigger value sounds better when slowing down tempo, but worse when increasing tempo
    /// and vice versa.
    ///
    /// Increasing this value reduces computational burden & vice versa.
    //public static const DEFAULT_SEQUENCE_MS:int = 130
    public static const DEFAULT_SEQUENCE_MS:int = USE_AUTO_SEQUENCE_LEN;

    /// Giving this value for the sequence length sets automatic parameter value
    /// according to tempo setting (recommended)
    public static const USE_AUTO_SEQUENCE_LEN:int = 0;

    /// Seeking window default length in milliseconds for algorithm that finds the best possible
    /// overlapping location. This determines from how wide window the algorithm may look for an
    /// optimal joining location when mixing the sound sequences back together.
    ///
    /// The bigger this window setting is, the higher the possibility to find a better mixing
    /// position will become, but at the same time large values may cause a "drifting" artifact
    /// because consequent sequences will be taken at more uneven intervals.
    ///
    /// If there's a disturbing artifact that sounds as if a constant frequency was drifting
    /// around, try reducing this setting.
    ///
    /// Increasing this value increases computational burden & vice versa.
    //public static const DEFAULT_SEEKWINDOW_MS:int = 25;
    public static const DEFAULT_SEEKWINDOW_MS:int = USE_AUTO_SEEKWINDOW_LEN;

    /// Giving this value for the seek window length sets automatic parameter value
    /// according to tempo setting (recommended)
    public static const USE_AUTO_SEEKWINDOW_LEN:int = 0;

    /// Overlap length in milliseconds. When the chopped sound sequences are mixed back together,
    /// to form a continuous sound stream, this parameter defines over how long period the two
    /// consecutive sequences are let to overlap each other.
    ///
    /// This shouldn't be that critical parameter. If you reduce the DEFAULT_SEQUENCE_MS setting
    /// by a large amount, you might wish to try a smaller value on this.
    ///
    /// Increasing this value increases computational burden & vice versa.
    public static const DEFAULT_OVERLAP_MS:int = 8;

    public static const CHANNELS:int = 2;

    // Table for the hierarchical mixing position seeking algorithm
    private static const SCAN_OFFSETS:Array = [
        [ 124,  186,  248,  310,  372,  434,  496,  558,  620,  682,  744, 806,
          868,  930,  992, 1054, 1116, 1178, 1240, 1302, 1364, 1426, 1488,   0],
        [-100,  -75,  -50,  -25,   25,   50,   75,  100,    0,    0,    0,   0,
            0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,   0],
        [ -20,  -15,  -10,   -5,    5,   10,   15,   20,    0,    0,    0,   0,
            0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,   0],
        [  -4,   -3,   -2,   -1,    1,    2,    3,    4,    0,    0,    0,   0,
            0,    0,    0,    0,    0,    0,    0,    0,    0,    0,    0,   0]];

    private var _sound:Sound;

    private var sampleReq:int;
    private var _tempo:Number;

    private var pMidBuffer:Vector.<Number>;
    private var pRefMidBuffer:Vector.<Number>;
    private var overlapLength:int;
    private var seekLength:int;
    private var seekWindowLength:int;
    private var nominalSkip:Number;
    private var skipFract:Number;
    private var bQuickSeek:Boolean;
    private var bMidBufferDirty:Boolean;

    private var sampleRate:int;
    private var sequenceMs:int;
    private var seekWindowMs:int;
    private var overlapMs:int;
    private var bAutoSeqSetting:Boolean;
    private var bAutoSeekSetting:Boolean;

    public function Stretch():void {
      bQuickSeek = false;
      bMidBufferDirty = false;

      pMidBuffer = null;
      overlapLength = 0;

      bAutoSeqSetting = true;
      bAutoSeekSetting = true;

      _tempo = 1;
      setParameters(44100, DEFAULT_SEQUENCE_MS, DEFAULT_SEEKWINDOW_MS, DEFAULT_OVERLAP_MS);
    }

    public function set sound(sound:Sound):void {
      _sound = sound;
    }

    // Sets routine control parameters. These control are certain time constants
    // defining how the sound is stretched to the desired duration.
    //
    // 'sampleRate' = sample rate of the sound
    // 'sequenceMS' = one processing sequence length in milliseconds (default = 82 ms)
    // 'seekwindowMS' = seeking window length for scanning the best overlapping
    //      position (default = 28 ms)
    // 'overlapMS' = overlapping length (default = 12 ms)
    public function setParameters(aSampleRate:int, aSequenceMS:int,
                              aSeekWindowMS:int, aOverlapMS:int):void {
      // accept only positive parameter values - if zero or negative, use old values instead
      if (aSampleRate > 0)   this.sampleRate = aSampleRate;
      if (aOverlapMS > 0)    this.overlapMs = aOverlapMS;

      if (aSequenceMS > 0)
      {
          this.sequenceMs = aSequenceMS;
          bAutoSeqSetting = false;
      } else {
          // zero or below, use automatic setting
          bAutoSeqSetting = true;
      }

      if (aSeekWindowMS > 0)
      {
          this.seekWindowMs = aSeekWindowMS;
          bAutoSeekSetting = false;
      } else {
          // zero or below, use automatic setting
          bAutoSeekSetting = true;
      }

      calcSeqParameters();

      calculateOverlapLength(overlapMs);

      // set tempo to recalculate 'sampleReq'
      tempo = _tempo;
    }

    // Sets new target tempo. Normal tempo = 'SCALE', smaller values represent slower
    // tempo, larger faster tempo.
    public function set tempo(newTempo:Number):void {
      var intskip:int;

      _tempo = newTempo;

      // Calculate new sequence duration
      calcSeqParameters();

      // Calculate ideal skip length (according to tempo value)
      nominalSkip = _tempo * (seekWindowLength - overlapLength);
      skipFract = 0;
      intskip = int(nominalSkip + 0.5);

      // Calculate how many samples are needed in the 'inputBuffer' to
      // process another batch of samples
      sampleReq = Math.max(intskip + overlapLength, seekWindowLength) + seekLength;
    }


    /// Calculates overlapInMsec period length in samples.
    private function calculateOverlapLength(overlapInMsec:int):void {
      var newOvl:int;

      // TODO assert(overlapInMsec >= 0);
      newOvl = (sampleRate * overlapInMsec) / 1000;
      if (newOvl < 16) newOvl = 16;

      // must be divisible by 8
      newOvl -= newOvl % 8;

      overlapLength = newOvl;

      // TODO make fixed size
      pRefMidBuffer = new Vector.<Number>();
    }

    // Adjust tempo param according to tempo, so that variating processing sequence length is used
    // at varius tempo settings, between the given low...top limits
    private static const AUTOSEQ_TEMPO_LOW:Number = 0.5;     // auto setting low tempo range (-50%)
    private static const AUTOSEQ_TEMPO_TOP:Number = 2.0;     // auto setting top tempo range (+100%)

    // sequence-ms setting values at above low & top tempo
    private static const AUTOSEQ_AT_MIN:Number = 125.0;
    private static const AUTOSEQ_AT_MAX:Number = 50.0;
    private static const AUTOSEQ_K:Number = ((AUTOSEQ_AT_MAX - AUTOSEQ_AT_MIN) / (AUTOSEQ_TEMPO_TOP - AUTOSEQ_TEMPO_LOW))
    private static const AUTOSEQ_C:Number = (AUTOSEQ_AT_MIN - (AUTOSEQ_K) * (AUTOSEQ_TEMPO_LOW))

    // seek-window-ms setting values at above low & top tempo
    private static const AUTOSEEK_AT_MIN:Number = 25.0;
    private static const AUTOSEEK_AT_MAX:Number = 15.0;
    private static const AUTOSEEK_K:Number = ((AUTOSEEK_AT_MAX - AUTOSEEK_AT_MIN) / (AUTOSEQ_TEMPO_TOP - AUTOSEQ_TEMPO_LOW))
    private static const AUTOSEEK_C:Number = (AUTOSEEK_AT_MIN - (AUTOSEEK_K) * (AUTOSEQ_TEMPO_LOW))

    private function checkLimits(x:Number, mi:Number, ma:Number):Number {
      return (x < mi) ? mi : ((x > ma) ? ma : x);
    }

    /// Calculates processing sequence length according to tempo setting
    private function calcSeqParameters():void
    {
      var seq:Number;
      var seek:Number;

      if (bAutoSeqSetting)
      {
        seq = AUTOSEQ_C + AUTOSEQ_K * _tempo;
        seq = checkLimits(seq, AUTOSEQ_AT_MAX, AUTOSEQ_AT_MIN);
        sequenceMs = int(seq + 0.5);
      }

      if (bAutoSeekSetting)
      {
          seek = AUTOSEEK_C + AUTOSEEK_K * _tempo;
        seek = checkLimits(seek, AUTOSEEK_AT_MAX, AUTOSEEK_AT_MIN);
        seekWindowMs = int(seek + 0.5);
      }

      // Update seek window lengths
      seekWindowLength = (sampleRate * sequenceMs) / 1000;
      seekLength = (sampleRate * seekWindowMs) / 1000;
    }

    // Enables/disables the quick position seeking algorithm.
    public function set quickSeek(enable:Boolean):void
    {
        bQuickSeek = enable;
    }

    // Seeks for the optimal overlap-mixing position.
    private function seekBestOverlapPosition(buffer:Vector.<Number>):int
    {
      return seekBestOverlapPositionStereoQuick(buffer);
      if (bQuickSeek)
      {
          return seekBestOverlapPositionStereoQuick(buffer);
      }
      else
      {
          return seekBestOverlapPositionStereo(buffer);
      }
    }

    // Seeks for the optimal overlap-mixing position. The 'stereo' version of the
    // routine
    //
    // The best position is determined as the position where the two overlapped
    // sample sequences are 'most alike', in terms of the highest cross-correlation
    // value over the overlapping period
    private function seekBestOverlapPositionStereo(buffer:Vector.<Number>):int {
        var bestOffs:int;
        var bestCorr:Number
        var corr:Number;
        var i:int;

        // Slopes the amplitudes of the 'midBuffer' samples
        precalcCorrReferenceStereo();

        bestCorr = int.MIN_VALUE;
        bestOffs = 0;

        // Scans for the best correlation value by testing each possible position
        // over the permitted range.
        for (i = 0; i < seekLength; i ++)
        {
            // Calculates correlation value for the mixing position corresponding
            // to 'i'
            corr = calcCrossCorrStereo(buffer, 2 * i, pRefMidBuffer);

            // Checks for the highest correlation value
            if (corr > bestCorr)
            {
                bestCorr = corr;
                bestOffs = i;
            }
        }

        return bestOffs;
    }

    // Seeks for the optimal overlap-mixing position. The 'stereo' version of the
    // routine
    //
    // The best position is determined as the position where the two overlapped
    // sample sequences are 'most alike', in terms of the highest cross-correlation
    // value over the overlapping period
    private function seekBestOverlapPositionStereoQuick(buffer:Vector.<Number>):int
    {
        var j:int;
        var bestOffs:int;
        var bestCorr:Number;
        var corr:Number;
        var scanCount:int;
        var corrOffset:int;
        var tempOffset:int;

        // Slopes the amplitude of the 'midBuffer' samples
        precalcCorrReferenceStereo();

        bestCorr = int.MIN_VALUE;
        bestOffs = 0;
        corrOffset = 0;
        tempOffset = 0;

        // Scans for the best correlation value using four-pass hierarchical search.
        //
        // The look-up table 'scans' has hierarchical position adjusting steps.
        // In first pass the routine searhes for the highest correlation with
        // relatively coarse steps, then rescans the neighbourhood of the highest
        // correlation with better resolution and so on.
        for (scanCount = 0;scanCount < 4; scanCount ++)
        {
            j = 0;
            while (SCAN_OFFSETS[scanCount][j])
            {
                tempOffset = corrOffset + SCAN_OFFSETS[scanCount][j];
                if (tempOffset >= seekLength) break;

                // Calculates correlation value for the mixing position corresponding
                // to 'tempOffset'
                corr = calcCrossCorrStereo(buffer, 2 * tempOffset, pRefMidBuffer);

                // Checks for the highest correlation value
                if (corr > bestCorr)
                {
                    bestCorr = corr;
                    bestOffs = tempOffset;
                }
                j ++;
            }
            corrOffset = bestOffs;
        }

        return bestOffs;
    }

    // Slopes the amplitude of the 'midBuffer' samples so that cross correlation
    // is faster to calculate
    private function precalcCorrReferenceStereo():void {
        var i:int;
        var cnt2:int;
        var temp:int;

        for (i=0 ; i < int(overlapLength) ;i ++)
        {
            temp = Number(i) * Number(overlapLength - i);
            cnt2 = i * 2;
            pRefMidBuffer[cnt2] = Number(pMidBuffer[cnt2] * temp);
            pRefMidBuffer[cnt2 + 1] = Number(pMidBuffer[cnt2 + 1] * temp);
        }
    }

    private function calcCrossCorrStereo(mixing:Vector.<Number>, mixingPos:int, compare:Vector.<Number>):Number {
      var corr:Number;
      var i:int;
      var mixingOffset:int;

      corr = 0;
      for (i = 2; i < 2 * overlapLength; i += 2)
      {
        mixingOffset = i + mixingPos;
          corr += mixing[mixingOffset] * compare[i] +
                  mixing[mixingOffset + 1] * compare[i + 1];
      }

      return corr;
    }

    // TODO inline
    // Overlaps samples in 'midBuffer' with the samples in 'pInputBuffer' at position
    // of 'ovlPos'.
    private function overlap(pOutput:Vector.<Number>, pInput:Vector.<Number>, ovlPos:uint):void {
        overlapStereo(pOutput, pInput, 2 * ovlPos);
    }

    // Overlaps samples in 'midBuffer' with the samples in 'pInput'
    private function overlapStereo(pOutput:Vector.<Number>, pInput:Vector.<Number>, pInputPos:int):void {
      var i:int;
      var cnt2:int;
      var fTemp:Number;
      var fScale:Number;
      var fi:Number;
      var pInputOffset:int;

      fScale = 1 / Number(overlapLength);

      for (i = 0; i < int(overlapLength) ; i ++)
      {
          fTemp = Number(overlapLength - i) * fScale;
          fi = Number(i) * fScale;
          cnt2 = 2 * i;
          pInputOffset = cnt2 + pInputPos;
          pOutput[pOutput.length] = pInput[pInputOffset + 0] * fi + pMidBuffer[cnt2 + 0] * fTemp;
          pOutput[pOutput.length] = pInput[pInputOffset + 1] * fi + pMidBuffer[cnt2 + 1] * fTemp;
      }
    }

    private var sourcePosition:int = 0;
    public function process(target:ByteArray):Number {
      var ovlSkip:int;
      var offset:int;
      var temp:int;
      var bytes:ByteArray = new ByteArray();
      var i:int;

      if (pMidBuffer == null)
      {
        pMidBuffer = new Vector.<Number>();
        sourcePosition += _sound.extract(bytes, 2 * overlapLength * 4, sourcePosition); // channels * overlapLength * bytes/sample/channel
        bytes.position = 0;
        while (bytes.bytesAvailable > 0) {
          pMidBuffer.push(bytes.readFloat(), bytes.readFloat());
        }
      }

        var output:Vector.<Number> = new Vector.<Number>();
      // Process samples as long as there are enough samples in 'inputBuffer'
      // to form a processing frame.
      // FIXME handle input empty
      while (output.length < 4096)
      {
          var input:Vector.<Number> = new Vector.<Number>();
          bytes.position = 0;
          _sound.extract(bytes, sampleReq * 2, sourcePosition);
          bytes.position = 0;
          while (bytes.bytesAvailable > 0) {
            input.push(bytes.readFloat(), bytes.readFloat());
          }

          // If tempo differs from the normal ('SCALE'), scan for the best overlapping
          // position
          offset = seekBestOverlapPosition(input);

          // Mix the samples in the 'inputBuffer' at position of 'offset' with the
          // samples in 'midBuffer' using sliding overlapping
          // ... first partially overlap with the end of the previous sequence
          // (that's in 'midBuffer')
          overlap(output, input, uint(offset));

          // ... then copy sequence samples from 'inputBuffer' to output
          temp = (seekWindowLength - 2 * overlapLength);// & 0xfffffffe;
          if (temp > 0)
          {
            append(output, input, 2 * (offset + overlapLength), temp * 2);
          }

          // Copies the end of the current sequence from 'inputBuffer' to
          // 'midBuffer' for being mixed with the beginning of the next
          // processing sequence and so on
          //assert(offset + seekWindowLength <= (int)inputBuffer.numSamples());
          pMidBuffer = new Vector.<Number>();

          append(pMidBuffer, input, 2 * (offset + seekWindowLength - overlapLength), 8 * overlapLength);

          // Remove the processed samples from the input buffer. Update
          // the difference between integer & nominal skip step to 'skipFract'
          // in order to prevent the error from accumulating over time.
          skipFract += nominalSkip;   // real skip size
          ovlSkip = int(skipFract);   // rounded to integer skip
          skipFract -= ovlSkip;       // maintain the fraction part, i.e. real vs. integer skip
          sourcePosition += uint(ovlSkip);
      }

      // copy output buffer to target
      for (i = 0; i < output.length; i++) {
        target.writeFloat(output[i]);
      }

      return output.length / 2;
    }

    private function append(dest:Vector.<Number>, source:Vector.<Number>, offset:int, length:int):void {
      var max:int = offset + length;
      for (var i:int = offset; i < max; i++) {
        dest.push(source[i]);
      }
    }
  }
}
