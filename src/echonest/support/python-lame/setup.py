#!/usr/bin/env python2.3

from distutils.core import setup
from distutils.extension import Extension

setup(
	name = "py-lame",
	description = "OO interface to LAME",
	version = "0.x",
	author = "Alexander Leidinger",
	author_email = "Alexander@Leidinger.net",
	url = "http://lame.sourceforge.net/",
	license = "BSD",
	ext_modules = [ 
		Extension("lame",
			["lamemodule.c"],
			include_dirs = ["/usr/local/include"],
			library_dirs = ["/usr/local/lib"],
			libraries = ["mp3lame"])
	],
	scripts = ['slame'],
	data_files = [ ('share/docs/py-lame', ['API', 'README']) ],
)
