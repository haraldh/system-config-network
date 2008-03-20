SUBDIRS=gui tui plugins tests conf

IDL_FILES = \
	DeviceList.idl \
	Firewall.idl \
	HardwareList.idl \
	IPsecList.idl \
	NetworkList.idl \
	ProfileList.idl \
	ProviderList.idl

PYTHON_FILES = \
	__init__.py \
	exception.py \
	genClass.py \
	genClassMap.py \
	ipcalc.py \
	log.py \
	NCAliasList.py \
	NCBackendHal.py \
	NCCallback.py \
	NCCompression.py \
	NCDeviceList.py \
	NCDevice.py \
	NCDialup.py \
	NCException.py \
	NC_functions.py \
	NCHardware.py \
	NCHardwareList.py \
	NCHardwareFactory.py \
	NCHostsList.py \
	NCHost.py \
	NCisdnhardware.py \
	NCIPsec.py \
	NCIPsecList.py \
	NCProfileList.py \
	NCRoute.py \
	NCWireless.py \
	Control.py \
	NCCard.py \
	NCDeviceFactory.py

EXTRA_DIST = $(IDL_FILES) $(PYTHON_FILES)

netconfpkgdir = $(pkgdatadir)/netconfpkg
netconfpkg_DATA = $(IDL_FILES)
netconfpkg_PYTHON = $(PYTHON_FILES)

execdir = $(sbindir)

CLEANFILES := $(notdir $(wildcard *~)) $(notdir $(wildcard *\#)) $(notdir $(wildcard \.\#*)) $(notdir $(wildcard *.pyc))

check-local:
	@for i in $(notdir $(wildcard *.py)) $(notdir $(wildcard *.idl)); do echo $(IDL_FILES) $(PYTHON_FILES)|grep -q $$i || (echo $$i is missing;false) || exit 1;done && echo "Source file check PASSED"
