
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
	NCHWWireless.py \
	NCHWTokenring.py

EXTRA_DIST = $(PYTHON_FILES)

netconfpkgdir = $(pkgdatadir)/netconfpkg/plugins
netconfpkg_PYTHON = $(PYTHON_FILES) 

CLEANFILES := $(notdir $(wildcard *~)) $(notdir $(wildcard *\#)) $(notdir $(wildcard \.\#*)) $(notdir $(wildcard *.pyc))

