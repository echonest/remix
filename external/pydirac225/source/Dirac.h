/*--------------------------------------------------------------------------------

 	Dirac.h
	
	Copyright (C) 2005-2010 The DSP Dimension,
	Stephan M. Bernsee (SMB)
	All rights reserved

	CONFIDENTIAL: This document contains confidential information. 
	Do not disclose any information contained in this document to any
	third-party without the prior written consent of Stephan M. Bernsee/
	The DSP Dimension.

    SMB 12-03-05        1.0.0     First source code distribution
    SMB 26-06-05        1.1.0     Fixed dynamic ts/ps (vh ref 0506261500)
    SMB 25-07-05        1.2.0     Implemented pitch correction (vh ref 0507251330)
    SMB 03-08-05        1.2.1     Optimized better and best quality modes (vh ref 0508031930)
    SMB 16-09-05        1.2.2     Reinstated formant handling (vh ref 0509161300)
                                  Extended ranges for pitch, time and formant handling to 10x/0.1x
	SMB 27-09-05		1.2.3	  Cleaned up code and reinstated package flags (vh ref 0509270830)
	SMB 19-10-05		1.2.4	  Removed obsolete code and fixed memory leaks (vh ref 0510191830)
	SMB 25-10-05		1.2.5	  Fixed interlaced channel callback on Windows (vh ref 0510251300)
	SMB 23-11-05		1.2.6	  Fixed quality problem in kDiracLambda1 for kDiracQualityBest
                                  Optimized formant handling
								  Formant correction now works correctly in kDiracLambda1 and
								  kDiracLambdaPreview (vh ref 0511231200)
    SMB 20-04-06        1.2.7     Several minor fixes for interlaced mode and memory allocation (vh ref 0604201500)
    SMB 24-04-06		1.2.8	  Fixed glitch at the beginning of the audio signal. DiracReset() should
    							  now be working more consistently (vh ref 0604241400)
    SMB 24-04-06		1.2.8r1	  Fixed glitch in sample rate converter and DiracReset() (vh ref 0604241700)
    SMB 25-04-06		1.2.9	  DiracReset() now has an option to clear its state buffers. Other minor fixes (vh ref 0604251000)
    SMB 06-08-08		1.3.0	  many minor bug fixes (vh ref 0711130830)
    SMB 06-08-08		1.4.0     many minor bug fixes, added Linux compatibility (vh ref 0808060830)
	SMB 17-05-09		1.5.0     bug fixes, increased precision, made calls ANSI C compatible  (vh ref 0905171330)

	SMB 06-10-09		2.0.0     First release of 2.0.0. See Changelog for details (vh ref 0909291600)
	SMB 08-10-09		2.0.1     fixed problem with disfunctional iPhone lib (vh ref 0910081200)
	SMB 08-10-09		2.0.2     fixed buffer overrun (vh ref 0910081500)
	SMB 03-11-09		2.1.0	  fixed formant correction. Fixed accumulating sample offset when pitch shifting. Added back in
								  pitch correction code. Numerous minor bug fixes (vh ref 0911061600)
	SMB 08-12-09		2.2.0	  Fixed volume offset for certain quality/lambda settings. Fixed excessive bass and DC response 
								  for frequencies < 20Hz, Fixed bug that caused the formant scaling to be always reciprocal to pitch in STUDIO
								  Optimized kDiracLambda1 (voice mode), (vh ref 0912080900)
	SMB 06-04-10		2.2.5	  Fixed bug that caused crash when using very low stretch ratios. Fixed bug in DiracReset() (vh ref 1004061715)

--------------------------------------------------------------------------------*/

// This file contains all the constants and prototypes for the "real" DIRAC calls
// that you will need in your project.


#ifndef __DIRAC__
#define __DIRAC__

	

// Windows DLL definitions
// ----------------------------------------------------------------------------

#ifndef TARGET_API_MAC_CARBON

	#ifdef DIRAC_AS_DLL
		#define DLL_DEF_TYPE __declspec(dllexport)
	#else
		#define DLL_DEF_TYPE
	#endif

#else
	#define DLL_DEF_TYPE __attribute__((visibility("default")))
#endif

// Function prototypes
// ----------------------------------------------------------------------------
#ifdef __cplusplus
extern "C" {
#endif
	
	DLL_DEF_TYPE const char *DiracVersion(void);
	DLL_DEF_TYPE void *DiracCreate(long lambda, long quality, long numChannels, float sampleRate, long (*readFromChannelsCallback)(float **data, long numFrames, void *userData));
	DLL_DEF_TYPE void *DiracCreateInterleaved(long lambda, long quality, long numChannels, float sampleRate, long (*readFromInterleavedChannelsCallback)(float *data, long numFrames, void *userData));
	DLL_DEF_TYPE long DiracSetProperty(long selector, long double value, void *dirac);
	DLL_DEF_TYPE long double DiracGetProperty(long selector, void *dirac);
	DLL_DEF_TYPE void DiracReset(bool clear, void *dirac);
	DLL_DEF_TYPE long DiracProcess(float **audioOut, long numFrames, void *userData, void *dirac);
	DLL_DEF_TYPE long DiracProcessInterleaved(float *audioOut, long numFrames, void *userData, void *dirac);
	DLL_DEF_TYPE void DiracDestroy(void *dirac);
	DLL_DEF_TYPE long DiracGetInputBufferSizeInFrames(void *dirac);
	DLL_DEF_TYPE long double DiracValidateStretchFactor(long double factor);
	
	// available in PRO only	
	DLL_DEF_TYPE long DiracSetTuningTable(float *frequencyTable, long numFrequencies, void *dirac);
	
	
#ifdef __cplusplus
}
#endif


// Property enums
// ----------------------------------------------------------------------------

enum
{
	kDiracPropertyPitchFactor = 100,
	kDiracPropertyTimeFactor,
	kDiracPropertyFormantFactor,
	kDiracPropertyCompactSupport,
	kDiracPropertyCacheGranularity,
	kDiracPropertyDoPitchCorrection,
	kDiracPropertyPitchCorrectionBasicTuningHz,
	kDiracPropertyPitchCorrectionSlurSpeed,
	kDiracPropertyPitchCorrectionDoFormantCorrection,
	kDiracPropertyPitchCorrectionFundamentalFrequency, /* experimental feature, use with caution */
	
	kDiracPropertyNumProperties
};



// Lambda enums
// ----------------------------------------------------------------------------

enum
{
	kDiracLambdaPreview = 200,
	kDiracLambda1,
	kDiracLambda2,
	kDiracLambda3,
	kDiracLambda4,
	kDiracLambda5,
	
	kDiracPropertyNumLambdas
};




// Quality enums
// ----------------------------------------------------------------------------

enum
{
	kDiracQualityPreview = 300,	
	kDiracQualityGood,
	kDiracQualityBetter,
	kDiracQualityBest,
	
	kDiracPropertyNumQualities
};




// Error enums
// ----------------------------------------------------------------------------
enum
{
	kDiracErrorNoErr		= 0,	
	kDiracErrorParamErr		= -1,
	kDiracErrorUnknownErr	= -2,
	kDiracErrorInvalidCb	= -3,
	kDiracErrorCacheErr		= -4,
	kDiracErrorNotInited	= -5,
	kDiracErrorMultipleInits	= -6,
	kDiracErrorFeatureNotSupported	= -7,
	kDiracErrorMemErr		= -108,
	
	kDiracErrorNumErrs
};





#endif /* __DIRAC__ */
