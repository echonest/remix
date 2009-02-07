/*
 *   Copyright (c) 2001-2002 Alexander Leidinger. All rights reserved.
 *
 *   Redistribution and use in source and binary forms, with or without
 *   modification, are permitted provided that the following conditions
 *   are met:
 *
 *   1. Redistributions of source code must retain the above copyright
 *      notice, this list of conditions and the following disclaimer.
 *   2. Redistributions in binary form must reproduce the above copyright
 *      notice, this list of conditions and the following disclaimer in the
 *      documentation and/or other materials provided with the distribution.
 *   
 *   THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
 *   ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 *   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 *   ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
 *   FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 *   DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
 *   OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 *   HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 *   LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
 *   OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
 *   SUCH DAMAGE.
 */

/* $Id: lamemodule.c,v 1.4 2003/06/17 09:07:51 aleidinger Exp $ */


#include <Python.h>
#include <lame/lame.h>
#include <stdio.h>


#ifdef __WIN32
#    define WIN_DLL_HELL _declspec(dllexport)
#else
#    define WIN_DLL_HELL
#endif

static void quiet_lib_printf( const char *format, va_list ap )
{
    return;
}

static PyObject *ErrorObject;

/* ----------------------------------------------------- */

/* Declarations for objects of type lame_encode */

typedef struct {
    PyObject_HEAD
    /* XXXX Add your own stuff here */
    PyObject*           mp3enc_attr;    /* Attributes dictionary */
    lame_global_flags*  gfp;
    char*               mp3_buf;
    int                 num_samples;
    int                 num_channels;
} mp3encobject;

staticforward PyTypeObject Mp3enctype;

#define mp3encobject_Check(v)    ((v)->ob_type == &Mp3enctype)

/* ---------------------------------------------------------------- */

static char mp3enc_encode__doc__[] = 
"Not implemented."
;

static PyObject *
mp3enc_encode(self, args)
        mp3encobject *self;
        PyObject *args;
{
        if (!PyArg_ParseTuple(args, ""))
                return NULL;
        Py_INCREF(Py_None);
        return Py_None;
}


static char mp3enc_encode_interleaved__doc__[] = 
"Encode interleaved audio data (2 channels, 16 bit per sample).\n"
"Parameter: audiodata\n"
"C function: lame_encode_buffer_interleaved()\n"
;
static PyObject *
mp3enc_encode_interleaved(self, args)
        mp3encobject *self;
        PyObject *args;
{
    int16_t* pcm;
    int      num_samples;
    int      mp3_data_size;

    if ( NULL == PyArg_ParseTuple( args, "s#", &pcm, &num_samples ) ) {
        return NULL;
    }

    if ( self->num_samples < num_samples ) {
	char *new_buf;
	
	new_buf = realloc( self->mp3_buf, 1.25*num_samples + 7200 );
	if ( NULL == new_buf ) {
	    PyErr_NoMemory();
	    return NULL;
	}
	
	self->mp3_buf     = new_buf;
	self->num_samples = num_samples;
    }

    mp3_data_size = lame_encode_buffer_interleaved(
                        self->gfp,
                        pcm,
                        num_samples / (self->num_channels * 2), /* 16bit! */
                        self->mp3_buf,
                        self->num_samples );

    if ( 0 > mp3_data_size ) {
        switch ( mp3_data_size ) {
            case -1:
                PyErr_SetString( (PyObject *)self,
                    "mp3buf too small (this shouldn't happen, please report)" );
                return NULL;
            case -2:
                PyErr_NoMemory();
                return NULL;
            case -3:
                PyErr_SetString( (PyObject *)self,
                    "init_parameters() not called (a bug in your program)" );
                return NULL;
            case -4:
                PyErr_SetString( (PyObject *)self,
                    "psycho acoustic problems" );
                return NULL;
            case -5:
                PyErr_SetString( (PyObject *)self,
                    "ogg cleanup encoding error (this shouldn't happen, there's no ogg support)" );
                return NULL;
            case -6:
                PyErr_SetString( (PyObject *)self,
                    "ogg frame encoding error (this shouldn't happen, there's no ogg support)" );
                return NULL;
            default:
                PyErr_SetString( (PyObject *)self,
                    "unknown error, please report" );
                return NULL;
        }
    }

    return Py_BuildValue( "s#", self->mp3_buf, mp3_data_size );
}


static char mp3enc_flush_buffers__doc__[] = 
"Encode remaining samples and flush the MP3 buffer.\n"
"No parameters.\n"
"C function: lame_encode_flush()\n"
;

static PyObject *
mp3enc_flush_buffers(self, args)
        mp3encobject *self;
        PyObject *args;
{
    int mp3_buf_fill_size;
    
    if (!PyArg_ParseTuple(args, ""))
            return NULL;

    mp3_buf_fill_size = lame_encode_flush( self->gfp, self->mp3_buf,
                                           self->num_samples );

    if ( 0 > mp3_buf_fill_size ) {
        switch ( mp3_buf_fill_size ) {
            case -1:
                PyErr_SetString( (PyObject *)self,
                    "mp3buf too small (this shouldn't happen, please report)" );
                return NULL;
            case -2:
                PyErr_NoMemory();
                return NULL;
            case -3:
                PyErr_SetString( (PyObject *)self,
                    "init_parameters() not called (a bug in your program)" );
                return NULL;
            case -4:
                PyErr_SetString( (PyObject *)self,
                    "psycho acoustic problems" );
                return NULL;
            case -5:
                PyErr_SetString( (PyObject *)self,
                    "ogg cleanup encoding error (this shouldn't happen, there's no ogg support)" );
                return NULL;
            case -6:
                PyErr_SetString( (PyObject *)self,
                    "ogg frame encoding error (this shouldn't happen, there's no ogg support)" );
                return NULL;
            default:
                PyErr_SetString( (PyObject *)self,
                    "unknown error, please report" );
                return NULL;
        }
    }

    return Py_BuildValue( "s#", self->mp3_buf, mp3_buf_fill_size );
}


static char mp3enc_delete__doc__[] = 
"Delete a MP3 encoder object.\n"
"No parameters.\n"
"C function: lame_close()\n"
;

