#!/bin/sh
# Run this to generate all the initial makefiles, etc.

srcdir=`dirname $0`
test -z "$srcdir" && srcdir=.

THEDIR=`pwd`
cd $srcdir

DIE=0

glib-gettextize --copy --force
intltoolize --copy -f --automake
aclocal -I m4

autoreconf -i -m -f -I m4
cd $THEDIR

$srcdir/configure --enable-maintainer-mode "$@"

echo 
echo "Now type 'make' to compile system-config-network."
