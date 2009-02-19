/* $Id: pymadfile.c,v 1.20 2003/02/05 06:29:23 jaq Exp $
 *
 * python interface to libmad (the mpeg audio decoder library)
 *
 * Copyright (c) 2002 Jamie Wilkinson
 *
 * This program is free software, you may copy and/or modify as per
 * the  GNU General Public License (version 2, or at your discretion,
 * any later version).  This is the same license as libmad.
 *
 * The code in py_madfile_read was copied from the madlld program, which
 * can be found at http://www.bsd-dk.dk/~elrond/audio/madlld/ and carries
 * the following copyright and license:
 *
 * The madlld program is © 2001 by Bertrand Petit, all rights reserved.
 * It is distributed under the terms of the license similar to the
 * Berkeley license reproduced below.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 *  1. Redistributions of source code must retain the above copyright
 *     notice, this list of conditions and the following disclaimer.
 * 
 *  2. Redistributions in binary form must reproduce the above copyright
 *     notice, this list of conditions and the following disclaimer in
 *     the documentation and/or other materials provided with the
 *     distribution.
 * 
 *  3. Neither the name of the author nor the names of its contributors
 *     may be used to endorse or promote products derived from this
 *     software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS''
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS
 * BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
 * OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
 * THE POSSIBILITY OF SUCH DAMAGE.
 */

#include <Python.h>

#define PY_ARRAY_UNIQUE_SYMBOL _mad_extension
#define NO_IMPORT_ARRAY
#include "/System/Library/Frameworks/Python.framework/Versions/2.5/Extras/lib/python/numpy/core/include/numpy/arrayobject.h"

#include <mad.h>

#include <stdio.h>
#include <stdint.h>
#include <errno.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/mman.h>

#include "madmodule.h"
#include "pymadfile.h"
#include "xing.h"

#if PY_VERSION_HEX < 0x01060000
#define PyObject_DEL(op) PyMem_DEL((op))
#endif

#define ERROR_MSG_SIZE  512
#define MAD_BUF_SIZE    (5*8192) /* should be a multiple of 4 >= 4096 and large enough to capture possible 
                                    junk at beginning of MP3 file*/

/* local helpers */
static unsigned long    calc_total_time(PyObject *);
static signed short int madfixed_to_short(mad_fixed_t);

PyTypeObject py_madfile_t = {
    PyObject_HEAD_INIT(&PyType_Type)
    0,
    "MadFile",
    sizeof(py_madfile),
    0,
    /* standard methods */
    (destructor) py_madfile_dealloc,
    (printfunc) 0,
    (getattrfunc) py_madfile_getattr,
    (setattrfunc) 0,
    (cmpfunc) 0,
    (reprfunc) 0,
    /* type categories */
    0, /* as number */
    0, /* as sequence */
    0, /* as mapping */
    0, /* hash */
    0, /* binary */
    0, /* repr */
    0, /* getattro */
    0, /* setattro */
    0, /* as buffer */
    0, /* tp_flags */
    NULL
};

/* functions */

