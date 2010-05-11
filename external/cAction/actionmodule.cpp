#include <Python.h>
#include <numpy/arrayobject.h>
#include <numpy/libnumarray.h>
#include <stdexcept>
#include <math.h>
#ifndef M_PI_2
#define M_PI_2  1.57079632679489661923 /* pi/2 */
#endif
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

static PyObject* cAction_limiter(PyObject* self, PyObject* args)
{
    float f;
    if (!PyArg_ParseTuple(args, "f", &f))
        return NULL;
        
    return PyFloat_FromDouble((double)limiter(f));
}

static PyObject* cAction_limit(PyObject* self, PyObject* args)
{
    PyObject *objInSound;
    if (!PyArg_ParseTuple(args, "O", &objInSound))
        return NULL;
    
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
    
    uint nSamples = inSound->dimensions[0];
    uint nChannels = inSound->dimensions[1];
    // inSamples is interlaced ... does it matter?
    float *inSamples = (Float32 *)NA_OFFSETDATA(inSound);
    
    // Limit:
    for (uint j = 0; j < nChannels; j++)
    {
        for (uint i = 0; i < nSamples; i++)
        {
            float f = inSamples[nChannels*i  + j];
            inSamples[nChannels*i  + j] = limiter(f);
        }
    }
    
    // Do we need to make a copy before returning, or can we return the modified original?
    return PyArray_Return(inSound);
}

static PyMethodDef cAction_methods[] = 
{
    {"limit", (PyCFunction) cAction_limit, METH_VARARGS, "limit an audio buffer so as not to clip."},
    {"limiter", (PyCFunction) cAction_limiter, METH_VARARGS, "limit a single number."},
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

