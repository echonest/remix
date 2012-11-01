#include <Python.h>
#include <numpy/arrayobject.h>
#include <numpy/libnumarray.h>
#include "source/Dirac.h"
#include "source/Dirac_LE.h"
#include <stdexcept>

#define DIMENSIONS 2

#ifndef Py_RETURN_NONE
#define Py_RETURN_NONE Py_INCREF(Py_None); return Py_None;
#endif

static PyObject *DiracError;

static PyObject *Dirac_timeScale(PyObject *self, PyObject *args) 
{
    // Only for lists:
    double *listInDurations = NULL;
    double *listOutDurations = NULL; 
    uint numChunks = 0; 
    
    float rate = 1.0f; // Only for single rates
    uint sampleRate = 44100;// default
    uint quality = 0;       // default
    
    // Parse input sound object, a numpy array.
    PyObject *objInSound, *objRate;
    if (!PyArg_ParseTuple(args, "OO|ii", &objInSound, &objRate, &sampleRate, &quality))
        return NULL;
    
    // Convert to actual PyArray with proper type
    PyArrayObject *inSound = (PyArrayObject *) NA_InputArray(objInSound, tFloat32, NUM_C_ARRAY);
    
    // Check that everything looks good
    if (!inSound) 
    {
        Py_XDECREF(inSound);
        PyErr_Format(DiracError, "couldn't convert array to PyArrayObject.");
        return NULL; 
    } 
    if (inSound->nd != 1 && inSound->nd != 2) 
    {
        Py_XDECREF(inSound);
        PyErr_Format(DiracError, "sound arrays must have 1 (mono) or 2 (stereo) dimensions.");
        return NULL;
    }
    
    if (!PyList_Check(objRate) && !PyFloat_Check(objRate)) 
    {
        PyErr_Format(DiracError, "expecting a float or list of tuples as second argument.");
        return NULL;
    }
    
    // Are we dealing with a list or a float?
    bool isList = PyList_Check(objRate);
    
    uint numOutSamples = 0;
    uint numInSamples = inSound->dimensions[0];
    uint numInChannels = inSound->dimensions[1];
    uint numOutChannels = numInChannels;
    
    // Main switch
    if (isList) 
    {
        numChunks = (uint) PyList_Size(objRate);
        // Let's add one more space in the case there's no 0 index
        long *listIndexes = (long *)malloc(numChunks * sizeof(long));
        double *listRates = (double *)malloc(numChunks * sizeof(double));
        
        for (uint i = 0; i < numChunks; i++)
        {
            PyObject *item = PyList_GetItem(objRate, i);
            if (!PyTuple_Check(item)) 
            {
                PyErr_Format(DiracError, "expecting a list of tuples for second argument.");
                return NULL;
            }
            
            long index = (long) PyLong_AsLong(PyTuple_GetItem(item, 0));
            double rate = (double) PyFloat_AsDouble(PyTuple_GetItem(item, 1));
            
            if (i == 0 && index != 0) 
            {
                PyErr_Format(DiracError, "first index must be 0.");
                return NULL;
            }
            if ((long)numInSamples < index)
            {
                PyErr_Format(DiracError, "at least one index goes beyond the limits of the array.");
                return NULL;
            }
            
            listIndexes[i] = index;
            listRates[i] = rate;
        }
        
        listInDurations = (double *)malloc(numChunks * sizeof(double));
        listOutDurations = (double *)malloc(numChunks * sizeof(double));
        
        for (uint i = 0; i < numChunks; i++)
        {   
            long thisNumSamples = 0;
            if (i == numChunks-1) 
                thisNumSamples = numInSamples - listIndexes[numChunks-1];
            else
                thisNumSamples = listIndexes[i+1] - listIndexes[i];
            numOutSamples += int(thisNumSamples * listRates[i]);
            listInDurations[i] = (double)thisNumSamples / sampleRate;
            listOutDurations[i] = listInDurations[i] * listRates[i];
        }
        
        free(listIndexes);
        free(listRates);
    }
    else 
    {
        rate = (float) PyFloat_AsDouble(objRate);
        numOutSamples = (uint)(numInSamples * rate);
    }
    
    // Create buffers we'll use for processing
    float **inSamples = allocateAudioBuffer(numInChannels, numInSamples);
    float **outSamples = allocateAudioBuffer(numOutChannels, numOutSamples);
    
    // For now, Dirac uses non-interlaced buffers. Make a copy.
    float *interlacedInSamples = (Float32 *) NA_OFFSETDATA(inSound);
    deinterlace(inSamples, interlacedInSamples, numInSamples, numInChannels);
    
    // Convert to real floats between -1 and 1 before processing...
    for (uint i = 0; i < numInSamples; i++)
    {
        inSamples[0][i] /= 32768.0f;
        inSamples[1][i] /= 32768.0f;
    }
    
    try 
    {
        // Actual time stretching
        if (isList) 
        {
            if (time_scale_list(outSamples, listOutDurations, inSamples, listInDurations, numChunks, numInChannels, (float)sampleRate, quality) < 0)
            {
                PyErr_Format(DiracError, "problem with time_scale_list.");
                return NULL;
            }
            free(listInDurations);
            free(listOutDurations);
        }
        else 
        {
            if (time_scale(outSamples, (double)numOutSamples/sampleRate, inSamples, (double)numInSamples/sampleRate, numInChannels, (float)sampleRate, quality) < 0) 
            {
                PyErr_Format(DiracError, "problem with time_scale.");
                return NULL;
            }
        }
    }
    catch (std::runtime_error &error) 
    {
        PyErr_Format(PyExc_RuntimeError, error.what());
        return NULL;
    }
    
    for (uint i = 0; i < numOutSamples; i++) 
    {
        outSamples[0][i] = limiter(outSamples[0][i]) * 32768.0f; // Not sure why limiting is necessary!
        outSamples[1][i] = limiter(outSamples[1][i]) * 32768.0f;
    }
    
    // Set dimensions for output object
    npy_intp dims[DIMENSIONS];
    dims[0] = numOutSamples;
    dims[1] = numOutChannels;
    
    // Allocate interlaced memory for output sound object
    PyArrayObject* outSound = (PyArrayObject *)PyArray_SimpleNew(DIMENSIONS, dims, NPY_FLOAT);
    
    // Get the actual array
    float* interlacedOutSamples = (float *)outSound->data;
    
    // Copy processed data into the interlaced buffer of floats
    interlace(interlacedOutSamples, outSamples, numOutSamples, numOutChannels);
    
    // Deallocate memory we don't need anymore
    deallocateAudioBuffer(inSamples, numInChannels);
    deallocateAudioBuffer(outSamples, numOutChannels);
    
    // Dealloc the temporary array we used to avoid leaking it!
    Py_DECREF(inSound);

    return PyArray_Return(outSound);
}

static PyMethodDef Dirac_methods[] = 
{
    {"timeScale", (PyCFunction) Dirac_timeScale, METH_VARARGS, "Time scale an audio buffer given a single rate, or a list of indexes and rates."},
    {NULL}
};

PyMODINIT_FUNC initdirac(void) 
{
    Py_InitModule3("dirac", Dirac_methods, "Dirac LE audio time-stretching library");
    
    DiracError = PyErr_NewException("dirac.error", NULL, NULL);
    Py_INCREF(DiracError);
    
    import_array();
    import_libnumarray();
}