PyObject * py_madfile_new(PyObject * self, PyObject * args) {
    py_madfile * mf = NULL;
    int close_file = 0;
    char * fname;
    PyObject *fobject = NULL;
    char *initial;
    long ibytes = 0;
    unsigned long int bufsiz = MAD_BUF_SIZE;
    int n;
  
    if (PyArg_ParseTuple(args, "s|l:MadFile", &fname, &bufsiz)) {
        fobject = PyFile_FromString(fname, "r");
	    close_file = 1;
	    
	    if (fobject == NULL) {
	        return NULL;
	    }
    } else if (PyArg_ParseTuple(args, "O|sl:MadFile", &fobject, &initial, &ibytes)) {
	    /* clear the first failure */
	    PyErr_Clear();
        /* make sure that if nothing else we can read it */
        if (!PyObject_HasAttrString(fobject, "read")) {
            Py_DECREF(fobject);
	        PyErr_SetString(PyExc_IOError, "Object must have a read method");
            return NULL;
        }
    } else {
	    return NULL;
    }

    /* bufsiz must be an integer multiple of 4 */
    if ((n = bufsiz % 4)) bufsiz -= n;
    if (bufsiz <= 4096) bufsiz = 4096;

    mf = PyObject_NEW(py_madfile, &py_madfile_t);
    Py_INCREF(fobject);
    mf->fobject = fobject;
    mf->close_file = close_file;

    /* initialise the mad structs */
    mad_stream_init(&mf->stream);
    mad_frame_init(&mf->frame);
    mad_synth_init(&mf->synth);
    mad_timer_reset(&mf->timer);
  
    mf->framecount = 0;

    mf->buffy = malloc(bufsiz * sizeof(unsigned char));
    mf->bufsiz = bufsiz;

    /* explicitly call read to fill the buffer and have the frame header
     * data immediately available to the caller */
    readframe((PyObject *)mf);

    mf->total_length = calc_total_time((PyObject *) mf);

    return (PyObject *) mf;
}

static void py_madfile_dealloc(PyObject * self, PyObject * args) {
    PyObject *o;

    if (PY_MADFILE(self)->fobject) {
    	mad_synth_finish(&MAD_SYNTH(self));
    	mad_frame_finish(&MAD_FRAME(self));
    	mad_stream_finish(&MAD_STREAM(self));

    	free(MAD_BUFFY(self));
    	MAD_BUFFY(self) = NULL;
    	MAD_BUFSIZ(self) = 0;
    
    	if (PY_MADFILE(self)->close_file) {
            o = PyObject_CallMethod(PY_MADFILE(self)->fobject, "close", NULL);
            if (o != NULL) {
                Py_DECREF(o);
            }
        }

    	Py_DECREF(PY_MADFILE(self)->fobject);
    	PY_MADFILE(self)->fobject = NULL;
    }
    
    PyObject_DEL(self);
}

/* Calculates length of MP3 by stepping through the frames and summing up
 * the duration of each frame. */
static unsigned long
calc_total_time(PyObject *self) {
    mad_timer_t timer;
    struct xing xing;
    struct stat buf;
    unsigned long r;
    PyObject *o;
    int fnum;

    xing_init(&xing);
    xing_parse(&xing, MAD_STREAM(self).anc_ptr, MAD_STREAM(self).anc_bitlen);

    if (xing.flags & XING_FRAMES) {
    	timer = MAD_FRAME(self).header.duration;
        mad_timer_multiply(&timer, xing.frames);
        r = mad_timer_count(timer, MAD_UNITS_MILLISECONDS);
    } else {
        o = PyObject_CallMethod(PY_MADFILE(self)->fobject, "fileno", NULL);
        if (o == NULL) {
            /* no fileno method is provided, probably not a file */
            PyErr_Clear();
            return -1;
        }
        fnum = PyInt_AsLong(o);
        Py_DECREF(o);
	    r = fstat(fnum, &buf);

	    /* Figure out actual length of file by stepping through it.
	     * This is a stripped down version of how madplay does it. */
	    void *ptr = mmap(0, buf.st_size, PROT_READ, MAP_SHARED, fnum, 0);
	    if(!ptr) {
            fprintf(stderr, "mmap failed, can't calculate length");
            return -1;
	    }

        mad_timer_t time = mad_timer_zero;
        struct mad_stream stream;
        struct mad_header header;

        mad_stream_init(&stream);
        mad_header_init(&header);

        mad_stream_buffer(&stream, ptr, buf.st_size);

        while (1) {
            if(mad_header_decode(&header, &stream) == -1) {
                if( MAD_RECOVERABLE(stream.error)) {
                    continue;
                 } else {
                    break;
                }
            }

            mad_timer_add(&time, header.duration);
        }

        if (munmap(ptr, buf.st_size) == -1) {
            return -1;
        }

        r = time.seconds * 1000;
    }
    
    return r;
}

