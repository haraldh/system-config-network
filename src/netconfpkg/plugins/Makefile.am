
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
netconfpkg_DATA = $(PYTHON_FILES) 

clean:
	rm -f *.pyo *.pyc
	rm -f *.so
	rm -f *~

install-data-local: install-netconfpkgDATA
	$(top_srcdir)/py-compile $(DESTDIR)$(netconfpkgdir)/*.py

uninstall-local:
	rm -f $(DESTDIR)$(netconfpkgdir)/*.py?
