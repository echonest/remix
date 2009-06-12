/***************************************************************************
 *   Copyright (C) 2006 by Patrick Stinson                                 *
 *   patrickkidd@gmail.com                                                 *
 *                                                                         *
 *   Permission is hereby granted, free of charge, to any person obtaining *
 *   a copy of this software and associated documentation files (the       *
 *   "Software"), to deal in the Software without restriction, including   *
 *   without limitation the rights to use, copy, modify, merge, publish,   *
 *   distribute, sublicense, and/or sell copies of the Software, and to    *
 *   permit persons to whom the Software is furnished to do so, subject to *
 *   the following conditions:                                             *
 *                                                                         *
 *   The above copyright notice and this permission notice shall be        *
 *   included in all copies or substantial portions of the Software.       *
 *                                                                         *
 *   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,       *
 *   EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF    *
 *   MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.*
 *   IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR     *
 *   OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, *
 *   ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR *
 *   OTHER DEALINGS IN THE SOFTWARE.                                       *
 ***************************************************************************/

#include <Python.h>
#include <numpy/arrayobject.h>
#include <numpy/libnumarray.h>
#include <iostream>
#include <stdexcept>
#include "libsoundtouch/SoundTouch.h"
#include "libsoundtouch/BPMDetect.h"

 
static PyObject *SoundTouchError;


#ifndef Py_RETURN_NONE
#define Py_RETURN_NONE Py_INCREF(Py_None); return Py_None;
#endif


/***************************************************************************
 *  class SoundTouch
 ***************************************************************************/

class SoundTouchProxy : public soundtouch::SoundTouch
{
public:
  float _getrate(){return rate;}
  float _gettempo(){return tempo;}
  uint _getchannels(){return channels;}
};


typedef struct {
  PyObject_HEAD
  SoundTouchProxy *soundtouch;
} SoundTouch;


static void
SoundTouch_dealloc(SoundTouch *self)
{
  delete self->soundtouch;
  self->ob_type->tp_free((PyObject *) self);
}


static PyObject *
SoundTouch_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
  SoundTouch *self;
  self = (SoundTouch *) type->tp_alloc(type, 0);
  self->soundtouch = new SoundTouchProxy;
  self->soundtouch->setChannels(2);
  self->soundtouch->setSampleRate(44100);
  return (PyObject *) self;
}


static int SoundTouch_init(SoundTouch *self, PyObject *args, PyObject *kwds)
{
  return 0;
}


static PyObject *
SoundTouch_setRate(SoundTouch *self, PyObject *args)
{
  float rate;
  if(!PyArg_ParseTuple(args, "f", &rate)) {
    return NULL;
  }
  self->soundtouch->setRate(rate);

  Py_RETURN_NONE;
}


static PyObject *
SoundTouch_setTempo(SoundTouch *self, PyObject *args)
{
  float tempo;
  if(!PyArg_ParseTuple(args, "f", &tempo))
    return NULL;

  self->soundtouch->setTempo(tempo);

  Py_RETURN_NONE;
}


static PyObject *
SoundTouch_setRateChange(SoundTouch *self, PyObject *args)
{
  float newRate;
  if(!PyArg_ParseTuple(args, "f", &newRate))
    return NULL;

  self->soundtouch->setRateChange(newRate);

  Py_RETURN_NONE;
}


static PyObject *
SoundTouch_setTempoChange(SoundTouch *self, PyObject *args)
{
  float newTempo;
  if(!PyArg_ParseTuple(args, "f", &newTempo))
    return NULL;

  self->soundtouch->setTempoChange(newTempo);

  Py_RETURN_NONE;
}


static PyObject *
SoundTouch_setPitch(SoundTouch *self, PyObject *args)
{
  float pitch;
  if(!PyArg_ParseTuple(args, "f", &pitch))
    return NULL;

  self->soundtouch->setPitch(pitch);

  Py_RETURN_NONE;
}


static PyObject *
SoundTouch_setPitchOctaves(SoundTouch *self, PyObject *args)
{
  float newPitch;
  if(!PyArg_ParseTuple(args, "f", &newPitch))
    return NULL;

  self->soundtouch->setPitchOctaves(newPitch);

  Py_RETURN_NONE;
}