/* convert the mad format to an unsigned short */
static signed short int
madfixed_to_short(mad_fixed_t sample) {
    /* A fixed point number is formed of the following bit pattern:
     *
     * SWWWFFFFFFFFFFFFFFFFFFFFFFFFFFFF
     * MSB                          LSB
     * S = sign
     * W = whole part bits
     * F = fractional part bits
     *
     * This pattern contains MAD_F_FRACBITS fractional bits, one should
     * always use this macro when working on the bits of a fixed point
     * number.  It is not guaranteed to be constant over the different
     * platforms supported by libmad.
     *
     * The unsigned short value is formed by the least significant
     * whole part bit, followed by the 15 most significant fractional
     * part bits.
     * 
     * This algorithm was taken from input/mad/mad_engine.c in
     * alsaplayer, because the one in madlld sucked arse.
     * http://www.geocrawler.com/archives/3/15440/2001/9/0/6629549/
     */

    /* round */
    sample += (1L << (MAD_F_FRACBITS - 16));
  
    /* clip */
    if (sample >= MAD_F_ONE) {
	    sample = MAD_F_ONE - 1;
    } else if (sample < -MAD_F_ONE) {
	    sample = -MAD_F_ONE;
	}
	
    /* quantize */
    return sample >> (MAD_F_FRACBITS + 1 - 16);
}

