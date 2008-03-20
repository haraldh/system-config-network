
PYTHON_FILES = \
	__init__.py \
	NCPluginDevADSL.py \
	NCPluginDevEthernet.py \
	NCPluginDevIsdn.py \
	NCPluginDevModem.py \
	NCPluginDevTokenRing.py \
	NCPluginDevWireless.py \
	NCPluginHWEthernet.py \
	NCPluginHWIsdn.py \
	NCPluginHWModem.py \
	NCPluginHWWireless.py \
	NCPluginHWTokenring.py \
	NCPluginHWQeth.py \
	NCPluginDevQeth.py

EXTRA_DIST = $(PYTHON_FILES)

netconfpkgdir = $(pkgdatadir)/netconfpkg/plugins
netconfpkg_PYTHON = $(PYTHON_FILES) 

CLEANFILES := $(notdir $(wildcard *~)) $(notdir $(wildcard *\#)) $(notdir $(wildcard \.\#*)) $(notdir $(wildcard *.pyc))

