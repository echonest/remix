#include <Python.h>
#include <numpy/arrayobject.h>
#include <numpy/libnumarray.h>
#include <stdexcept>
#include <math.h>
#include <string.h>
#ifndef M_PI_2
#define M_PI_2  1.57079632679489661923 /* pi/2 */
#endif
#define DIMENSIONS 2

enum modes {LINEAR, EQUAL_POWER};
typedef unsigned int uint;
static PyObject *ActionError;

static float limiter(float f)
{
    const float DYN_RANGE  = 32767.0f;
    const float LIM_THRESH = 30000.0f;
    const float LIM_RANGE  = (DYN_RANGE - LIM_THRESH);
    float result = f;
    
    if (LIM_THRESH < f)
    {
        result = (f - LIM_THRESH) / LIM_RANGE;
        result = (atan(result) / M_PI_2) * LIM_RANGE + LIM_THRESH;
    }
    else if (f < -LIM_THRESH)
    {
        result = -(f + LIM_THRESH) / LIM_RANGE;
        result = -((atan(result) / M_PI_2) * LIM_RANGE + LIM_THRESH);
    }
    
    return result;
}

#define CROSSFADE_COEFF 0.6f
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

PyArrayObject *get_pyarray(PyObject *objInSound)
{
    // Convert to actual PyArray with proper type
    PyArrayObject *inSound = (PyArrayObject *) NA_InputArray(objInSound, tFloat32, NUM_C_ARRAY);
    
    // Check that everything looks good
    if (!inSound)
    {
        Py_XDECREF(inSound);
        PyErr_Format(ActionError, "couldn't convert array to PyArrayObject.");
        return NULL;
    }
    
    if (inSound->nd != 1 && inSound->nd != 2) 
    {
        Py_XDECREF(inSound);
        PyErr_Format(ActionError, "sound arrays must have 1 (mono) or 2 (stereo) dimensions.");
        return NULL;
    }
    
    return inSound;
}

static PyObject* cAction_limit(PyObject* self, PyObject* args)
{
    PyObject *objInSound;
    if (!PyArg_ParseTuple(args, "O", &objInSound))
        return NULL;
    
    PyArrayObject *inSound = get_pyarray(objInSound);
    if (inSound == NULL)
        return NULL;
    
    uint nSamples = inSound->dimensions[0];
    uint nChannels = inSound->dimensions[1];
    float *inSamples = (Float32 *)NA_OFFSETDATA(inSound);
    
    // Limit:
    for (uint j = 0; j < nChannels; j++)
    {
        for (uint i = 0; i < nSamples; i++)
        {
            float f = inSamples[nChannels*i  + j];
            inSamples[nChannels*i + j] = limiter(f);
        }
    }
    
    // Do we need to make a copy before returning, or can we return the modified original?
    return PyArray_Return(inSound);
}

static PyObject* cAction_fade(PyObject* self, PyObject* args)
{
    PyObject *objInSound;
    float volume = 1.0f;
    float from = 0.0f;
    float to = 1.0f;
    
    if (!PyArg_ParseTuple(args, "O|f|f|f", &objInSound, &volume, &from, &to))
        return NULL;
    
    PyArrayObject *inSound = get_pyarray(objInSound);
    if (inSound == NULL)
        return NULL;
    
    uint nSamples = inSound->dimensions[0];
    uint nChannels = inSound->dimensions[1];
    float *inSamples = (Float32 *)NA_OFFSETDATA(inSound);
    
    // Limit:
    for (uint j = 0; j < nChannels; j++)
    {
        for (uint i = 0; i < nSamples; i++)
        {
            float frac = ((float)(nSamples - i) / (float) nSamples) * (to - from) + from;
            float f = inSamples[nChannels * i + j];
            inSamples[nChannels * i + j] = limiter(frac * f * volume);
        }
    }
    
    // Do we need to make a copy before returning, or can we return the modified original?
    return PyArray_Return(inSound);
}


static PyObject* cAction_fade_out(PyObject* self, PyObject* args)
{
    PyObject *objInSound;
    float volume = 1.0f;
    
    if (!PyArg_ParseTuple(args, "O|f", &objInSound, &volume))
        return NULL;
    
    PyArrayObject *inSound = get_pyarray(objInSound);
    if (inSound == NULL)
        return NULL;
    
    uint nSamples = inSound->dimensions[0];
    uint nChannels = inSound->dimensions[1];
    float *inSamples = (Float32 *)NA_OFFSETDATA(inSound);
    
    // Limit:
    for (uint j = 0; j < nChannels; j++)
    {
        for (uint i = 0; i < nSamples; i++)
        {
            float frac = (float)(nSamples-i) / (float)nSamples;
            float f = inSamples[nChannels*i + j];
            inSamples[nChannels*i + j] = limiter(frac * f * volume);
        }
    }
    
    // Do we need to make a copy before returning, or can we return the modified original?
    return PyArray_Return(inSound);
}