static pcm *
readframe(PyObject * self) {
    int nextframe = 0;
    int result;
    char errmsg[ERROR_MSG_SIZE];

    /* if we are at EOF, then return None */
    // FIXME: move to if null read
    /*
    if (feof(PY_MADFILE(self)->f)) {
    Py_INCREF(Py_None);
    return Py_None;
    }
    */

    /* nextframe might get set during this loop, in which case the
     * bucket needs to be refilled */
    do {
        nextframe = 0; /* reset */

    	/* The input bucket must be filled if it becomes empty or if
    	 * it's the first execution on this file */
    	if ((MAD_STREAM(self).buffer == NULL) || (MAD_STREAM(self).error == MAD_ERROR_BUFLEN)) {
    	    size_t readsize, remaining;
    	    unsigned char * readstart;
            PyObject *o_read;
            char * o_buffer;
  
    	    /* [1] libmad may not consume all bytes of the input buffer.
    	     *     If the last frame in the buffer is not wholly contained
    	     *     by it, then that frame's start is pointed to by the
    	     *     next_frame member of the mad_stream structure.  This
    	     *     common situation occurs when mad_frame_decode():
    	     *      1) fails,
    	     *      2) sets the stream error to MAD_ERROR_BUFLEN, and
    	     *      3) sets the next_frame pointer to a non NULL value.
    	     *     (See also the comment marked [2] below)
    	     *
    	     *     When this occurs, the remaining unused bytes must be put
    	     *     back at the beginning of the buffer and taken into
    	     *     account before refilling the buffer.  This means that
    	     *     the input buffer must be large enough to hold a whole
    	     *     frame at the highest observable bitrate (currently
    	     *     448kbps).
    	     */
    	    if (MAD_STREAM(self).next_frame != NULL) {
    	        remaining = MAD_STREAM(self).bufend - MAD_STREAM(self).next_frame;
    	        memmove(MAD_BUFFY(self), MAD_STREAM(self).next_frame, remaining);
                readstart = MAD_BUFFY(self) + remaining;
                readsize = MAD_BUFSIZ(self) - remaining;
    	    } else {
                readstart = MAD_BUFFY(self);
                readsize = MAD_BUFSIZ(self);
    		    remaining = 0;
    	    }
  
    	    /* Fill in the buffer.  If an error occurs, make like a tree */
            o_read = PyObject_CallMethod(PY_MADFILE(self)->fobject, "read", "i", readsize);
            if (o_read == NULL) {
                // FIXME: should specifically handle read errors...
                return NULL;
            }
            PyString_AsStringAndSize(o_read, &o_buffer, &readsize);
            // EOF?
            if (readsize == 0) {
                Py_DECREF(o_read);
                return NULL;
            }
            memcpy(readstart, o_buffer, readsize);
            Py_DECREF(o_read);

    	    /* Pipe the new buffer content to libmad's stream decode
    	     * facility */
    	    mad_stream_buffer(&MAD_STREAM(self), MAD_BUFFY(self), readsize + remaining);
    	    MAD_STREAM(self).error = 0;
    	}

    	/* Decode the next mpeg frame.  The streams are read from the
    	 * buffer, its constituents are broken down and stored in the
    	 * frame structure, ready for examination/alteration or PCM
    	 * synthesis.  Decoding options are carried to the Frame from
    	 * the Stream.
    	 *
    	 * Error handling: mad_frame_decode() returns a non-zero value
    	 * when an error occurs.  The error condition can be checked in
    	 * the error member of the Stream structure.  A mad error is
    	 * recoverable or fatal, the error status is checked with the
    	 * MAD_RECOVERABLE macro.
    	 *
    	 * [2] When a fatal error is encountered, all decoding activities
    	 *     shall be stopped, except when a MAD_ERROR_BUFLEN is
    	 *     signalled.  This condition means that the 
    	 *     mad_frame_decode() function needs more input do its work.
    	 *     One should refill the buffer and repeat the 
    	 *     mad_frame_decode() call.  Some bytes may be left unused
    	 *     at the end of the buffer if those bytes form an incomplete
    	 *     frame.  Before refilling, the remaining bytes must be
    	 *     moved to the beginning of the buffer and used for input
    	 *     for the next mad_frame_decode() invocation.  (See the
    	 *     comment marked [1] for earlier details)
    	 *
    	 * Recoverable errors are caused by malformed bitstreams, in
    	 * this case one can call again mad_frame_decode() in order to
    	 * skip the faulty part and resync to the next frame.
    	 */
        Py_BEGIN_ALLOW_THREADS
        result = mad_frame_decode(&MAD_FRAME(self), &MAD_STREAM(self));
        Py_END_ALLOW_THREADS
    
        if (result) {
            if (MAD_RECOVERABLE(MAD_STREAM(self).error)) {
        		/* FIXME: prefer to return an error string to the caller
        		 * rather than print to stderr 
        		fprintf(stderr, "mad: recoverable frame level error: %s\n",
        		        mad_stream_errorstr(&MAD_STREAM(self)));
        		fflush(stderr);
                        */
        		/* go onto the next frame */
        		nextframe = 1;
    	    } else {
    	        if (MAD_STREAM(self).error == MAD_ERROR_BUFLEN) {
    	            /* not enough data to decode */
    	            nextframe = 1;
    	        } else {
    	            snprintf(errmsg, ERROR_MSG_SIZE, "unrecoverable frame level error: %s", mad_stream_errorstr(&MAD_STREAM(self)));
    	            PyErr_SetString(PyExc_RuntimeError, errmsg);
    	            return NULL;
    	        }
            }
        }
    } while (nextframe);

    Py_BEGIN_ALLOW_THREADS

    /* Accounting.  The computed frame duration is in the frame header
     * structure.  It is expressed as a fixed point number whose data
     * type is mad_timer_t.  It is different from the fixed point
     * format of the samples and unlike it, cannot be directly added
     * or subtracted.  The timer module provides several functions to
     * operate on such numbers.  Be careful though, as some functions
     * of mad's timer module receive their mad_timer_t arguments by
     * value! */
    PY_MADFILE(self)->framecount++;
    mad_timer_add(&MAD_TIMER(self), MAD_FRAME(self).header.duration);

    /* Once decoded, the frame can be synthesised to PCM samples.
     * No errors are reported by mad_synth_frame() */
    mad_synth_frame(&MAD_SYNTH(self), &MAD_FRAME(self));

    Py_END_ALLOW_THREADS
    
    return &MAD_SYNTH(self).pcm;
}

