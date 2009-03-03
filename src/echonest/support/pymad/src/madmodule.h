/* $Id: madmodule.h,v 1.1 2002/06/17 01:16:56 jaq Exp $
 *
 * python interface to libmad (the mpeg audio decoder library)
 *
 * Copyright (c) 2002 Jamie Wilkinson
 *
 * This program is free software, you may copy and/or modify as per
 * the GNU General Public License (version 2, or at your discretion,
 * any later version).  This is the same license as libmad.
 */

#ifndef __MADMODULE_H__
#define __MADMODULE_H__

#include <Python.h>

/* module accessible functions */
PyObject * py_madfile_new(PyObject *, PyObject *);

#endif /* __MADMODULE_H__ */
