
PYTHON_FILES = \
	__init__.py \
	NCDevADSL.py \
	NCDevCipe.py \
	NCDevEthernet.py \
	NCDevIsdn.py \
	NCDevModem.py \
	NCDevTokenRing.py \
	NCDevWireless.py \
	NCHWEthernet.py \
	NCHWIsdn.py \
	NCHWModem.py \
	NCHWTokenring.py

BUILT_SOURCES = $(if $(shell test -w $srcdir && echo OK), \
		     $(patsubst %.py,%.pyc,$(PYTHON_FILES))) __init__.py


EXTRA_DIST = $(PYTHON_FILES)

netconfpkgdir = $(pkgdatadir)/netconfpkg/plugins
netconfpkg_DATA = $(PYTHON_FILES) $(BUILT_SOURCES) 


INCLUDES = -I/usr/include/python2.2


execdir = $(sbindir)

clean:
	rm -f *.pyo *.pyc
	rm -f ${BUILT_SOURCES}
	rm -f *.so
	rm -f *~

%.pyc: %.py
	@echo "Compiling because of " $*
	@PYTHON@ @PY_COMPILEALL@ -l -d . $srcdir
