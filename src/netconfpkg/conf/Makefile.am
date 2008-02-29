
PYTHON_FILES = \
	__init__.py \
	ConfPAP.py \
	Conf.py \
	ConfSMB.py

EXTRA_DIST = $(PYTHON_FILES)

netconfpkgdir = $(pkgdatadir)/netconfpkg/conf
netconfpkg_PYTHON = $(PYTHON_FILES) 

CLEANFILES := $(notdir $(wildcard *~)) $(notdir $(wildcard *\#)) $(notdir $(wildcard \.\#*)) $(notdir $(wildcard *.pyc))

