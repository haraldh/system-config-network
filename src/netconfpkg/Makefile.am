SUBDIRS=gui plugins tests

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
	NCHardware.py \
	NCHardwareList.py \
	NCHardwareFactory.py \
	NCisdnhardware.py \
	NCProfileList.py \
	NCWireless.py \
	Control.py \
	NCCard.py \
	NCDeviceFactory.py


EXTRA_DIST = $(IDL_FILES) $(PYTHON_FILES)

netconfpkgdir = $(pkgdatadir)/netconfpkg
netconfpkg_DATA = $(PYTHON_FILES) $(IDL_FILES)

execdir = $(sbindir)

clean:
	rm -f *.pyo *.pyc
	rm -f *.so
	rm -f *~

install-data-local: install-netconfpkgDATA
	$(top_srcdir)/py-compile $(DESTDIR)$(netconfpkgdir)/*.py

uninstall-local:
	rm -f $(DESTDIR)$(netconfpkgdir)/*.py?
