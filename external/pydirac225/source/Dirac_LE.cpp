/*
 *  Dirac_LE.cpp
 *  Dirac_LE_Lib
 *
 *  Created by Tristan Jehan on 4/15/10.
 *  Copyright 2010 The Echo Nest. All rights reserved.
 *	
 *  IMPORTANT:  This file and its contents are subject to the terms set forth in the 
 *  "License Agreement.txt" file that accompanies this distribution.
 *
 *  Copyright © 2005-2010 Stephan M. Bernsee, http://www.dspdimension.com. All Rights Reserved
 *
 */

#include "Dirac_LE.h"
#include <math.h>
#include <algorithm>
#include <string.h>
#include <stdio.h>
#ifndef M_PI_2
#define M_PI_2  1.57079632679489661923 /* pi/2 */
#endif

using namespace std;

#define MAX_NUM_CHANNELS 2
#define PITCH 0.0f
#define FORMANT -0.0f
#define NUM_FRAMES_PER_READ 4096
#define SIZE_CROSSFADE 0.06 // in sec
#define CROSSFADE_COEFF 0.6
#define LIM_THRESH 0.95f
#define LIM_RANGE (1.0f - LIM_THRESH)

// Structure we pass to the callback function.
typedef struct 
{
	unsigned long sReadPosition[MAX_NUM_CHANNELS];
	long sMaxNumFrames;
	long sNumChannels;
	long sChannel;
	float **inData;
	
} userDataStruct;

// Utilities -- To remove by using interlace functionalities of dirac
void interlace(float *out, float **in, uint numFrames, uint numChannels)
{
	for (uint j=0; j<numChannels; j++)
		for (uint i=0; i<numFrames; i++)
			out[numChannels*i+j] = in[j][i];
}

void deinterlace(float **out, float *in, uint numFrames, uint numChannels)
{
	for (uint j=0; j<numChannels; j++)
		for (uint i=0; i<numFrames; i++)
			out[j][i] = in[numChannels*i+j];
}

float **allocateAudioBuffer(uint numChannels, uint numFrames)
{
	float **samples = (float **)malloc(numChannels * sizeof(float *));
	for (uint i=0; i<numChannels; i++)
		samples[i] = (float *)malloc(numFrames * sizeof(float));
	return samples;
}

void deallocateAudioBuffer(float **samples, uint numChannels)
{
	for (uint i=0; i<numChannels; i++)
		free(samples[i]);
	free(samples);
}

float limiter(float val)
{
	float res = 0;
	if (LIM_THRESH < val)
	{
		res = (val - LIM_THRESH) / LIM_RANGE;
		res = (atanf(res) / M_PI_2) * LIM_RANGE + LIM_THRESH;
	}
	else if (val < -LIM_THRESH)
	{
		res = - (val + LIM_THRESH) / LIM_RANGE;
		res = - ( (atanf(res) / M_PI_2) * LIM_RANGE + LIM_THRESH );
	}
	else 
	{
		res = val;
	}
	return res;
}

float logFactor(float val)
{
	return powf(val, CROSSFADE_COEFF);
}

float linear(float x1, float x2, long i, long n)
{
	float f_in  = float(i) / float(n-1);
	float f_out = float(n-i) / float(n);
	return f_out * x1 + f_in * x2;
}

float equal_power(float x1, float x2, long i, long n)
{
	float f_in  = float(i) / float(n-1);
	float f_out = float(n-i) / float(n);
	float val = logFactor(f_out) * x1 + logFactor(f_in) * x2;
	return limiter(val);
}

int crossFade(float **samplesOut, long outIndex, float **samplesIn, long inIndex, long numChannels, long numSamples)
{
	for (long i=0; i<numChannels; i++)
		for (long j=0; j<numSamples; j++)
			samplesOut[i][j+outIndex] = equal_power(samplesOut[i][j+outIndex], samplesIn[i][j+inIndex], j, numSamples);
	return numSamples;
}

// Callback function
long callback(float **chdata, long numFrames, void *userData)
{	
	if (!chdata) return 0;
	userDataStruct *state = (userDataStruct*)userData;
	if (!state)	return 0;	
	
	memcpy(&chdata[0][0], &state->inData[state->sChannel][state->sReadPosition[state->sChannel]], min((long)numFrames, (long)(state->sMaxNumFrames-state->sReadPosition[state->sChannel])) * sizeof(float));
	
	long new_pos = min((long)state->sReadPosition[state->sChannel] + numFrames, (long)state->sMaxNumFrames);
	long res = new_pos - state->sReadPosition[state->sChannel];
	state->sReadPosition[state->sChannel] = new_pos;
	
	return res;
}

