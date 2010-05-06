/*
 *  Dirac_LE.h
 *  Dirac_LE_Lib
 *
 *  Created by Tristan Jehan on 4/15/10.
 *  Copyright 2010 The Echo Nest. All rights reserved.
 *
 *  IMPORTANT:  This file and its contents are subject to the terms set forth in the 
 *  "License Agreement.txt" file that accompanies this distribution.
 *
 *  Copyright © 2005-2010 Stephan M. Bernsee, http://www.dspdimension.com. All Rights Reserved
 */

#include "Dirac.h"
typedef unsigned int uint;

#define TIME 1.0f
#define QUALITY 0 // 0=decent/fast, 1=good/slow, 2=best/very_slow

// Utilities
float limiter(float val);
float **allocateAudioBuffer(uint numChannels, uint numFrames);
void deallocateAudioBuffer(float **samples, uint numChannels);
void interlace(float *out, float **in, uint numFrames, uint numChannels);
void deinterlace(float **out, float *in, uint numFrames, uint numChannels);

// This function time-stretches 'inDuration' seconds to a buffer of 'outDuration' seconds.
// It takes 'numChannels' from audio buffer 'inSamples' and writes the result into pre-allocated audio buffer 'outSamples'.
// 'quality' is an integer from 0 (lowest quality / fast processing) to 2 (highest quality / slow processing)
// returns 0 if everything went well and a negative eror number in case of a problem.
int time_scale(float **outSamples, double outDuration, float **inSamples, double inDuration, long numChannels, float sampleRate, uint quality=QUALITY);

// Same as above but with lists of times and durations as an input and durations as an output.
// We don't allow pitch-shifting in the case of a list because of unavoidable artifacts with the limitations of dirac LE.
int time_scale_list(float **outSamples, double *outDurations, float **inSamples, double *inDurations, uint numChunks, long numChannels, float sampleRate, uint quality=QUALITY);