static PyObject* cAction_fade_in(PyObject* self, PyObject* args)
{
    PyObject *objInSound;
    float volume = 1.0f;
    
    if (!PyArg_ParseTuple(args, "O|f", &objInSound, &volume))
        return NULL;
    
    PyArrayObject *inSound = get_pyarray(objInSound);
    if (inSound == NULL)
        return NULL;
    
    uint nSamples = inSound->dimensions[0];
    uint nChannels = inSound->dimensions[1];
    float *inSamples = (Float32 *)NA_OFFSETDATA(inSound);
    
    // Limit:
    for (uint j = 0; j < nChannels; j++)
    {
        for (uint i = 0; i < nSamples; i++)
        {
            float frac = 1.0f - ((float)(nSamples-i) / (float)nSamples);
            float f = inSamples[nChannels*i + j];
            inSamples[nChannels*i + j] = limiter(frac * f * volume);
        }
    }
    
    // Do we need to make a copy before returning, or can we return the modified original?
    return PyArray_Return(inSound);
}

static PyObject* cAction_crossfade(PyObject* self, PyObject* args)
{
    PyObject *objInSound1, *objInSound2;
    char* s_mode = NULL;

    //  Hacky - the percentage through the crossfade that we're processing.
    //  Allows for incremental processing of the same crossfade in chunks.
    
    long total = -1;
    long offset = 0;

    if (!PyArg_ParseTuple(args, "OO|sll", &objInSound1, &objInSound2, &s_mode, &total, &offset))
        return NULL;
    
    PyArrayObject *inSound1 = get_pyarray(objInSound1);
    if (inSound1 == NULL)
        return NULL;
    PyArrayObject *inSound2 = get_pyarray(objInSound2);
    if (inSound2 == NULL)
    {
        Py_XDECREF(inSound1);
        return NULL;
    }
    
    float* inSamples1 = (float *)inSound1->data;
    float* inSamples2 = (float *)inSound2->data;
    
    uint numInSamples = inSound1->dimensions[0];
    uint numInChannels = inSound1->dimensions[1];
    
    npy_intp dims[DIMENSIONS];
    dims[0] = numInSamples;
    dims[1] = numInChannels;

    if ( total < 0 ) {
        total = numInSamples;
    } 
        
    // Allocate interlaced memory for output sound object
    PyArrayObject* outSound = (PyArrayObject *)PyArray_SimpleNew(DIMENSIONS, dims, NPY_FLOAT);
    
    // Get the actual array
    float* outSamples = (float *)outSound->data;
    
    // Figure out which crossfade to use.
    float (*fader)(float, float, long, long) = strcmp(s_mode, "linear") == 0 ? linear : equal_power;
    for (uint i = 0; i < numInChannels; i++)
    {
        for (uint j = 0; j < numInSamples; j++)
        {
            uint index = i + j*numInChannels;
            outSamples[index] = fader(inSamples1[index], inSamples2[index], (j + offset > total ? total : j + offset), total);
        }
    }
    
    Py_DECREF(inSound1);
    Py_DECREF(inSound2);
    return PyArray_Return(outSound);
}

static PyMethodDef cAction_methods[] = 
{
    {"limit", (PyCFunction) cAction_limit, METH_VARARGS, "limit an audio buffer so as not to clip."},
    {"crossfade", (PyCFunction) cAction_crossfade, METH_VARARGS, "crossfade two audio buffers."},
    {"fadein", (PyCFunction) cAction_fade_in, METH_VARARGS, "fade in an audio buffer."},
    {"fadeout", (PyCFunction) cAction_fade_out, METH_VARARGS, "fade out an audio buffer."},
    {"fade", (PyCFunction) cAction_fade, METH_VARARGS, "fade an audio buffer between two volumes."},
    {NULL}
};

PyMODINIT_FUNC initcAction(void) 
{
    Py_InitModule3("cAction", cAction_methods, "c ext for action.py");
    ActionError = PyErr_NewException("cAction.error", NULL, NULL);
    Py_INCREF(ActionError);
    
    import_array();
    import_libnumarray();
}