int time_pitch_scale(float **outSamples, double outDuration, float **inSamples, double inDuration, long numChannels, float sampleRate, float pitch, bool smooth, uint quality)
{
	long counter[MAX_NUM_CHANNELS];
	void *dirac[MAX_NUM_CHANNELS];

	long outFrames = outDuration * sampleRate;
	long inFrames = inDuration * sampleRate;
	float time = outDuration/inDuration;
	float formant = pow(2., -pitch/12.);	// formant shift. Note formants are reciprocal to pitch in natural transposing.
	pitch = pow(2., pitch/12.);	// pitch shift
	
	userDataStruct state;
	state.sNumChannels = numChannels;
	state.sMaxNumFrames = inFrames;
	state.inData = inSamples;
	state.sChannel = 0;
	
	// We need one instance per channel with version LE
	for (long i=0; i<numChannels; i++)
	{
		if (quality == 1) dirac[i] = DiracCreate(kDiracLambda3, kDiracQualityGood, 1, sampleRate, &callback);
		else if (quality == 2) dirac[i] = DiracCreate(kDiracLambda3, kDiracQualityBest, 1, sampleRate, &callback);
		else dirac[i] = DiracCreate(kDiracLambdaPreview, kDiracQualityPreview, 1, sampleRate, &callback);

		if (!dirac[i]) 
		{
			printf("!! ERROR !!\n\n\tCould not create DIRAC instance\n\tCheck number of channels and sample rate!\n");
			printf("\n\tNote that the free DIRAC LE library supports only\n\tone channel per instance\n\n\n");
			return -1;
		}
		// Pass the values to our DIRAC instance 	
		DiracSetProperty(kDiracPropertyTimeFactor, time, dirac[i]);
		DiracSetProperty(kDiracPropertyPitchFactor, pitch, dirac[i]);
		DiracSetProperty(kDiracPropertyFormantFactor, formant, dirac[i]);
		state.sReadPosition[i] = 0;
		counter[i] = 0;
	}
	
	// Allocate buffer for output
	float **out = allocateAudioBuffer(1, NUM_FRAMES_PER_READ);
	
	// Processing
	while(1) 
	{
		bool done = false;
		for (long i=0; i<numChannels; i++)
		{
			// tell the callback function which channel to work on
			state.sChannel = i;
			// process the data
			long ret = DiracProcess(out, NUM_FRAMES_PER_READ, (void *)&state, dirac[i]);
			// copy to output buffer
            // Let's make sure we never go over buffer limits.
            if (outFrames < counter[i]+ret) 
                memcpy(&outSamples[i][counter[i]], &out[0][0], max(outFrames - counter[i], (long)0) * sizeof(float));
			else 
			    memcpy(&outSamples[i][counter[i]], &out[0][0], ret * sizeof(float));
    		// move on
			counter[i] += ret;
			if (ret <= 0) done = true;
		}
		
        // As soon as we've written enough frames we exit the main loop.
		if (done) {
			if (smooth)
			{	
				long sizeCrossfade = SIZE_CROSSFADE * sampleRate; // convert to number of samples
				long inIndex = inFrames - sizeCrossfade;
				long outIndex = outFrames - sizeCrossfade; // we assume the right number of samples out...
				
				if (inIndex < 0 || outIndex < 0)
				{
					sizeCrossfade += min(inIndex, outIndex);
					inIndex = inFrames - sizeCrossfade;
					outIndex = outFrames - sizeCrossfade;
				}

				if (crossFade(outSamples, outIndex, inSamples, inIndex, numChannels, sizeCrossfade) < 0)
				{
					printf("!! ERROR !!\n\n\tProblem cross-fading!\n");
					printf("\n\tNote that the free DIRAC LE library supports only\n\tone channel per instance\n\n\n");
					return -2;
				}
			}
			break;
		}
   	}
	
	deallocateAudioBuffer(out, 1);
	
	// destroy DIRAC instances
	for (long i=0; i<numChannels; i++)
		DiracDestroy(dirac[i]);
	
	return 0;
}

// assummes output audio buffers already allocated
int time_scale(float **outSamples, double outDuration, float **inSamples, double inDuration, long numChannels, float sampleRate, uint quality)
{
	return time_pitch_scale(outSamples, outDuration, inSamples, inDuration, numChannels, sampleRate, 0, true, quality);
}

int time_scale_list(float **outSamples, double *outDurations, float **inSamples, double *inDurations, uint numChunks, long numChannels, float sampleRate, uint quality)
{
	float **tmp_inSamples = (float **)malloc(numChannels * sizeof(float *));
	float **tmp_outSamples = (float **)malloc(numChannels * sizeof(float *));
	
	long counterIn = 0;
	long counterOut = 0;
	
	for (uint i=0; i<numChunks; i++)
	{			
		for (long j=0; j<numChannels; j++)
		{
			tmp_inSamples[j] = &inSamples[j][counterIn];
			tmp_outSamples[j] = &outSamples[j][counterOut];
		}
		
		if (time_scale(tmp_outSamples, outDurations[i], tmp_inSamples, inDurations[i], numChannels, sampleRate, quality) < 0)
		{
			printf("!! ERROR !!\n\n\tProblem with processing list.\n");
			return -1;
		}
		
		counterIn += (long)(inDurations[i] * sampleRate);
		counterOut += (long)(outDurations[i] * sampleRate);
	}

	free(tmp_inSamples);
	free(tmp_outSamples);
	
	return 0;
}