static PyObject * 
py_madfile_read(PyObject * self, PyObject * args) {
    pcm *frame = readframe(self);
    
    if (frame == NULL) {
        Py_INCREF(Py_None);
        return Py_None;
    }
    
    int dimensions[1];
    dimensions[0] = frame->length * 2;
    PyArrayObject *array = (PyArrayObject *)PyArray_FromDims(1, dimensions, PyArray_SHORT);
  
    Py_BEGIN_ALLOW_THREADS
    
    /* Synthesised samples must be converted from mad's fixed point
     * format to the consumer format.  Here we use signed 16 bit
     * big endian ints on two channels.  Integer samples are 
     * temporarily stored in a buffer that is flushed when full. */
    short *buffer = (short *)array->data;
    unsigned int i;
    for (i = 0; i < frame->length; ) {
	    signed short sample;

	    // left channel
	    sample = madfixed_to_short(frame->samples[0][i]);
        buffer[i++] = sample;

	    // right channel
	    if (MAD_NCHANNELS(&MAD_FRAME(self).header) == 2) {
	        sample = madfixed_to_short(MAD_SYNTH(self).pcm.samples[1][i]);
        }
        buffer[i++] = sample;
    }
  
    Py_END_ALLOW_THREADS
    
    return PyArray_Return(array);
}

static PyObject * 
py_madfile_readall(PyObject * self, PyObject * args) {
    sample_list *head, *curr;
    unsigned int frame_length, total_length = 0;
    unsigned int i, l;
    
    // create dummy node to sit at beginning
    head = (sample_list *)malloc(sizeof(sample_list));
    if (head == NULL) {
        Py_INCREF(Py_None);
        return Py_None;
    }
    
    curr = head;
    pcm *frame;
    while ((frame = readframe(self)) != NULL) {
        frame_length = frame->length;
        total_length += frame_length;
        
        sample_list *sl = (sample_list *)malloc(sizeof(sample_list));
        if (sl == NULL) {
            PyErr_SetString(PyExc_MemoryError, "can't allocate memory for sample data");
            return NULL;
        }
        
        sl->samples = (signed short **)malloc(2 * sizeof(signed short *));
        if (sl->samples == NULL) {
            PyErr_SetString(PyExc_MemoryError, "can't allocate memory for sample data");
            return NULL;
        }
        
        sl->samples[0] = (signed short *)malloc(frame_length * sizeof(signed short));
        if (sl->samples[0] == NULL) {
            PyErr_SetString(PyExc_MemoryError, "can't allocate memory for sample data");
            return NULL;
        }
        
        sl->samples[1] = (signed short *)malloc(frame_length * sizeof(signed short));
        if (sl->samples[1] == NULL) {
            PyErr_SetString(PyExc_MemoryError, "can't allocate memory for sample data");
            return NULL;
        }
        
        sl->length = frame_length;
        sl->next = NULL;
        
        for (i = 0; i < frame_length; i++) {
    	    signed short sample;

    	    // left channel
    	    sample = madfixed_to_short(frame->samples[0][i]);
            sl->samples[0][i] = sample;
            
            // right channel
    	    if (MAD_NCHANNELS(&MAD_FRAME(self).header) == 2) {
    	        sample = madfixed_to_short(frame->samples[1][i]);
            }
            sl->samples[1][i] = sample;
        }
        
        curr->next = (sample_list *)sl;
        curr = sl;
    }
    
    int dimensions[1] = {total_length * 2};
    PyArrayObject *array  = (PyArrayObject *)PyArray_FromDims(1, dimensions, PyArray_SHORT);
    
    Py_BEGIN_ALLOW_THREADS
    
    short *buffer = (short *)array->data;
    i = 0;
    curr = (sample_list *)head->next;
    
    while (curr) {
        sample_list *copied = curr;
        
        // do stuff
        for (l = 0; l < copied->length && i < total_length * 2; l++) {
            buffer[i++] = copied->samples[0][l];
            buffer[i++] = copied->samples[1][l];
        }
        
        curr = (sample_list *)curr->next;
        
        free(copied->samples[0]);
        free(copied->samples[1]);
        free(copied->samples);
        free(copied);
    }

    Py_END_ALLOW_THREADS
    
    return PyArray_Return(array);
}