static PyObject *
mp3enc_delete(self, args)
        mp3encobject *self;
        PyObject *args;
{
    if (!PyArg_ParseTuple(args, ""))
            return NULL;

    if ( NULL != self->gfp ) {
        lame_close( self->gfp );
        self->gfp = NULL;
    }

    if ( NULL != self->mp3_buf ) {
        free( self->mp3_buf );
        self->mp3_buf = NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_init_parameters__doc__[] =
"Initializates the internal state of LAME.\n"
"No paramteres. First you have to use the set_*() functions.\n"
"C function: lame_init_params()\n"
;

static PyObject *
mp3enc_init_parameters(self, args)
    mp3encobject *self;
    PyObject *args;
{
    if ( NULL == PyArg_ParseTuple( args, "" ) )
        return NULL;

    if ( NULL == self->mp3_buf ) {
	PyErr_SetString( (PyObject *)self, "no mp3 buffer" );
	return NULL;
    }
    
    if ( 0 > lame_init_params( self->gfp ) ) {
        PyErr_SetString( (PyObject *)self, "can't init parameters" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_num_samples__doc__[] =
"Set the number of samples.\n"
"Default: 2^32-1\n"
"Parameter: int\n"
"C function: lame_set_num_samples()\n"
;

static PyObject *
mp3enc_set_num_samples(self, args)
    mp3encobject *self;
    PyObject *args;
{
    unsigned long num_samples;

    if ( NULL == PyArg_ParseTuple( args, "l", &num_samples ) )
        return NULL;

    if ( 0 > lame_set_num_samples( self->gfp, num_samples ) ) {
        PyErr_SetString( (PyObject *)self, "can't set number of samples" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_in_samplerate__doc__[] =
"Set samplerate of infile (in Hz).\n"
"Default: 44100\n"
"Parameter: int\n"
"C function: lame_set_in_samplerate()\n"
;

static PyObject *
mp3enc_set_in_samplerate(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int in_samplerate;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &in_samplerate ) )
        return NULL;
    
    if ( 0 > lame_set_in_samplerate( self->gfp, in_samplerate ) ) {
        PyErr_SetString( (PyObject *)self, "can't set samplerate for infile" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_num_channels__doc__[] =
"Set number of channels of infile.\n"
"Default: 2\n"
"Parameter: int\n"
"C function: lame_set_num_channels()\n"
;

static PyObject *
mp3enc_set_num_channels(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int num_channels;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &num_channels ) )
        return NULL;
    
    if ( 0 > lame_set_num_channels( self->gfp, num_channels ) ) {
        PyErr_SetString( (PyObject *)self,
			 "can't set number of channels of infile" );
        return NULL;
    }

    self->num_channels = num_channels;
    
    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_scale__doc__[] =
"Scale the input by this amount before encoding.\n"
"Default: 0 (disabled)\n"
"Parameter: float\n"
"C function: lame_set_scale()\n"
;

static PyObject *
mp3enc_set_scale(self, args)
    mp3encobject *self;
    PyObject *args;
{
    float scale;
    
    if ( NULL == PyArg_ParseTuple( args, "f", &scale ) )
        return NULL;
    
    if ( 0 > lame_set_scale( self->gfp, scale ) ) {
        PyErr_SetString( (PyObject *)self, "can't set scaling" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_scale_left__doc__[] =
"Scale channel 0 (left) of the input by this amount before encoding.\n"
"Default: 0 (disabled)\n"
"Parameter: float\n"
"C function: lame_set_scale_left()\n"
;

static PyObject *
mp3enc_set_scale_left(self, args)
    mp3encobject *self;
    PyObject *args;
{
    float scale_left;
    
    if ( NULL == PyArg_ParseTuple( args, "f", &scale_left ) )
        return NULL;
    
    if ( 0 > lame_set_scale_left( self->gfp, scale_left ) ) {
        PyErr_SetString( (PyObject *)self, "can't set scaling for channel 0 (left)" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_scale_right__doc__[] =
"Scale channel 1 (right) of the input by this amount before encoding.\n"
"Default: 0 (disabled)\n"
"Parameter: float\n"
"C function: lame_set_scale_right()\n"
;

static PyObject *
mp3enc_set_scale_right(self, args)
    mp3encobject *self;
    PyObject *args;
{
    float scale_right;
    
    if ( NULL == PyArg_ParseTuple( args, "f", &scale_right ) )
        return NULL;
    
    if ( 0 > lame_set_scale_right( self->gfp, scale_right ) ) {
        PyErr_SetString( (PyObject *)self, "can't set scaling of channel 1 (right)" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_out_samplerate__doc__[] =
"Set output samplerate (in Hz).\n"
"Default: 0 (let LAME choose one)\n"
"Parameter: int\n"
"C function: lame_set_out_samplerate()\n"
;

static PyObject *
mp3enc_set_out_samplerate(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int out_samplerate;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &out_samplerate ) )
        return NULL;
    
    if ( 0 > lame_set_out_samplerate( self->gfp, out_samplerate ) ) {
        PyErr_SetString( (PyObject *)self, "can't set output samplerate" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_analysis__doc__[] =
"Collect data for an MP3 frame analyzer.\n"
"Default: 0 (disabled)\n"
"Parameter: int\n"
"C function: lame_set_analysis\n"
;

static PyObject *
mp3enc_set_analysis(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int analysis;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &analysis ) )
        return NULL;
    
    if ( 0 > lame_set_analysis( self->gfp, analysis ) ) {
        PyErr_SetString( (PyObject *)self, "can't set analysis mode" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_write_vbr_tag__doc__[] =
"Write a Xing VBR header frame.\n"
"Default: 1\n"
"Paramter: int\n"
"C function: lame_set_bWriteVbrTag()\n"
;

static PyObject *
mp3enc_set_write_vbr_tag(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int write_vbr_tag;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &write_vbr_tag ) )
        return NULL;
    
    if ( 0 > lame_set_bWriteVbrTag( self->gfp, write_vbr_tag ) ) {
        PyErr_SetString( (PyObject *)self, "can't set write_vbr_tag" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


#if 0    /* encode only at the moment! */
static char mp3enc_set_decode_only__doc__[] =
"Use LAME to decode MP3 to WAVE.\n"
"Default: 0 (disabled)\n"
"Parameter: int\n"
"C function: lame_set_decode_only()\n"
;

static PyObject *
mp3enc_set_decode_only(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int decode_only;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &decode_only ) )
        return NULL;
    
    if ( 0 > lame_set_decode_only( self->gfp, decode_only ) ) {
        PyErr_SetString( (PyObject *)self, "can't set decode only" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}
#endif


static char mp3enc_set_quality__doc__[] =
"Choose quality.\n"
"Range: 0 (best) - 9 (worst)\n"
"Parameter: int\n"
"C function: lame_set_quality()\n"
;

static PyObject *
mp3enc_set_quality(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int quality;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &quality ) )
        return NULL;
    
    if ( 0 > lame_set_quality( self->gfp, quality ) ) {
        PyErr_SetString( (PyObject *)self, "can't set quality" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_mode__doc__[] =
"Set mode.\n"
"Default: let LAME choose\n"
"Parameter: lame.STEREO, lame.JOINT_STEREO, lame.DUAL, lame.MONO\n"
"C function: lame_set_mode\n"
;

static PyObject *
mp3enc_set_mode(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int mode;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &mode ) )
        return NULL;
    
    if ( 0 > lame_set_mode( self->gfp, mode ) ) {
        PyErr_SetString( (PyObject *)self, "can't set mode" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_mode_automs__doc__[] =
"Use a M/S mode with a switching threshold based on compression ratio.\n"
"Default: 0 (disabled)\n"
"Parameter: int\n"
"C function: lame_set_mode_automs()\n"
;

static PyObject *
mp3enc_set_mode_automs(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int mode_automs;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &mode_automs ) )
        return NULL;
    
    if ( 0 > lame_set_mode_automs( self->gfp, mode_automs ) ) {
        PyErr_SetString( (PyObject *)self, "can't set mode_automs" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_force_ms__doc__[] =
"Force M/S for all frames (purpose: for testing only).\n"
"Default: 0 (disabled)\n"
"Parameter: int\n"
"C function: lame_set_force_ms()\n"
;

static PyObject *
mp3enc_set_force_ms(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int force_ms;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &force_ms ) )
        return NULL;
    
    if ( 0 > lame_set_force_ms( self->gfp, force_ms ) ) {
        PyErr_SetString( (PyObject *)self, "can't force all frames to M/S" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_free_format__doc__[] =
"Use free format.\n"
"Default: 0 (disabled)\n"
"Parameter: int\n"
"C function: lame_set_free_format()\n"
;

static PyObject *
mp3enc_set_free_format(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int free_format;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &free_format ) )
        return NULL;
    
    if ( 0 > lame_set_free_format( self->gfp, free_format ) ) {
        PyErr_SetString( (PyObject *)self, "can't set to free format" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_bitrate__doc__[] =
"Set bitrate.\n"
"Default: 128\n"
"Paramter: int\n"
"C function: lame_set_brate()\n"
;

static PyObject *
mp3enc_set_bitrate(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int brate;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &brate ) )
        return NULL;
    
    if ( 0 > lame_set_brate( self->gfp, brate ) ) {
        PyErr_SetString( (PyObject *)self, "can't set bitrate" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_compression_ratio__doc__[] =
"Set compression ratio.\n"
"Default: 11.0\n"
"Paramter: float\n"
"C function: lame_set_compression_ratio()\n"
;

static PyObject *
mp3enc_set_compression_ratio(self, args)
    mp3encobject *self;
    PyObject *args;
{
    float compression_ratio;
    
    if ( NULL == PyArg_ParseTuple( args, "f", &compression_ratio ) )
        return NULL;
    
    if ( 0 > lame_set_compression_ratio( self->gfp, compression_ratio ) ) {
        PyErr_SetString( (PyObject *)self, "can't set compression ratio" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_preset__doc__[] =
"Set a buildin preset.\n"
"Paramter: int (bitrate) or lame.PRESET_R3MIX, lame.PRESET_STANDARD,\n"
"          lame.PRESET_STANDARD_FAST, lame.PRESET_EXTREME,\n"
"          lame.PRESET_EXTREME_FAST, lame.PRESET_INSANE,\n"
"          lame.PRESET_MEDIUM, lame.PRESET_MEDIUM_FAST\n"
"C function: lame_set_preset()\n"
;

static PyObject *
mp3enc_set_preset(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int preset;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &preset ) )
        return NULL;
    
    if ( 0 > lame_set_preset( self->gfp, preset ) ) {
        PyErr_SetString( (PyObject *)self, "can't set preset" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_asm_optimizations__doc__[] =
"Disable specific asm optimizations (if compiled in).\n"
"Paramters: lame.ASM_MMX, lame.ASM_3DNOW, lame.ASM_SSE;\n"
"           int (0 = disable)\n"
"C function: lame_set_asm_optimizations()\n"
;

static PyObject *
mp3enc_set_asm_optimizations(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int val1, val2;
    
    if ( NULL == PyArg_ParseTuple( args, "ii", &val1, &val2 ) )
        return NULL;
    
    if ( 0 > lame_set_asm_optimizations( self->gfp, val1, val2 ) ) {
        PyErr_SetString( (PyObject *)self, "can't set asm optimizations" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_copyright__doc__[] =
"Set copyright bit.\n"
"Default: 0 (disabled)\n"
"Parameter: int\n"
"C function: lame_set_copyright()\n"
;

static PyObject *
mp3enc_set_copyright(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int copyright;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &copyright ) )
        return NULL;
    
    if ( 0 > lame_set_copyright( self->gfp, copyright ) ) {
        PyErr_SetString( (PyObject *)self, "can't set copyright bit" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_original__doc__[] =
"Set original bit.\n"
"Default: 1 (enabled)\n"
"Parameter: int\n"
"C function: lame_set_original()\n"
;

static PyObject *
mp3enc_set_original(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int original;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &original ) )
        return NULL;
    
    if ( 0 > lame_set_original( self->gfp, original ) ) {
        PyErr_SetString( (PyObject *)self, "can't set original bit" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_error_protection__doc__[] =
"Add error protection (uses 2 bytes from each frame for CRC).\n"
"Default: 0 (disabled)\n"
"Parameter: int\n"
"C function: lame_set_error_protection()\n"
;

static PyObject *
mp3enc_set_error_protection(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int error_protection;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &error_protection ) )
        return NULL;
    
    if ( 0 > lame_set_error_protection( self->gfp, error_protection ) ) {
        PyErr_SetString( (PyObject *)self, "can't set error protection" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_padding_type__doc__[] =
"Set padding type.\n"
"Default: lame.PAD_ADJUST\n"
"Paramter: lame.PAD_NO, lame.PAD_ALL, lame.PAD_ADJUST\n"
"C function: lame_set_padding_type()\n"
;

static PyObject *
mp3enc_set_padding_type(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int padding_type;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &padding_type ) )
        return NULL;
    
    if ( 0 > lame_set_padding_type( self->gfp, padding_type ) ) {
        PyErr_SetString( (PyObject *)self, "can't set padding type" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_extension__doc__[] =
"Set extension bit (meaningless).\n"
"Default: 0 (disabled)\n"
"Parameter: int\n"
"C function: lame_set_extension()\n"
;

static PyObject *
mp3enc_set_extension(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int extension;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &extension ) )
        return NULL;
    
    if ( 0 > lame_set_extension( self->gfp, extension ) ) {
        PyErr_SetString( (PyObject *)self, "can't set extension bit" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_strict_iso__doc__[] =
"Enforce strict ISO compliance.\n"
"Default: 0 (disabled)\n"
"Parameter: int\n"
"C function: lame_set_strict_ISO()\n"
;

static PyObject *
mp3enc_set_strict_iso(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int strict_iso;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &strict_iso ) )
        return NULL;
    
    if ( 0 > lame_set_strict_ISO( self->gfp, strict_iso ) ) {
        PyErr_SetString( (PyObject *)self, "can't set strict ISO compliance" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_disable_reservoir__doc__[] =
"Disable the bit reservoir (purpose: for testing only).\n"
"Default: 0 (disabled)\n"
"Parameter: int\n"
"C function: lame_set_disable_reservoir()\n"
;

static PyObject *
mp3enc_set_disable_reservoir(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int disable_reservoir;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &disable_reservoir ) )
        return NULL;
    
    if ( 0 > lame_set_disable_reservoir( self->gfp, disable_reservoir ) ) {
        PyErr_SetString( (PyObject *)self, "can't set disable_reservoir" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_exp_quantization__doc__[] =
"Select a different 'best quantization' function (experimental!).\n"
"Default: 0\n"
"Parameter: int\n"
"C function: lame_set_experimentalX()\n"
;

static PyObject *
mp3enc_set_exp_quantization(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int quantization;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &quantization ) )
        return NULL;
    
    if ( 0 > lame_set_experimentalX( self->gfp, quantization ) ) {
        PyErr_SetString( (PyObject *)self, "can't choose quantization function" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_exp_y__doc__[] =
"Experimental option.\n"
"Default: 0 (disabled)\n"
"Parameter: int\n"
"C function: lame_set_experimentalY()\n"
;

static PyObject *
mp3enc_set_exp_y(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int y;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &y ) )
        return NULL;
    
    if ( 0 > lame_set_experimentalY( self->gfp, y ) ) {
        PyErr_SetString( (PyObject *)self, "can't set exp_y" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_exp_z__doc__[] =
"Experimantal option.\n"
"Default: 0 (disabled)\n"
"Parameter: int\n"
"C function: lame_set_experimentalZ()\n"
;

static PyObject *
mp3enc_set_exp_z(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int z;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &z ) )
        return NULL;
    
    if ( 0 > lame_set_experimentalZ( self->gfp, z ) ) {
        PyErr_SetString( (PyObject *)self, "can't set exp_z" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_exp_nspsytune__doc__[] =
"Use Naoki's psycho acoustic model instead of GPSYCHO (experimental!).\n"
"Default: 0 (disabled)\n"
"Parameter: int\n"
"C function: lame_set_exp_nspsytune()\n"
;

static PyObject *
mp3enc_set_exp_nspsytune(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int nspsytune;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &nspsytune ) )
        return NULL;
    
    if ( 0 > lame_set_exp_nspsytune( self->gfp, nspsytune ) ) {
        PyErr_SetString( (PyObject *)self, "can't use nspsytune" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_vbr__doc__[] =
"Set VBR mode.\n"
"Default: lame.VBR_OFF (disabled)\n"
"Parameter: lame.VBR_OFF, lame.VBR_OLD, lame.VBR_ABR, lame.VBR_NEW,\n"
"           lame.VBR_DEFAULT\n"
"C function: lame_set_VBR()\n"
;

static PyObject *
mp3enc_set_vbr(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int vbr;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &vbr ) )
        return NULL;
    
    if ( 0 > lame_set_VBR( self->gfp, vbr ) ) {
        PyErr_SetString( (PyObject *)self, "can't set VBR mode" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_vbr_quality__doc__[] =
"Set VBR quality level.\n"
"Default: 4\n"
"Parameter: 0 (highest) - 9 (lowest)\n"
"C function: lame_set_VBR_q()\n"
;

static PyObject *
mp3enc_set_vbr_quality(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int vbr_quality;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &vbr_quality ) )
        return NULL;
    
    if ( 0 > lame_set_VBR_q( self->gfp, vbr_quality ) ) {
        PyErr_SetString( (PyObject *)self, "can't set VBR quality level" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_abr_bitrate__doc__[] =
"Set ABR bitrate.\n"
"Default: 128\n"
"Parameter: int\n"
"C function: lame_set_VBR_mean_bitrate_kbps()\n"
;

static PyObject *
mp3enc_set_abr_bitrate(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int abr_bitrate;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &abr_bitrate ) )
        return NULL;
    
    if ( 0 > lame_set_VBR_mean_bitrate_kbps( self->gfp, abr_bitrate ) ) {
        PyErr_SetString( (PyObject *)self, "can't set ABR bitrate" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_vbr_min_bitrate__doc__[] =
"Set minimal bitrate for ABR/VBR.\n"
"Default: lowest possible bitrate\n"
"Parameter: int\n"
"C function: lame_set_VBR_min_bitrate_kbps()\n"
;

static PyObject *
mp3enc_set_vbr_min_bitrate(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int vbr_min_bitrate;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &vbr_min_bitrate ) )
        return NULL;
    
    if ( 0 > lame_set_VBR_min_bitrate_kbps( self->gfp, vbr_min_bitrate ) ) {
        PyErr_SetString( (PyObject *)self, "can't set minimum bitrate" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_vbr_max_bitrate__doc__[] =
"Set maximal bitrate for ABR/VBR.\n"
"Default: highest possible bitrate\n"
"Parameter: int\n"
"C function: lame_set_VBR_max_bitrate_kbps()\n"
;

static PyObject *
mp3enc_set_vbr_max_bitrate(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int vbr_max_bitrate;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &vbr_max_bitrate ) )
        return NULL;
    
    if ( 0 > lame_set_VBR_max_bitrate_kbps( self->gfp, vbr_max_bitrate ) ) {
        PyErr_SetString( (PyObject *)self, "can't set maximal bitrate" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_vbr_min_enforce__doc__[] =
"Enforce minimum bitrate for ABR/VBR, normally it will be violated for\n"
"analog silence.\n"
"Default: 0 (disabled)\n"
"Parameter: int\n"
"C function: lame_set_VBR_hard_min()\n"
;

static PyObject *
mp3enc_set_vbr_min_enforce(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int vbr_min_enforce;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &vbr_min_enforce ) )
        return NULL;
    
    if ( 0 > lame_set_VBR_hard_min( self->gfp, vbr_min_enforce ) ) {
        PyErr_SetString( (PyObject *)self, "can't enforce minimal bitrate" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_lowpass_frequency__doc__[] =
"Lowpass frequency in Hz (-1: disabled).\n"
"Default: 0 (LAME chooses)\n"
"Parameter: int\n"
"C function: lame_set_lowpassfreq()\n"
;

static PyObject *
mp3enc_set_lowpass_frequency(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int lowpass_frequency;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &lowpass_frequency ) )
        return NULL;
    
    if ( 0 > lame_set_lowpassfreq( self->gfp, lowpass_frequency ) ) {
        PyErr_SetString( (PyObject *)self, "can't set lowpass frequency" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_lowpass_width__doc__[] =
"Width of transition band in Hz.\n"
"Default: one polyphase filter band\n"
"Parameter: int\n"
"C function: lame_set_lowpasswidth()\n"
;

static PyObject *
mp3enc_set_lowpass_width(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int lowpass_width;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &lowpass_width ) )
        return NULL;
    
    if ( 0 > lame_set_lowpasswidth( self->gfp, lowpass_width ) ) {
        PyErr_SetString( (PyObject *)self, "can't set width of lowpass" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_highpass_frequency__doc__[] =
"Highpass frequency in Hz (-1: disabled).\n"
"Default: 0 (LAME chooses)\n"
"Parameter: int\n"
"C function: lame_set_highpassfreq()\n"
;

static PyObject *
mp3enc_set_highpass_frequency(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int highpass_frequency;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &highpass_frequency ) )
        return NULL;
    
    if ( 0 > lame_set_highpassfreq( self->gfp, highpass_frequency ) ) {
        PyErr_SetString( (PyObject *)self, "can't set highpass frequency" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_highpass_width__doc__[] =
"Set width of highpass in Hz.\n"
"Default: one polyphase filter band\n"
"Parameter: int\n"
"C function: lame_set_highpasswidth()\n"
;

static PyObject *
mp3enc_set_highpass_width(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int highpass_width;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &highpass_width ) )
        return NULL;
    
    if ( 0 > lame_set_highpasswidth( self->gfp, highpass_width ) ) {
        PyErr_SetString( (PyObject *)self, "can't set highpass width" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_ath_for_masking_only__doc__[] =
"Only use ATH for masking.\n"
"Default: 0 (disabled)\n"
"Parameter: int\n"
"C function: lame_set_ATHonly()\n"
;

static PyObject *
mp3enc_set_ath_for_masking_only(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int ath_for_masking_only;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &ath_for_masking_only) )
        return NULL;
    
    if ( 0 > lame_set_ATHonly( self->gfp, ath_for_masking_only ) ) {
        PyErr_SetString( (PyObject *)self, "can't set ath_for_masking_only" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_ath_for_short_only__doc__[] =
"Only use ATH for short blocks.\n"
"Default: 0 (disabled)\n"
"Parameter: int\n"
"C function: lame_set_ATHshort()\n"
;

static PyObject *
mp3enc_set_ath_for_short_only(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int ath_for_short_only;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &ath_for_short_only ) )
        return NULL;
    
    if ( 0 > lame_set_ATHshort( self->gfp, ath_for_short_only ) ) {
        PyErr_SetString( (PyObject *)self, "can't set ath_for_short_only" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_ath_disable__doc__[] =
"Disable ATH.\n"
"Default: 0 (use ATH)\n"
"Parameter: int\n"
"C function: lame_set_noATH()\n"
;

static PyObject *
mp3enc_set_ath_disable(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int ath_disable;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &ath_disable ) )
        return NULL;
    
    if ( 0 > lame_set_noATH( self->gfp, ath_disable ) ) {
        PyErr_SetString( (PyObject *)self, "can't disable ATH" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_ath_type__doc__[] =
"Select type of ATH.\n"
"Default: XXX\n"
"Parameter: int  XXX should be lame.YYY\n"
"C function: lame_set_ATHtype()\n"
;

static PyObject *
mp3enc_set_ath_type(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int ath_type;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &ath_type ) )
        return NULL;
    
    if ( 0 > lame_set_ATHtype( self->gfp, ath_type ) ) {
        PyErr_SetString( (PyObject *)self, "can't set ATH type" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_ath_lower__doc__[] =
"Lower ATH by this many dB.\n"
"Default: 0\n"
"Parameter: int\n"
"C function: lame_set_ATHlower()\n"
;

static PyObject *
mp3enc_set_ath_lower(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int ath_lower;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &ath_lower ) )
        return NULL;
    
    if ( 0 > lame_set_ATHlower( self->gfp, ath_lower ) ) {
        PyErr_SetString( (PyObject *)self, "can't lower ATH" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_athaa_type__doc__[] =
"Select type of ATH adaptive adjustment.\n"
"Default: XXX\n"
"Parameter: int  XXX should be lame.YYY\n"
"C function: lame_set_athaa_type()\n"
;

static PyObject *
mp3enc_set_athaa_type(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int athaa_type;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &athaa_type ) )
        return NULL;
    
    if ( 0 > lame_set_athaa_type( self->gfp, athaa_type ) ) {
        PyErr_SetString( (PyObject *)self, "can't select type of ATH adaptive adjustment" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_athaa_loudness_approximation__doc__[] =
"Choose the loudness approximation used by the ATH adaptive auto leveling.\n"
"Default: XXX\n"
"Parameter: int  XXX should be lame.YYY\n"
"C function: lame_set_athaa_loudapprox()\n"
;

static PyObject *
mp3enc_set_athaa_loudness_approximation(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int athaa_loudness_approximation;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &athaa_loudness_approximation ) )
        return NULL;
    
    if ( 0 > lame_set_athaa_loudapprox( self->gfp, athaa_loudness_approximation ) ) {
        PyErr_SetString( (PyObject *)self, "can't set loudness approximation" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_athaa_sensitivity__doc__[] =
"Adjust the point below which adaptive ATH level adjustment occurs (in dB).\n"
"Default: 0\n"
"Parameter: int\n"
"C function: lame_set_athaa_sensitivity()\n"
;

static PyObject *
mp3enc_set_athaa_sensitivity(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int athaa_sensitivity;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &athaa_sensitivity ) )
        return NULL;
    
    if ( 0 > lame_set_athaa_sensitivity( self->gfp, athaa_sensitivity ) ) {
        PyErr_SetString( (PyObject *)self, "can't set ATHaa sensitivity" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_predictability_limit__doc__[] =
"Predictability limit for the ISO tonality formula.\n"
"Default: XXX\n"
"Parameter: int\n"
"C function: lame_set_cwlimit()\n"
;

static PyObject *
mp3enc_set_predictability_limit(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int predictability_limit;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &predictability_limit ) )
        return NULL;
    
    if ( 0 > lame_set_cwlimit( self->gfp, predictability_limit ) ) {
        PyErr_SetString( (PyObject *)self, "can't set predictability limit for ISO tonality formula" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_allow_blocktype_difference__doc__[] =
"Allow blocktypes to differ between channels.\n"
"Default: 0 (disabled) for JOINT_STEREO, 1 (enabled) for STEREO\n"
"Parameter: int\n"
"C function: lame_set_allow_diff_short()\n"
;

static PyObject *
mp3enc_set_allow_blocktype_difference(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int allow_blocktype_difference;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &allow_blocktype_difference ) )
        return NULL;
    
    if ( 0 > lame_set_allow_diff_short( self->gfp, allow_blocktype_difference ) ) {
        PyErr_SetString( (PyObject *)self, "can't set allow_blocktype_difference" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_use_temporal_masking__doc__[] =
"Use temporal masking.\n"
"Default: 1 (enabled)\n"
"Parameter: int\n"
"C function: lame_set_useTemporal()\n"
;

static PyObject *
mp3enc_set_use_temporal_masking(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int use_temporal_masking;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &use_temporal_masking ) )
        return NULL;
    
    if ( 0 > lame_set_useTemporal( self->gfp, use_temporal_masking ) ) {
        PyErr_SetString( (PyObject *)self, "can't change temporal masking" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_inter_channel_ratio__doc__[] =
"Set inter channel ratio.\n"
"Default: XXX\n"
"Parameter: float\n"
"C function: lame_set_interChRatio()\n"
;

static PyObject *
mp3enc_set_inter_channel_ratio(self, args)
    mp3encobject *self;
    PyObject *args;
{
    float inter_channel_ratio;
    
    if ( NULL == PyArg_ParseTuple( args, "f", &inter_channel_ratio ) )
        return NULL;
    
    if ( 0 > lame_set_interChRatio( self->gfp, inter_channel_ratio ) ) {
        PyErr_SetString( (PyObject *)self, "can't change inter channel ratio" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_substep__doc__[] =
"Set substep shaping method.\n"
"Default: XXX\n"
"Parameter: int  XXX should be lame.YYY\n"
"C function: lame_set_substep()\n"
;

static PyObject *
mp3enc_set_substep(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int substep;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &substep ) )
        return NULL;
    
    if ( 0 > lame_set_substep( self->gfp, substep ) ) {
        PyErr_SetString( (PyObject *)self, "can't change substep shaping method" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_no_short_blocks__doc__[] =
"Disable the use of short blocks.\n"
"Default: 0 (use short blocks)\n"
"Parameter: int\n"
"C function: lame_set_no_short_blocks()\n"
;

static PyObject *
mp3enc_set_no_short_blocks(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int no_short_blocks;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &no_short_blocks ) )
        return NULL;
    
    if ( 0 > lame_set_no_short_blocks( self->gfp, no_short_blocks ) ) {
        PyErr_SetString( (PyObject *)self, "can't change the use of short blocks" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_force_short_blocks__doc__[] =
"Force the use of short blocks.\n"
"Default: 0 (disabled)\n"
"Parameter: int\n"
"C function: lame_set_force_short_blocks()\n"
;

static PyObject *
mp3enc_set_force_short_blocks(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int force_short_blocks;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &force_short_blocks ) )
        return NULL;
    
    if ( 0 > lame_set_force_short_blocks( self->gfp, force_short_blocks ) ) {
        PyErr_SetString( (PyObject *)self, "can't force short blocks" );
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_get_frame_num__doc__[] =
"Get number of encoded frames so far.\n"
"C function: lame_get_frameNum()"
;

static PyObject *
mp3enc_get_frame_num(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int frame_num;
    
    if ( NULL == PyArg_ParseTuple( args, "" ) )
        return NULL;
    
    frame_num = lame_get_frameNum( self->gfp );

    return Py_BuildValue( "i", frame_num );
}


static char mp3enc_get_total_frames__doc__[] =
"Get estimate of the total number of frames to be encoded, only valid if\n"
"the calling program set num_samples.\n"
"C function: lame_get_totalframes()\n"
;

static PyObject *
mp3enc_get_total_frames(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int total_frames;
    
    if ( NULL == PyArg_ParseTuple( args, "" ) )
        return NULL;
    
    total_frames = lame_get_totalframes( self->gfp );

    return Py_BuildValue( "i", total_frames );
}


static char mp3enc_get_bitrate_histogram__doc__[] =
"Get tuple of histogram dictionaries with bitrate/value keys.\n"
"C functions: lame_bitrate_kbps(), lame_bitrate_hist()\n"
;

static PyObject *
mp3enc_get_bitrate_histogram(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int bitrate_count[14];
    int bitrate_value[14];
    
    if ( NULL == PyArg_ParseTuple( args, "" ) )
        return NULL;
    
    lame_bitrate_kbps( self->gfp, bitrate_value );
    lame_bitrate_hist( self->gfp, bitrate_count );

    return Py_BuildValue( "({sisi}{sisi}{sisi}{sisi}{sisi}{sisi}{sisi}{sisi}{sisi}{sisi}{sisi}{sisi}{sisi}{sisi})",
			  "bitrate", bitrate_value[ 0],
			  "value"  , bitrate_count[ 0],
			  "bitrate", bitrate_value[ 1],
			  "value"  , bitrate_count[ 1],
			  "bitrate", bitrate_value[ 2],
			  "value"  , bitrate_count[ 2],
			  "bitrate", bitrate_value[ 3],
			  "value"  , bitrate_count[ 3],
			  "bitrate", bitrate_value[ 4],
			  "value"  , bitrate_count[ 4],
			  "bitrate", bitrate_value[ 5],
			  "value"  , bitrate_count[ 5],
			  "bitrate", bitrate_value[ 6],
			  "value"  , bitrate_count[ 6],
			  "bitrate", bitrate_value[ 7],
			  "value"  , bitrate_count[ 7],
			  "bitrate", bitrate_value[ 8],
			  "value"  , bitrate_count[ 8],
			  "bitrate", bitrate_value[ 9],
			  "value"  , bitrate_count[ 9],
			  "bitrate", bitrate_value[10],
			  "value"  , bitrate_count[10],
			  "bitrate", bitrate_value[11],
			  "value"  , bitrate_count[11],
			  "bitrate", bitrate_value[12],
			  "value"  , bitrate_count[12],
			  "bitrate", bitrate_value[13],
			  "value"  , bitrate_count[13] );
}


static char mp3enc_get_bitrate_values__doc__[] =
"Get tuple of possible bitrates.\n"
"C function: lame_bitrate_kbps()\n"
;

static PyObject *
mp3enc_get_bitrate_values(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int bitrate_count[14];
    
    if ( NULL == PyArg_ParseTuple( args, "" ) )
        return NULL;
    
    lame_bitrate_kbps( self->gfp, bitrate_count );

    return Py_BuildValue( "(iiiiiiiiiiiiii)",
			  bitrate_count[ 0],
			  bitrate_count[ 1],
			  bitrate_count[ 2],
			  bitrate_count[ 3],
			  bitrate_count[ 4],
			  bitrate_count[ 5],
			  bitrate_count[ 6],
			  bitrate_count[ 7],
			  bitrate_count[ 8],
			  bitrate_count[ 9],
			  bitrate_count[10],
			  bitrate_count[11],
			  bitrate_count[12],
			  bitrate_count[13] );
}


static char mp3enc_get_bitrate_stereo_mode_histogram__doc__[] =
"Get tuple of dictionaries for stereo mode histogram with LR/LR-I/MS/MS-I keys.\n"
"C function: lame_bitrate_stereo_mode_hist()\n"
;

static PyObject *
mp3enc_get_bitrate_stereo_mode_histogram(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int bitrate_stmode_count[14][4];
    
    if ( NULL == PyArg_ParseTuple( args, "" ) )
        return NULL;
    
    lame_bitrate_stereo_mode_hist( self->gfp, bitrate_stmode_count );

    return Py_BuildValue( "({sisisisi}{sisisisi}{sisisisi}{sisisisi}{sisisisi}{sisisisi}{sisisisi}{sisisisi}{sisisisi}{sisisisi}{sisisisi}{sisisisi}{sisisisi}{sisisisi})",
			  "LR"  , bitrate_stmode_count[ 0][0],
			  "LR-I", bitrate_stmode_count[ 0][1],
			  "MS"  , bitrate_stmode_count[ 0][2],
			  "MS-I", bitrate_stmode_count[ 0][3],
			  "LR"  , bitrate_stmode_count[ 1][0],
			  "LR-I", bitrate_stmode_count[ 1][1],
			  "MS"  , bitrate_stmode_count[ 1][2],
			  "MS-I", bitrate_stmode_count[ 1][3],
			  "LR"  , bitrate_stmode_count[ 2][0],
			  "LR-I", bitrate_stmode_count[ 2][1],
			  "MS"  , bitrate_stmode_count[ 2][2],
			  "MS-I", bitrate_stmode_count[ 2][3],
			  "LR"  , bitrate_stmode_count[ 3][0],
			  "LR-I", bitrate_stmode_count[ 3][1],
			  "MS"  , bitrate_stmode_count[ 3][2],
			  "MS-I", bitrate_stmode_count[ 3][3],
			  "LR"  , bitrate_stmode_count[ 4][0],
			  "LR-I", bitrate_stmode_count[ 4][1],
			  "MS"  , bitrate_stmode_count[ 4][2],
			  "MS-I", bitrate_stmode_count[ 4][3],
			  "LR"  , bitrate_stmode_count[ 5][0],
			  "LR-I", bitrate_stmode_count[ 5][1],
			  "MS"  , bitrate_stmode_count[ 5][2],
			  "MS-I", bitrate_stmode_count[ 5][3],
			  "LR"  , bitrate_stmode_count[ 6][0],
			  "LR-I", bitrate_stmode_count[ 6][1],
			  "MS"  , bitrate_stmode_count[ 6][2],
			  "MS-I", bitrate_stmode_count[ 6][3],
			  "LR"  , bitrate_stmode_count[ 7][0],
			  "LR-I", bitrate_stmode_count[ 7][1],
			  "MS"  , bitrate_stmode_count[ 7][2],
			  "MS-I", bitrate_stmode_count[ 7][3],
			  "LR"  , bitrate_stmode_count[ 8][0],
			  "LR-I", bitrate_stmode_count[ 8][1],
			  "MS"  , bitrate_stmode_count[ 8][2],
			  "MS-I", bitrate_stmode_count[ 8][3],
			  "LR"  , bitrate_stmode_count[ 9][0],
			  "LR-I", bitrate_stmode_count[ 9][1],
			  "MS"  , bitrate_stmode_count[ 9][2],
			  "MS-I", bitrate_stmode_count[ 9][3],
			  "LR"  , bitrate_stmode_count[10][0],
			  "LR-I", bitrate_stmode_count[10][1],
			  "MS"  , bitrate_stmode_count[10][2],
			  "MS-I", bitrate_stmode_count[10][3],
			  "LR"  , bitrate_stmode_count[11][0],
			  "LR-I", bitrate_stmode_count[11][1],
			  "MS"  , bitrate_stmode_count[11][2],
			  "MS-I", bitrate_stmode_count[11][3],
			  "LR"  , bitrate_stmode_count[12][0],
			  "LR-I", bitrate_stmode_count[12][1],
			  "MS"  , bitrate_stmode_count[12][2],
			  "MS-I", bitrate_stmode_count[12][3],
			  "LR"  , bitrate_stmode_count[13][0],
			  "LR-I", bitrate_stmode_count[13][1],
			  "MS"  , bitrate_stmode_count[13][2],
			  "MS-I", bitrate_stmode_count[13][3] );
}


static char mp3enc_get_stereo_mode_histogram__doc__[] =
"Get dictionary for stereo mode histogram with LR/LR-I/MS/MS-I keys.\n"
"C function: lame_stereo_mode_hist()\n"
;

static PyObject *
mp3enc_get_stereo_mode_histogram(self, args)
    mp3encobject *self;
    PyObject *args;
{
    int stmode_count[4];
    
    if ( NULL == PyArg_ParseTuple( args, "" ) )
        return NULL;
    
    lame_stereo_mode_hist( self->gfp, stmode_count );

    return Py_BuildValue( "{sisisisi}",
			  "LR"  , stmode_count[0],
			  "LR-I", stmode_count[1],
			  "MS"  , stmode_count[2],
			  "MS-I", stmode_count[3] );
}


static char mp3enc_set_exp_msfix__doc__[] =
"Undocumented, don't use.\n"
"Parameter: double\n"
"C function: lame_set_msfix()\n"
;

extern void lame_set_msfix( lame_t, double );

static PyObject *
mp3enc_set_exp_msfix(self, args)
    mp3encobject *self;
    PyObject *args;
{
    double msfix;
    
    if ( NULL == PyArg_ParseTuple( args, "d", &msfix ) )
        return NULL;

    lame_set_msfix( self->gfp, msfix );

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_set_exp_preset_expopts__doc__[] =
"Undocumented, don't use.\n"
"Parameter: int\n"
"C function: lame_set_preset_expopts()\n"
;

extern int lame_set_preset_expopts( lame_t, int );

static PyObject *
mp3enc_set_exp_preset_expopts(self, args)
    mp3encobject *self;
    PyObject *args;
{
    double preset_expopts;
    
    if ( NULL == PyArg_ParseTuple( args, "i", &preset_expopts ) )
        return NULL;

    lame_set_preset_expopts( self->gfp, preset_expopts );

    Py_INCREF(Py_None);
    return Py_None;
}


static char mp3enc_write_tags__doc__[] =
"Write ID3v1 TAG's.\n"
"Parameter: file\n"
"C function: lame_mp3_tags_fid()\n"
;

static PyObject *
mp3enc_write_tags(self, args)
    mp3encobject *self;
    PyObject *args;
{
    PyObject *object;
    FILE *mp3_file;
    
    if ( NULL == PyArg_ParseTuple( args, "O", &object ) )
        return NULL;

    if ( 0 == PyFile_Check( object ) )
	return NULL;
    
    mp3_file = PyFile_AsFile( object );
    
    lame_mp3_tags_fid( self->gfp, mp3_file );

    Py_INCREF(Py_None);
    return Py_None;
}


static struct PyMethodDef mp3enc_methods[] = {
    {"encode", (PyCFunction)mp3enc_encode,
        METH_VARARGS, mp3enc_encode__doc__                           },
    {"encode_interleaved", (PyCFunction)mp3enc_encode_interleaved,
        METH_VARARGS, mp3enc_encode_interleaved__doc__               },
    {"flush_buffers", (PyCFunction)mp3enc_flush_buffers,
	METH_VARARGS, mp3enc_flush_buffers__doc__                    },
    {"delete", (PyCFunction)mp3enc_delete,
        METH_VARARGS, mp3enc_delete__doc__                           },
    {"init_parameters", (PyCFunction)mp3enc_init_parameters,
	METH_VARARGS, mp3enc_init_parameters__doc__                  },
    {"set_num_samples", (PyCFunction)mp3enc_set_num_samples,
	METH_VARARGS, mp3enc_set_num_samples__doc__                  },
    {"set_in_samplerate", (PyCFunction)mp3enc_set_in_samplerate,
	METH_VARARGS, mp3enc_set_in_samplerate__doc__                },
    {"set_num_channels", (PyCFunction)mp3enc_set_num_channels,
	METH_VARARGS, mp3enc_set_num_channels__doc__                 },
    {"set_scale", (PyCFunction)mp3enc_set_scale,
	METH_VARARGS, mp3enc_set_scale__doc__                        },
    {"set_scale_left", (PyCFunction)mp3enc_set_scale_left,
	METH_VARARGS, mp3enc_set_scale_left__doc__                   },
    {"set_scale_right", (PyCFunction)mp3enc_set_scale_right,
	METH_VARARGS, mp3enc_set_scale_right__doc__                  },
    {"set_out_samplerate", (PyCFunction)mp3enc_set_out_samplerate,
	METH_VARARGS, mp3enc_set_out_samplerate__doc__               },
    {"set_analysis", (PyCFunction)mp3enc_set_analysis,
	METH_VARARGS, mp3enc_set_analysis__doc__                     },
    {"set_write_vbr_tag", (PyCFunction)mp3enc_set_write_vbr_tag,
	METH_VARARGS, mp3enc_set_write_vbr_tag__doc__                },
#if 0
    {"set_decode_only", (PyCFunction)mp3enc_set_decode_only,
	METH_VARARGS, mp3enc_set_decode_only__doc__                  },
#endif
    {"set_quality", (PyCFunction)mp3enc_set_quality,
	METH_VARARGS, mp3enc_set_quality__doc__                       },
    {"set_mode", (PyCFunction)mp3enc_set_mode,
	METH_VARARGS, mp3enc_set_mode__doc__                          },
    {"set_mode_automs", (PyCFunction)mp3enc_set_mode_automs,
	METH_VARARGS, mp3enc_set_mode_automs__doc__                   },
    {"set_force_ms", (PyCFunction)mp3enc_set_force_ms,
	METH_VARARGS, mp3enc_set_force_ms__doc__                      },
    {"set_free_format", (PyCFunction)mp3enc_set_free_format,
	METH_VARARGS, mp3enc_set_free_format__doc__                   },
    {"set_bitrate", (PyCFunction)mp3enc_set_bitrate,
	METH_VARARGS, mp3enc_set_bitrate__doc__                       },
    {"set_compression_ratio", (PyCFunction)mp3enc_set_compression_ratio,
	METH_VARARGS, mp3enc_set_compression_ratio__doc__             },
    {"set_preset", (PyCFunction)mp3enc_set_preset,
	METH_VARARGS, mp3enc_set_preset__doc__                        },
    {"set_asm_optimizations", (PyCFunction)mp3enc_set_asm_optimizations,
	METH_VARARGS, mp3enc_set_asm_optimizations__doc__             },
    {"set_copyright", (PyCFunction)mp3enc_set_copyright,
	METH_VARARGS, mp3enc_set_copyright__doc__                     },
    {"set_original", (PyCFunction)mp3enc_set_original,
	METH_VARARGS, mp3enc_set_original__doc__                      },
    {"set_error_protection", (PyCFunction)mp3enc_set_error_protection,
	METH_VARARGS, mp3enc_set_error_protection__doc__              },
    {"set_padding_type", (PyCFunction)mp3enc_set_padding_type,
	METH_VARARGS, mp3enc_set_padding_type__doc__                  },
    {"set_extension", (PyCFunction)mp3enc_set_extension,
	METH_VARARGS, mp3enc_set_extension__doc__                     },
    {"set_strict_iso", (PyCFunction)mp3enc_set_strict_iso,
	METH_VARARGS, mp3enc_set_strict_iso__doc__                    },
    {"set_disable_reservoir", (PyCFunction)mp3enc_set_disable_reservoir,
	METH_VARARGS, mp3enc_set_disable_reservoir__doc__             },
    {"set_exp_quantization", (PyCFunction)mp3enc_set_exp_quantization,
	METH_VARARGS, mp3enc_set_exp_quantization__doc__              },
    {"set_exp_y", (PyCFunction)mp3enc_set_exp_y,
	METH_VARARGS, mp3enc_set_exp_y__doc__                         },
    {"set_exp_z", (PyCFunction)mp3enc_set_exp_z,
	METH_VARARGS, mp3enc_set_exp_z__doc__                         },
    {"set_exp_nspsytune", (PyCFunction)mp3enc_set_exp_nspsytune,
	METH_VARARGS, mp3enc_set_exp_nspsytune__doc__                 },
    {"set_vbr", (PyCFunction)mp3enc_set_vbr,
	METH_VARARGS, mp3enc_set_vbr__doc__                           },
    {"set_vbr_quality", (PyCFunction)mp3enc_set_vbr_quality,
	METH_VARARGS, mp3enc_set_vbr_quality__doc__                   },
    {"set_abr_bitrate", (PyCFunction)mp3enc_set_abr_bitrate,
	METH_VARARGS, mp3enc_set_abr_bitrate__doc__                   },
    {"set_vbr_min_bitrate", (PyCFunction)mp3enc_set_vbr_min_bitrate,
	METH_VARARGS, mp3enc_set_vbr_min_bitrate__doc__               },
    {"set_vbr_max_bitrate", (PyCFunction)mp3enc_set_vbr_max_bitrate,
	METH_VARARGS, mp3enc_set_vbr_max_bitrate__doc__               },
    {"set_vbr_min_enforce", (PyCFunction)mp3enc_set_vbr_min_enforce,
	METH_VARARGS, mp3enc_set_vbr_min_enforce__doc__               },
    {"set_lowpass_frequency", (PyCFunction)mp3enc_set_lowpass_frequency,
	METH_VARARGS, mp3enc_set_lowpass_frequency__doc__             },
    {"set_lowpass_width", (PyCFunction)mp3enc_set_lowpass_width,
	METH_VARARGS, mp3enc_set_lowpass_width__doc__                 },
    {"set_highpass_frequency", (PyCFunction)mp3enc_set_highpass_frequency,
	METH_VARARGS, mp3enc_set_highpass_frequency__doc__            },
    {"set_highpass_width", (PyCFunction)mp3enc_set_highpass_width,
	METH_VARARGS, mp3enc_set_highpass_width__doc__                },
    {"set_ath_for_masking_only", (PyCFunction)mp3enc_set_ath_for_masking_only,
	METH_VARARGS, mp3enc_set_ath_for_masking_only__doc__          },
    {"set_ath_for_short_only", (PyCFunction)mp3enc_set_ath_for_short_only,
	METH_VARARGS, mp3enc_set_ath_for_short_only__doc__            },
    {"set_ath_disable", (PyCFunction)mp3enc_set_ath_disable,
	METH_VARARGS, mp3enc_set_ath_disable__doc__                   },
    {"set_ath_type", (PyCFunction)mp3enc_set_ath_type,
	METH_VARARGS, mp3enc_set_ath_type__doc__                      },
    {"set_ath_lower", (PyCFunction)mp3enc_set_ath_lower,
	METH_VARARGS, mp3enc_set_ath_lower__doc__                     },
    {"set_athaa_type", (PyCFunction)mp3enc_set_athaa_type,
	METH_VARARGS, mp3enc_set_athaa_type__doc__                    },
    {"set_athaa_loudness_approximation", (PyCFunction)mp3enc_set_athaa_loudness_approximation,
	METH_VARARGS, mp3enc_set_athaa_loudness_approximation__doc__  },
    {"set_athaa_sensitivity", (PyCFunction)mp3enc_set_athaa_sensitivity,
	METH_VARARGS, mp3enc_set_athaa_sensitivity__doc__             },
    {"set_predictability_limit", (PyCFunction)mp3enc_set_predictability_limit,
	METH_VARARGS, mp3enc_set_predictability_limit__doc__          },
    {"set_allow_blocktype_difference", (PyCFunction)mp3enc_set_allow_blocktype_difference,
	METH_VARARGS, mp3enc_set_allow_blocktype_difference__doc__    },
    {"set_use_temporal_masking", (PyCFunction)mp3enc_set_use_temporal_masking,
	METH_VARARGS, mp3enc_set_use_temporal_masking__doc__          },
    {"set_inter_channel_ratio", (PyCFunction)mp3enc_set_inter_channel_ratio,
	METH_VARARGS, mp3enc_set_inter_channel_ratio__doc__           },
    {"set_substep", (PyCFunction)mp3enc_set_substep,
	METH_VARARGS, mp3enc_set_substep__doc__                       },
    {"set_no_short_blocks", (PyCFunction)mp3enc_set_no_short_blocks,
	METH_VARARGS, mp3enc_set_no_short_blocks__doc__               },
    {"set_force_short_blocks", (PyCFunction)mp3enc_set_force_short_blocks,
	METH_VARARGS, mp3enc_set_force_short_blocks__doc__            },
    {"get_frame_num", (PyCFunction)mp3enc_get_frame_num,
	METH_VARARGS, mp3enc_get_frame_num__doc__                     },
    {"get_total_frames", (PyCFunction)mp3enc_get_total_frames,
	METH_VARARGS, mp3enc_get_total_frames__doc__                  },
    {"get_bitrate_histogram", (PyCFunction)mp3enc_get_bitrate_histogram,
	METH_VARARGS, mp3enc_get_bitrate_histogram__doc__             },
    {"get_bitrate_values", (PyCFunction)mp3enc_get_bitrate_values,
	METH_VARARGS, mp3enc_get_bitrate_values__doc__                },
    {"get_bitrate_stereo_mode_histogram", (PyCFunction)mp3enc_get_bitrate_stereo_mode_histogram,
	METH_VARARGS, mp3enc_get_bitrate_stereo_mode_histogram__doc__ },
    {"get_stereo_mode_histogram", (PyCFunction)mp3enc_get_stereo_mode_histogram,
	METH_VARARGS, mp3enc_get_stereo_mode_histogram__doc__         },

    {"set_exp_msfix", (PyCFunction)mp3enc_set_exp_msfix,
	METH_VARARGS, mp3enc_set_exp_msfix__doc__            },
    {"set_exp_preset_expopts", (PyCFunction)mp3enc_set_exp_preset_expopts,
	METH_VARARGS, mp3enc_set_exp_preset_expopts__doc__            },
    {"write_tags", (PyCFunction)mp3enc_write_tags,
	METH_VARARGS, mp3enc_write_tags__doc__                        },
#if 0
    {"set_", (PyCFunction)mp3enc_set_,
	METH_VARARGS, mp3enc_set___doc__          },
    {"set_", (PyCFunction)mp3enc_set_,
	METH_VARARGS, mp3enc_set___doc__          },
    {"set_", (PyCFunction)mp3enc_set_,
	METH_VARARGS, mp3enc_set___doc__          },
#endif
    
    {NULL,    NULL}           /* sentinel */
};

/* ---------- */

static PyObject *
mp3enc_dealloc( mp3encobject *self );

static mp3encobject *
newmp3encobject( void )
{
    mp3encobject *self;
        
    self = PyObject_NEW( mp3encobject, &Mp3enctype );
    if ( self == NULL ) {
        PyErr_SetString( (PyObject *)NULL, "can't init myself" );
        return NULL;
    }

    /* XXXX Add your own initializers here */
    self->mp3enc_attr = NULL;
    self->gfp         = lame_init();
    if ( NULL == self->gfp ) {
        PyErr_SetString( (PyObject *)self, "can't init LAME" );
        return (mp3encobject *)mp3enc_dealloc( self );
    }

    /* later */
    self->num_samples        = 2;
    self->num_channels       = 2; /* default */
    self->mp3_buf            = NULL;

    /* we don't want output from the lib */
    lame_set_errorf( self->gfp, quiet_lib_printf );
    lame_set_debugf( self->gfp, quiet_lib_printf );
    lame_set_msgf  ( self->gfp, quiet_lib_printf );

    self->mp3_buf = malloc( 1.25*self->num_samples + 7200 );
    if ( NULL == self->mp3_buf ) {
        PyErr_NoMemory();
        return (mp3encobject *)mp3enc_dealloc( self );
    }

    return self;
}


static PyObject *
mp3enc_dealloc(self)
        mp3encobject *self;
{
        /* XXXX Add your own cleanup code here */
        if ( NULL != self->gfp ) {
            lame_close( self->gfp );
            self->gfp = NULL;
        }

        if ( NULL != self->mp3_buf ) {
            free( self->mp3_buf );
            self->mp3_buf = NULL;
        }

        Py_XDECREF(self->mp3enc_attr);
        //PyMem_DEL(self);

        return NULL;
}

static PyObject *
mp3enc_getattr(self, name)
        mp3encobject *self;
        char *name;
{
        /* XXXX Add your own getattr code here */
    if (self->mp3enc_attr != NULL) {
        PyObject *v = PyDict_GetItemString(self->mp3enc_attr, name);
        if (v != NULL) {
            Py_INCREF(v);
            return v;
        }
    }
    return Py_FindMethod(mp3enc_methods, (PyObject *)self, name);
}


static char Mp3enctype__doc__[] = 
""
;

static PyTypeObject Mp3enctype = {
        PyObject_HEAD_INIT(NULL)
       0,                              /*ob_size*/
        "lame_encode",                  /*tp_name*/
        sizeof(mp3encobject),           /*tp_basicsize*/
        0,                              /*tp_itemsize*/
        /* methods */
        (destructor)mp3enc_dealloc,     /*tp_dealloc*/
        (printfunc)0,                   /*tp_print*/
        (getattrfunc)mp3enc_getattr,    /*tp_getattr*/
        (setattrfunc)0,                 /*tp_setattr*/
        (cmpfunc)0,                     /*tp_compare*/
        (reprfunc)0,                    /*tp_repr*/
        0,                              /*tp_as_number*/
        0,                              /*tp_as_sequence*/
        0,                              /*tp_as_mapping*/
        (hashfunc)0,                    /*tp_hashg*/
        (ternaryfunc)0,                 /*tp_call*/
        (reprfunc)0,                    /*tp_str*/

        /* Space for future expansion */
        0L,0L,0L,0L,
        Mp3enctype__doc__ /* Documentation string */
};

/* End of code for lame_encode objects */
/* -------------------------------------------------------- */


static char mp3lame_init__doc__[] =
"Initialize an mp3 encoder object"
;

static PyObject *
mp3lame_init(self, args)
        PyObject *self; /* Not used */
        PyObject *args;
{
    mp3encobject* rv;
    const char*  mp3_filename;
    FILE*  mp3_file;

    if ( NULL == PyArg_ParseTuple( args, "" ) )
        return NULL;

    rv = newmp3encobject();
    if ( NULL == rv )
        return NULL;

    return (PyObject *)rv;
}


static char mp3lame_url__doc__[] =
"Returns the URL for the LAME website."
;

static PyObject *
mp3lame_url(self, args)
    mp3encobject *self; /* Not used */
    PyObject *args;
{
    if ( NULL == PyArg_ParseTuple(args, "") )
        return NULL;

    return Py_BuildValue("s", get_lame_url());
}


static char mp3lame_version__doc__[] =
"Returns the used version of LAME: (major, minor, alpha, beta, psy_major, psy_minor, psy_alpha, psy_beta, compile_time_features)"
;


static PyObject *
mp3lame_version(self, args)
    PyObject *self; /* Not used */
    PyObject *args;
{
    lame_version_t version;

    if ( NULL == PyArg_ParseTuple( args, "" ) )
        return NULL;

    get_lame_version_numerical( &version );

    return Py_BuildValue( "iiiiiiiis",
       version.major,
       version.minor,
       version.alpha,
       version.beta,
       version.psy_major,
       version.psy_minor,
       version.psy_alpha,
       version.psy_beta,
       version.features );
}


/* List of methods defined in the module */

static struct PyMethodDef mp3lame_methods[] = {
{"init",        (PyCFunction)mp3lame_init,        METH_VARARGS, mp3lame_init__doc__},
{"url",         (PyCFunction)mp3lame_url,         METH_VARARGS, mp3lame_url__doc__ },
{"version",     (PyCFunction)mp3lame_version,     METH_VARARGS, mp3lame_version__doc__},

{NULL,   (PyCFunction)NULL,            0,            NULL}  /* sentinel */
};

/* Initialization function for the module (*must* be called initlame) */

static char lame_module_documentation[] =
"Python modul for the LAME encoding routines."
;

void WIN_DLL_HELL
initlame()
{
    PyObject *m, *d, *tempobj;

    /* Initialize the type of the new type object here; doing it here
     * is required for portability to Windows without requiring C++. */
    Mp3enctype.ob_type = &PyType_Type;

    /* Create the module and add the functions */
    m = Py_InitModule3("lame", mp3lame_methods, lame_module_documentation);

    /* Add some symbolic constants to the module */
    d = PyModule_GetDict(m);
    ErrorObject = PyString_FromString("lame.error");
    PyDict_SetItemString(d, "error", ErrorObject);

    /* Own constants */
    tempobj = PyInt_FromLong(0);
    PyDict_SetItemString(d, "VBR_OFF", tempobj);
    PyDict_SetItemString(d, "STEREO", tempobj);
    PyDict_SetItemString(d, "PAD_NO", tempobj);
    Py_DECREF(tempobj);
    
    tempobj = PyInt_FromLong(1);
    PyDict_SetItemString(d, "JOINT_STEREO", tempobj);
    PyDict_SetItemString(d, "PAD_ALL", tempobj);
    PyDict_SetItemString(d, "ASM_MMX", tempobj);
    Py_DECREF(tempobj);
    
    tempobj = PyInt_FromLong(2);
    PyDict_SetItemString(d, "VBR_OLD", tempobj);
    PyDict_SetItemString(d, "DUAL", tempobj);
    PyDict_SetItemString(d, "PAD_ADJUST", tempobj);
    PyDict_SetItemString(d, "ASM_3DNOW", tempobj);
    Py_DECREF(tempobj);
    
    tempobj = PyInt_FromLong(3);
    PyDict_SetItemString(d, "VBR_ABR", tempobj);
    PyDict_SetItemString(d, "MONO", tempobj);
    PyDict_SetItemString(d, "ASM_SSE", tempobj);
    Py_DECREF(tempobj);
    
    tempobj = PyInt_FromLong(4);
    PyDict_SetItemString(d, "VBR_NEW", tempobj);
    PyDict_SetItemString(d, "VBR_DEFAULT", tempobj);
    tempobj = PyInt_FromLong(3);
    Py_DECREF(tempobj);
    
    tempobj = PyInt_FromLong(1000);
    PyDict_SetItemString(d, "PRESET_R3MIX", tempobj);
    Py_DECREF(tempobj);
    
    tempobj = PyInt_FromLong(1001);
    PyDict_SetItemString(d, "PRESET_STANDARD", tempobj);
    Py_DECREF(tempobj);
    
    tempobj = PyInt_FromLong(1002);
    PyDict_SetItemString(d, "PRESET_EXTREME", tempobj);
    Py_DECREF(tempobj);
    
    tempobj = PyInt_FromLong(1003);
    PyDict_SetItemString(d, "PRESET_INSANE", tempobj);
    Py_DECREF(tempobj);
    
    tempobj = PyInt_FromLong(1004);
    PyDict_SetItemString(d, "PRESET_STANDARD_FAST", tempobj);
    Py_DECREF(tempobj);
    
    tempobj = PyInt_FromLong(1005);
    PyDict_SetItemString(d, "PRESET_EXTREME_FAST", tempobj);
    Py_DECREF(tempobj);
    
    tempobj = PyInt_FromLong(1006);
    PyDict_SetItemString(d, "PRESET_MEDIUM", tempobj);
    Py_DECREF(tempobj);
    
    tempobj = PyInt_FromLong(1007);
    PyDict_SetItemString(d, "PRESET_MEDIUM_FAST", tempobj);
    Py_DECREF(tempobj);
    
    /* Check for errors */
    if (PyErr_Occurred())
        Py_FatalError("can't initialize module lame");
}