static PyObject *
SoundTouch_setPitchSemiTones(SoundTouch *self, PyObject *args)
{
  float newPitch;
  if(!PyArg_ParseTuple(args, "f", &newPitch))
    return NULL;
  self->soundtouch->setPitchSemiTones(newPitch);

  Py_RETURN_NONE;
}


static PyObject *
SoundTouch_setChannels(SoundTouch *self, PyObject *args)
{
  int channels;
  if(!PyArg_ParseTuple(args, "i", &channels))
    return NULL;

  try
    {
      self->soundtouch->setChannels(channels);
    }
  catch(std::runtime_error &error)
    {
      PyErr_Format(PyExc_RuntimeError, error.what());
      return NULL;
    }

  Py_RETURN_NONE;
}


static PyObject *
SoundTouch_setSampleRate(SoundTouch *self, PyObject *args)
{
  int sampleRate;
  if(!PyArg_ParseTuple(args, "i", &sampleRate))
    return NULL;

  self->soundtouch->setSampleRate(sampleRate);

  Py_RETURN_NONE;
}


static PyObject *
SoundTouch_flush(SoundTouch *self)
{
  self->soundtouch->flush();

  Py_RETURN_NONE;
}


static PyObject *
SoundTouch_clear(SoundTouch *self)
{
  self->soundtouch->clear();

  Py_RETURN_NONE;
}


static PyObject *
SoundTouch_putSamples(SoundTouch *self, PyObject *args)
{
  float *samples;
  PyObject *osound;
  PyArrayObject *sound;
  PyObject *typeObject;
  int type;

  int ret = PyArg_ParseTuple(args, "O", &osound);
  if(!ret) {
    return NULL;
  }
  /*

  typeObject = PyObject_CallMethod(osound, "type", NULL);
  
  type = NA_typeObjectToTypeNo(typeObject);
  
  Py_DECREF(typeObject);
*/  
  type = tFloat32; // hack for now
  
  if(type != tFloat32)
    {
      PyErr_Format(SoundTouchError, "sounds must be Float32");
      return NULL;
    }

  sound = (PyArrayObject *) NA_InputArray(osound, tFloat32, NUM_C_ARRAY);
  
  if(!sound)
    {
      Py_XDECREF(sound);
      PyErr_Format(SoundTouchError, 
                   "couldn't convert array to PyArrayObject.");
      return NULL;
    }
  else if(sound->nd != 1)
    {
      Py_XDECREF(sound);
      PyErr_Format(SoundTouchError, "sound arrays must have 1 dimension.");
      return NULL;
    }

  samples = (Float32 *) NA_OFFSETDATA(sound);
  uint numSamples = sound->dimensions[0];
  uint channels = self->soundtouch->_getchannels();

  try
    {
      self->soundtouch->putSamples(samples, numSamples / channels);
    }
  catch(std::runtime_error &error)
    {
      PyErr_Format(PyExc_RuntimeError, error.what());
      return NULL;
    }

  Py_RETURN_NONE;
}

static PyObject *
SoundTouch_receiveSamples(SoundTouch *self, PyObject *args)
{
  float *samples;
  PyObject *osound;
  PyArrayObject *sound;
  int type;
  PyObject *typeObject;

  if(!PyArg_ParseTuple(args, "O", &osound)) {
    return NULL;
  }

  /*typeObject = PyObject_CallMethod(osound, "type", NULL);
  type = NA_typeObjectToTypeNo(typeObject);
  Py_DECREF(typeObject);
  if(type != tFloat32)
    {
      PyErr_Format(SoundTouchError, "sounds must be Float32");
      return NULL;
    }
*/
    type = tFloat32; //hack
  sound = (PyArrayObject *) NA_InputArray(osound, tFloat32, NUM_C_ARRAY);
  if(!sound)
    {
      Py_XDECREF(sound);
      PyErr_Format(SoundTouchError, 
                   "couldn't convert array to PyArrayObject.");
      return NULL;
    }
  else if(sound->nd != 1)
    {
      Py_XDECREF(sound);
      PyErr_Format(SoundTouchError, "sound arrays must have 1 dimension.");
      return NULL;
    }


  uint length = sound->dimensions[0];
  uint channels = self->soundtouch->_getchannels();
  samples = (Float32 *) NA_OFFSETDATA(sound);

  length = self->soundtouch->receiveSamples(samples, length / channels);
  
  return Py_BuildValue("i", length);
}


