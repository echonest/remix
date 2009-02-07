/* $Id: pymadfile.h,v 1.5 2003/01/11 13:15:39 jaq Exp $
 *
 * python interface to libmad (the mpeg audio decoder library)
 *
 * Copyright (c) 2002 Jamie Wilkinson
 *
 * This program is free software, you may copy and/or modify as per
 * the GNU General Public License (version 2, or at your discretion,
 * any later version).  This is the same license as libmad.
 */

#ifndef __PY_MADFILE_H__
#define __PY_MADFILE_H__

typedef struct {
    signed short **samples;
    unsigned int length;
    struct sample_list *next;
} sample_list;
    
typedef struct {
    PyObject_HEAD
    PyObject * fobject;
    int close_file;
    struct mad_stream stream;
    struct mad_frame  frame;
    struct mad_synth  synth;
    mad_timer_t timer;
    unsigned char * buffy;
    unsigned int bufsiz;
    unsigned int framecount;
    unsigned long total_length;
} py_madfile; /* MadFile */

#define PY_MADFILE(x) ((py_madfile *) x)
#define MAD_STREAM(x) (PY_MADFILE(x)->stream)
#define MAD_FRAME(x)  (PY_MADFILE(x)->frame)
#define MAD_SYNTH(x)  (PY_MADFILE(x)->synth)
#define MAD_BUFFY(x)  (PY_MADFILE(x)->buffy)
#define MAD_BUFSIZ(x) (PY_MADFILE(x)->bufsiz)
#define MAD_TIMER(x)  (PY_MADFILE(x)->timer)

typedef struct mad_pcm pcm;

extern PyTypeObject py_madfile_t;

static pcm * readframe(PyObject * self);

static void py_madfile_dealloc(PyObject * self, PyObject * args);
static PyObject * py_madfile_read(PyObject * self, PyObject * args);
static PyObject * py_madfile_readall(PyObject * self, PyObject * args);
static PyObject * py_madfile_layer(PyObject * self, PyObject * args);
static PyObject * py_madfile_mode(PyObject * self, PyObject * args);
static PyObject * py_madfile_samplerate(PyObject * self, PyObject * args);
static PyObject * py_madfile_bitrate(PyObject * self, PyObject * args);
static PyObject * py_madfile_emphasis(PyObject * self, PyObject * args);
static PyObject * py_madfile_total_time(PyObject * self, PyObject * args);
static PyObject * py_madfile_current_time(PyObject * self, PyObject * args);
static PyObject * py_madfile_seek_time(PyObject * self, PyObject * args);
static PyObject * py_madfile_getattr(PyObject * self, char * name);

#endif /* __PY_MADFILE_H__ */
