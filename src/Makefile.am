SUBDIRS=netconfpkg pixmaps doc

PYTHON_FILES = netconf.py 

GLADE_FILES = maindialog.glade 

EXTRA_DIST = $(PYTHON_FILES) $(GLADE_FILES) providerdb

execdir = $(sbindir)

all-local:
	rm -f redhat-config-network
	rm -f redhat-config-network-cmd
	ln -s netconf.py redhat-config-network
	ln -s netconf.py redhat-config-network-cmd

pythondir = $(pkgdatadir)
python_DATA = $(PYTHON_FILES)

gladedir = $(pkgdatadir)/netconfpkg
glade_DATA = $(GLADE_FILES)

providerdir = $(pkgdatadir)/netconfpkg
provider_DATA = providerdb

install-exec-local:
	mkdir -p $(DESTDIR)$(pkgdatadir) $(DESTDIR)$(sbindir)
	install -m 0755 $(srcdir)/netconf.py $(DESTDIR)$(pkgdatadir)/
	ln  -s $(pkgdatadir)/netconf.py $(DESTDIR)$(sbindir)/redhat-config-network
	ln  -s $(pkgdatadir)/netconf.py $(DESTDIR)$(sbindir)/redhat-config-network-cmd
	ln  -s $(pkgdatadir)/netconf.py $(DESTDIR)$(sbindir)/neat

docs:
	python ./pydoc.py -w $(PYTHON_FILES)
	mv *.html doc

check-local:
	pychecker $(PYTHON_FILES)

clean:
	rm -f *.pyo *.pyc
	rm -f ${BUILT_SOURCES}