static PyObject *
SoundTouch_setSetting(SoundTouch *self, PyObject *args)
{
  uint settingId;
  uint value;
  if(!PyArg_ParseTuple(args, "ii", &settingId, &value))
    return NULL;

  int ret = self->soundtouch->setSetting(settingId, value) ? 1 : 0;
  return Py_BuildValue("b", ret);
}


static PyObject *
SoundTouch_getSetting(SoundTouch *self, PyObject *args)
{
  uint settingId;

  if(!PyArg_ParseTuple(args, "i", &settingId))
    return NULL;

  return Py_BuildValue("i", self->soundtouch->getSetting(settingId));
}


static PyObject *
SoundTouch_numUnprocessedSamples(SoundTouch *self)
{
  return Py_BuildValue("i", self->soundtouch->numUnprocessedSamples());
}


static PyObject *
SoundTouch_isEmpty(SoundTouch *self)
{
  if(self->soundtouch->isEmpty())
    {
      Py_INCREF(Py_True);
      return Py_True;
    }
  else
    {
      Py_INCREF(Py_False);
      return Py_False;
    }
}


static PyObject *
SoundTouch_numSamples(SoundTouch *self)
{
  return Py_BuildValue("i", self->soundtouch->numSamples());
}


/*
static PyGetSetDef SoundTouch_getseters[] = {
  {"rate", (getter) SoundTouch_getrate, NULL, 
   "Effective 'rate' value calculated from 'virtualRate', 'virtualTempo'"
   "and 'virtualPitch'"},
  {
}
*/




static PyMethodDef SoundTouch_methods[] = {
  {"setRate", (PyCFunction) SoundTouch_setRate, METH_VARARGS,
   "Sets new rate control value. Normal rate = 1.0, smaller values"
   "represent slower rate, larger faster rates."},

  {"setRateChange", (PyCFunction) SoundTouch_setRateChange, METH_VARARGS,
   "Sets new rate control value as a difference in percents compared"
   "to the original rate (-50 .. +100 %)"},

  {"setTempo", (PyCFunction) SoundTouch_setTempo, METH_VARARGS,
   "Sets new tempo control value. Normal tempo = 1.0, smaller values"
   "represent slower tempo, larger faster tempo."},

  {"setTempoChange", (PyCFunction) SoundTouch_setTempoChange, METH_VARARGS,
   "Sets new tempo control value as a difference in percents compared"
   "to the original tempo (-50 .. +100 %)"},

  {"setPitch", (PyCFunction) SoundTouch_setPitch, METH_VARARGS,
   "Sets new pitch control value. Original pitch = 1.0, smaller values"
   "represent lower pitches, larger values higher pitch."},

  {"setPitchOctaves", (PyCFunction) SoundTouch_setPitchOctaves, METH_VARARGS,
   "Sets pitch change in octaves compared to the original pitch"
   "(-1.00 .. +1.00)"},

  {"setPitchSemiTones", (PyCFunction) SoundTouch_setPitchSemiTones, METH_VARARGS,
   "Sets pitch change in semi-tones compared to the original pitch"
   "(-12 .. +12)"},

  {"setChannels", (PyCFunction) SoundTouch_setChannels, METH_VARARGS,
   "Sets the number of channels, 1 = mono, 2 = stereo"},

  {"setSampleRate", (PyCFunction) SoundTouch_setSampleRate, METH_VARARGS,
   "Sets sample rate."},

  {"flush", (PyCFunction) SoundTouch_flush, METH_NOARGS,
   "Flushes the last samples from the processing pipeline to the output.\n"
   "Clears also the internal processing buffers.\n"
   "\n"
   "Note: This function is meant for extracting the last samples of a sound"
   "stream. This function may introduce additional blank samples in the end"
   "of the sound stream, and thus it's not recommended to call this function"
   "in the middle of a sound stream."},

  {"putSamples", (PyCFunction) SoundTouch_putSamples, METH_VARARGS,
   "Adds 'numSamples' pcs of samples from the 'samples' memory position into"
   "the input of the object. Notice that sample rate _has_to_ be set before"
   "calling this function, otherwise throws a runtime_error exception"},

  {"receiveSamples", (PyCFunction) SoundTouch_receiveSamples, METH_VARARGS,
   "Return samples from beginning of the sample buffer. Copies requested "
   "samples to output buffer and removes them from the sample buffer. If "
   "there are less than 'numsample' samples in the buffer, returns all "
   "that are available."},

  {"clear", (PyCFunction) SoundTouch_clear, METH_VARARGS,
   "Clears all the samples in the object's output and internal processing"
   "buffers."},

  {"setSetting", (PyCFunction) SoundTouch_setSetting, METH_VARARGS,
   "Changes a setting controlling the processing system behaviour. See the"
   "'SETTING_...' defines for available setting ID's.\n"
   "\n"
   "return 'TRUE' if the setting was succesfully changed."},

  {"getSetting", (PyCFunction) SoundTouch_getSetting, METH_VARARGS,
   "Reads a setting controlling the processing system behaviour. See the"
   "'SETTING_...' defines for available setting ID's.\n"
   "\n"
   "return the setting value."},

  {"numUnprocessedSamples", (PyCFunction) SoundTouch_numUnprocessedSamples, METH_VARARGS,
   "Returns number of samples currently unprocessed."},

  /***************** FIFOSampleBuffer ***************************************/
  {"isEmpty", (PyCFunction) SoundTouch_isEmpty, METH_NOARGS,
   "Returns True if the sample buffer is empty."},

  {"numSamples", (PyCFunction) SoundTouch_numSamples, METH_NOARGS,
   "Returns the number of samples currently in the buffer."},

  {NULL} /* Sentinel */
};


