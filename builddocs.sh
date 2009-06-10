#!/bin/sh
svn delete --force apidocs
epydoc --config epydoc.cfg --name "The Echo Nest Remix API, SVN `svn info | grep '^Revision: '`"
svn add apidocs