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

glade-strings.c: *.glade  netconfpkg/*.glade
	libglade-xgettext -c -o $(srcdir)/glade-strings.c $?

pythondir = $(pkgdatadir)
###python_DATA = $(PYTHON_FILES)

gladedir = $(pkgdatadir)/netconfpkg
glade_DATA = $(GLADE_FILES)

providerdir = $(pkgdatadir)
provider_DATA = providerdb

install-exec-local:
	mkdir -p $(DESTDIR)$(pkgdatadir) $(DESTDIR)$(sbindir)
	install -m 0755 $(srcdir)/netconf.py $(DESTDIR)$(pkgdatadir)/
	softdir=$(pkgdatadir); \
	p=$(DESTDIR) ; \
	softdir=$${softdir/#$$p} ; \
	p=$(prefix) ; \
	softdir=$${softdir/#$$p} ; \
	softdir=$${softdir/#\/} ; \
	ln  -fs ../$${softdir}/netconf.py $(DESTDIR)$(sbindir)/redhat-config-network; \
	ln  -fs ../$${softdir}/netconf.py $(DESTDIR)$(sbindir)/redhat-config-network-cmd; \
	ln  -fs ../$${softdir}/netconf.py $(DESTDIR)$(sbindir)/neat ;

docs:
	python /usr/lib/python1.5/pydoc.py -w $(PYTHON_FILES)
	mv *.html doc

check-local:
	pychecker $(PYTHON_FILES)

clean:
	rm -f *.pyo *.pyc
	rm -f ${BUILT_SOURCES}