static char * SoundTouch_doc = 
" SoundTouch - main class for tempo/pitch/rate adjusting routines.\n"
"\n"
" Notes:\n"
" - Initialize the SoundTouch object instance by setting up the sound stream\n"
"   parameters with functions 'setSampleRate' and 'setChannels', then set\n"
"   desired tempo/pitch/rate settings with the corresponding functions.\n"
"\n"
" - The SoundTouch class behaves like a first-in-first-out pipeline: The\n"
"   samples that are to be processed are fed into one of the pipe by calling\n"
"   function 'putSamples', while the ready processed samples can be read\n"
"   from the other end of the pipeline with function 'receiveSamples'.\n"
"\n"
" - The SoundTouch processing classes require certain sized 'batches' of\n"
"   samples in order to process the sound. For this reason the classes buffer\n"
"   incoming samples until there are enough of samples available for\n"
"   processing, then they carry out the processing step and consequently\n"
"   make the processed samples available for outputting.\n"
"\n"
" - For the above reason, the processing routines introduce a certain\n"
"   'latency' between the input and output, so that the samples input to\n"
"   SoundTouch may not be immediately available in the output, and neither\n"
"   the amount of outputtable samples may not immediately be in direct\n"
"   relationship with the amount of previously input samples.\n"
"\n"
" - The tempo/pitch/rate control parameters can be altered during processing.\n"
"   Please notice though that they aren't currently protected by semaphores,\n"
"   so in multi-thread application external semaphore protection may be\n"
"   required.\n"
"\n"
" - This class utilizes classes 'TDStretch' for tempo change (without modifying\n"
"   pitch) and 'RateTransposer' for changing the playback rate (that is, both\n"
"   tempo and pitch in the same ratio) of the sound. The third available control\n"
"   'pitch' (change pitch but maintain tempo) is produced by a combination of\n"
"   combining the two other controls.\n"
"\n"
"Other handy functions that are implemented in the ancestor classes (see\n"
"classes 'FIFOProcessor' and 'FIFOSamplePipe')\n"
"\n"
" - receiveSamples() : Use this function to receive 'ready' processed samples from SoundTouch.\n"
" - numSamples()     : Get number of 'ready' samples that can be received with\n"
"                      function 'receiveSamples()'\n"
" - isEmpty()        : Returns nonzero if there aren't any 'ready' samples.\n"
" - clear()          : Clears all samples from ready/processing buffers.\n";


