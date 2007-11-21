PYTHON_FILES = \
	__init__.py \
	NCEthernetInterface.py \
	NCIsdnInterface.py \
	NCModemInterface.py \
	NCTcpIp.py


EXTRA_DIST = $(PYTHON_FILES)

netconfpkgdir = $(pkgdatadir)/netconfpkg/tui
netconfpkg_PYTHON = $(PYTHON_FILES)

execdir = $(sbindir)

CLEANFILES := $(notdir $(wildcard *~)) $(notdir $(wildcard *\#)) $(notdir $(wildcard \.\#*)) $(notdir $(wildcard *.gladep)) $(notdir $(wildcard *.pyc))
