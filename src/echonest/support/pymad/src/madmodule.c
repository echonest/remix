/* $Id: madmodule.c,v 1.4 2002/08/18 06:21:48 jaq Exp $
 *
 * python interface to libmad (the mpeg audio decoder library)
 *
 * Copyright (c) 2002 Jamie Wilkinson
 *
 * This program is free software, you may copy and/or modify as per
 * the GNU General Public License (version 2, or at your discretion,
 * any later version).  This is the same license as libmad.
 */

#include <mad.h>
#include "madmodule.h"

static PyMethodDef mad_methods[] = {
    { "MadFile", py_madfile_new, METH_VARARGS, "" },
    { NULL, 0, 0, NULL }
};

/* this handy tool for passing C constants to Python-land from
 * http://starship.python.net/crew/arcege/extwriting/pyext.html
 */
#define PY_CONST(x) PyDict_SetItemString(dict, #x, PyInt_FromLong(MAD_##x))

void initmad(void) {
    PyObject * module, * dict;

    module = Py_InitModule("mad", mad_methods);
    dict = PyModule_GetDict(module);

    PyDict_SetItemString(dict, "__version__",
			 PyString_FromString(VERSION));

    /* layer */
    PY_CONST(LAYER_I);
    PY_CONST(LAYER_II);
    PY_CONST(LAYER_III);

    /* mode */
    PY_CONST(MODE_SINGLE_CHANNEL);
    PY_CONST(MODE_DUAL_CHANNEL);
    PY_CONST(MODE_JOINT_STEREO);
    PY_CONST(MODE_STEREO);

    /* emphasis */
    PY_CONST(EMPHASIS_NONE);
    PY_CONST(EMPHASIS_50_15_US);
    PY_CONST(EMPHASIS_CCITT_J_17);

    if (PyErr_Occurred())
	PyErr_SetString(PyExc_ImportError, "mad: init failed");
}
