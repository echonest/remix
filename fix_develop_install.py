#!/usr/bin/env python


# Fixes the paths due to package dirs being ignored by setup.py develop
# https://bitbucket.org/tarek/distribute/issue/177/setuppy-develop-doesnt-support-package_dir
#


# Let's start by hard-coding the paths
f = open('/usr/local/lib/python2.7/dist-packages/easy-install.pth', 'a')
f.write("/home/thor/Code/remix/src\n")
f.write("/home/thor/Code/remix/pyechonest\n")
f.close()
