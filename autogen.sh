#!/bin/sh
# Run this to generate all the initial makefiles, etc.

cp -p /usr/share/aclocal/nls.m4 m4/nls.m4
cp -p /usr/share/aclocal/po.m4 m4/po.m4
cp -p /usr/share/aclocal/progtest.m4 m4/progtest.m4
cp -p /usr/share/gettext/po/remove-potcdate.sin po/remove-potcdate.sin

DIE=0

intltoolize --copy -f --automake
aclocal -I m4

autoreconf -i -m -f -I m4
./configure --enable-maintainer-mode "$@"

echo
echo "Now type 'make' to compile system-config-network."

