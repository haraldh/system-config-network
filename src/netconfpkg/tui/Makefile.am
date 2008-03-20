PYTHON_FILES = \
	__init__.py \
	NCPluginEthernetInterface.py \
	NCPluginIsdnInterface.py \
	NCPluginQethInterface.py \
	NCPluginModemInterface.py \
	NCTcpIp.py


EXTRA_DIST = $(PYTHON_FILES)

netconfpkgdir = $(pkgdatadir)/netconfpkg/tui
netconfpkg_PYTHON = $(PYTHON_FILES)

execdir = $(sbindir)

CLEANFILES := $(notdir $(wildcard *~)) $(notdir $(wildcard *\#)) $(notdir $(wildcard \.\#*)) $(notdir $(wildcard *.gladep)) $(notdir $(wildcard *.pyc))