static PyTypeObject SoundTouchType = {
  PyObject_HEAD_INIT(NULL)
  0,                         /*ob_size*/
  "soundtouch.SoundTouch",   /*tp_name*/
  sizeof(SoundTouch), /*tp_basicsize*/
  0,                         /*tp_itemsize*/
  (destructor) SoundTouch_dealloc,                         /*tp_dealloc*/
  0,                         /*tp_print*/
  0,                         /*tp_getattr*/
  0,                         /*tp_setattr*/
  0,                         /*tp_compare*/
  0,                         /*tp_repr*/
  0,                         /*tp_as_number*/
  0,                         /*tp_as_sequence*/
  0,                         /*tp_as_mapping*/
  0,                         /*tp_hash */
  0,                         /*tp_call*/
  0,                         /*tp_str*/
  0,                         /*tp_getattro*/
  0,                         /*tp_setattro*/
  0,                         /*tp_as_buffer*/
  Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,        /*tp_flags*/
  SoundTouch_doc,      /* tp_doc */
  0,                         /* tp_traverse */
  0,                         /* tp_clear */
  0,                         /* tp_richcompare */
  0,                         /* tp_weaklistoffset */
  0,                         /* tp_iter */
  0,                         /* tp_iternext */
  SoundTouch_methods,        /* tp_methods */
  0,        /* tp_members */
  0,                         /* tp_getset */
  0,                         /* tp_base */
  0,                         /* tp_dict */
  0,                         /* tp_descr_get */
  0,                         /* tp_descr_set */
  0,                         /* tp_dictoffset */
  (initproc)SoundTouch_init, /* tp_init */
  0,                         /* tp_alloc */
  SoundTouch_new,              /* tp_new */
};


/***************************************************************************
 * module parts
 **************************************************************************/


static PyObject *
soundtouch_find_bpm(PyObject *obj, PyObject *args)
{
  PyObject *osound;
  int samplerate;

  int length;
  float tempo;
  Float32 *samples;
  PyArrayObject *sound;
  PyObject *typeObject;
  int type;

  if(!sizeof(Float32) == sizeof(float))
    {
      PyErr_Format(SoundTouchError, 
                   "numarray Float32 != float on this machine");
      return NULL;
    }

  if(!PyArg_ParseTuple(args, "Oi", &osound, &samplerate)) {
    return NULL;
  }

  typeObject = PyObject_CallMethod(osound, "type", NULL);
  type = NA_typeObjectToTypeNo(typeObject);
  Py_DECREF(typeObject);
  if(type != tFloat32)
    {
      PyErr_Format(SoundTouchError, "sounds must be Float32");
      return NULL;
    }

  sound = (PyArrayObject *) NA_InputArray(osound, tFloat32, NUM_C_ARRAY);
  if(!sound)
    {
      Py_XDECREF(sound);
      PyErr_Format(SoundTouchError, "couldn't convert array to PyArrayObject.");
      return NULL;
    }
  else if(sound->nd != 1)
    {
      Py_XDECREF(sound);
      PyErr_Format(SoundTouchError, "sound arrays must have 1 dimension.");
      return NULL;
    }

  samples = (Float32 *) NA_OFFSETDATA(sound);
  length = sound->dimensions[0];

  /* The real code */
  int items = 1024;
  const float *cur = samples;
  const float *end = samples + length;
  soundtouch::SAMPLETYPE stage[1024];
  BPMDetect bpm(2, samplerate);

  while(cur != end)
    {
      if(end - cur < items)
        items = end - cur;

      memcpy(stage, cur, items * sizeof(float));
      cur += items;

      bpm.inputSamples(stage, items / 2);
    }
  tempo = bpm.getBpm();

  Py_DECREF(sound);
  return Py_BuildValue("f", tempo);
}


static PyMethodDef soundtouch_methods[] = {

  {"find_bpm", soundtouch_find_bpm, METH_VARARGS,
   "Find the tempo of a chunk of sound. args: sound, samplerate)"},
  {NULL, NULL, 0, NULL}
};


extern "C" 
PyMODINIT_FUNC initsoundtouch(void)
{
  PyObject *module;

  if(PyType_Ready(&SoundTouchType) < 0)
    return;

  module = Py_InitModule3("soundtouch", soundtouch_methods,
                          "soundtouch audio processing library");
  

  Py_INCREF(&SoundTouchType);
  PyModule_AddObject(module, "SoundTouch", 
                     (PyObject *)&SoundTouchType);

  SoundTouchError = PyErr_NewException("soundtouch.error", NULL, NULL);
  Py_INCREF(SoundTouchError);
  PyModule_AddObject(module, "error", SoundTouchError);

  import_libnumarray();
}