/* return the MPEG layer */
static PyObject *
py_madfile_layer(PyObject * self, PyObject * args) {
    return PyInt_FromLong(MAD_FRAME(self).header.layer);
}

/* return the channel mode */
static PyObject *
py_madfile_mode(PyObject * self, PyObject * args) {
    return PyInt_FromLong(MAD_FRAME(self).header.mode);
}

/* return the stream samplerate */
static PyObject *
py_madfile_samplerate(PyObject * self, PyObject * args) {
    return PyInt_FromLong(MAD_FRAME(self).header.samplerate);
}

/* return the stream bitrate */
static PyObject *
py_madfile_bitrate(PyObject * self, PyObject * args) {
    return PyInt_FromLong(MAD_FRAME(self).header.bitrate);
}

/* return the emphasis value */
static PyObject *
py_madfile_emphasis(PyObject * self, PyObject * args) {
    return PyInt_FromLong(MAD_FRAME(self).header.emphasis);
}

/* return the estimated playtime of the track, in milliseconds */
static PyObject *
py_madfile_total_time(PyObject * self, PyObject * args) {
    return PyInt_FromLong(PY_MADFILE(self)->total_length);
}

/* return the current position in the track, in milliseconds */
static PyObject *
py_madfile_current_time(PyObject * self, PyObject * args) {
    return PyInt_FromLong(mad_timer_count(MAD_TIMER(self),
					  MAD_UNITS_MILLISECONDS));
}

/* seek playback to the given position, in milliseconds, from the start
 * FIXME: this implementation is really evil -- amazing that it semi-works */
static PyObject *
py_madfile_seek_time(PyObject * self, PyObject * args) {
    long pos, offset;
    struct stat buf;
    int r;
    PyObject *o;
    int fnum;

    if (!PyArg_ParseTuple(args, "l", &pos) || pos < 0) {
    	PyErr_SetString(PyExc_TypeError, "invalid argument");
    	return NULL;
    }

    o = PyObject_CallMethod(PY_MADFILE(self)->fobject, "fileno", NULL);
    if (o == NULL) {
	    PyErr_SetString(PyExc_IOError, "couldn't get fileno");
        return NULL;
    }
    fnum = PyInt_AsLong(o);
    Py_DECREF(o);
    
    r = fstat(fnum, &buf);
    if (r != 0) {
    	PyErr_SetString(PyExc_IOError, "couldn't stat file");
    	return NULL;
    }

    offset = ((double)pos / PY_MADFILE(self)->total_length) * buf.st_size;

    o = PyObject_CallMethod(PY_MADFILE(self)->fobject, "seek", "l", offset);
    if (o == NULL) {
        /* most likely no seek method -- FIXME get better checking */
    	PyErr_SetString(PyExc_IOError, "couldn't seek file");
    	return NULL;
    }
    Py_DECREF(o);

    mad_timer_set(&MAD_TIMER(self), 0, pos, 1000);

    return Py_None;
}

/* housekeeping */

static PyMethodDef madfile_methods[] = {
    { "read", py_madfile_read, METH_VARARGS, "" },
    { "readall", py_madfile_readall, METH_VARARGS, "" },
    { "layer", py_madfile_layer, METH_VARARGS, "" },
    { "mode", py_madfile_mode, METH_VARARGS, "" },
    { "samplerate", py_madfile_samplerate, METH_VARARGS, "" },
    { "bitrate", py_madfile_bitrate, METH_VARARGS, "" },
    { "emphasis", py_madfile_emphasis, METH_VARARGS, "" },
    { "total_time", py_madfile_total_time, METH_VARARGS, "" },
    { "current_time", py_madfile_current_time, METH_VARARGS, "" },
    { "seek_time", py_madfile_seek_time, METH_VARARGS, "" },
    { NULL, 0, 0, NULL }
};

static PyObject * py_madfile_getattr(PyObject * self, char * name) {
    return Py_FindMethod(madfile_methods, self, name);
}
