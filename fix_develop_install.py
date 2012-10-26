#!/usr/bin/env python
# Fixes the paths due to package dirs being ignored by setup.py develop:
# https://bitbucket.org/tarek/distribute/issue/177/setuppy-develop-doesnt-support-package_dir

# Run this, with sudo, after running python setup.py develop.  

import sys
import os

# Get the location of easy-install.pth
temp_path = sys.path
final_python_path =  list(set(temp_path))
for path in final_python_path:
    try:
        files = os.listdir(path)
        if "easy-install.pth" in files:
            path_to_easy_install = path
            break
    except OSError: # In case sys.path has dirs that have been deleted
        pass

# Get the location of the remix installaton.
f = open(path_to_easy_install + os.sep + 'remix.egg-link', 'r')
for line in f:
    if os.sep in line:
        path_to_remix = line.strip()
        break
f.close()

# Do the modfication:
easy_install_path = path_to_easy_install + os.sep + 'easy-install.pth'
remix_source_string = path_to_remix + os.sep + "src\n"
pyechonest_source_string = path_to_remix + os.sep + "pyechonest\n"

print "Adding %s and %s to %s" % (remix_source_string, pyechonest_source_string, easy_install_path)
f = open(easy_install_path, 'a')
f.write(remix_source_string)
f.write(pyechonest_source_string)
f.close()
