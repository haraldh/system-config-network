SUBDIRS=gui tests

IDL_FILES = \
	DeviceList.idl \
	Firewall.idl \
	HardwareList.idl \
	NetworkList.idl \
	ProfileList.idl \
	ProviderList.idl

PYTHON_FILES = \
	__init__.py \
	ipcalc.py \
	NCCallback.py \
	NCCipe.py \
	NCCompression.py \
	NCDeviceList.py \
	NCDevice.py \
	NCDialup.py \
	NC_functions.py \
	NCHardwareList.py \
	NCisdnhardware.py \
	NCProfileList.py \
	NCWireless.py \
	Control.py

BUILT_SOURCES = $(if $(shell test -w $srcdir && echo OK), \
		     $(patsubst %.py,%.pyc,$(PYTHON_FILES)))

EXTRA_DIST = $(IDL_FILES) $(PYTHON_FILES)

netconfpkgdir = $(pkgdatadir)/netconfpkg
netconfpkg_DATA = $(PYTHON_FILES) $(BUILT_SOURCES) $(IDL_FILES)


INCLUDES = -I/usr/include/python2.2


execdir = $(sbindir)

clean:
	rm -f *.pyo *.pyc
	rm -f ${BUILT_SOURCES}
	rm -f *.so

%.pyc: %.py
	@echo "Compiling because of " $*
	@PYTHON@ @PY_COMPILEALL@ -l -d . $srcdir
