SUBDIRS=netconfpkg pixmaps doc

PYTHON_FILES = netconf.py netconf-tui.py neat-control.py netconf-cmd.py version.py

GLADE_FILES = neat-control.glade

EXTRA_DIST = $(PYTHON_FILES) $(GLADE_FILES) providerdb module-info

execdir = $(sbindir)

version.py: version.py.in

all-local: version.py 
	rm -f redhat-config-network
	rm -f redhat-config-network-cmd
	rm -f redhat-config-network-tui
	rm -f redhat-config-network-druid
	rm -f  redhat-control-network
	ln -s $(srcdir)/netconf.py redhat-config-network
	ln -s $(srcdir)/netconf-cmd.py redhat-config-network-cmd
	ln -s $(srcdir)/netconf.py redhat-config-network-druid
	ln -s $(srcdir)/netconf-tui.py redhat-config-network-tui
	ln -s $(srcdir)/neat-control.py redhat-control-network
	chmod 0755 redhat-config-network redhat-config-network-cmd 
	chmod 0755 redhat-config-network-druid redhat-config-network-tui redhat-control-network

gladedir = $(pkgdatadir)/netconfpkg/gui
glade_DATA = $(GLADE_FILES)

providerdir = $(pkgdatadir)
provider_DATA = providerdb

moduleinfodir = $(pkgdatadir)
moduleinfo_DATA = module-info

install-exec-local:
	mkdir -p $(DESTDIR)$(pkgdatadir) $(DESTDIR)$(sbindir) $(DESTDIR)$(bindir)
	install -m 0755 $(srcdir)/version.py $(DESTDIR)$(pkgdatadir)/
	install -m 0755 $(srcdir)/netconf.py $(DESTDIR)$(pkgdatadir)/
	install -m 0755 $(srcdir)/netconf-cmd.py $(DESTDIR)$(pkgdatadir)/
	install -m 0755 $(srcdir)/netconf-tui.py $(DESTDIR)$(pkgdatadir)/
	install -m 0755 $(srcdir)/neat-control.py $(DESTDIR)$(pkgdatadir)/
	softdir=$(pkgdatadir); \
	p=$(DESTDIR) ; \
	softdir=$${softdir/#$$p} ; \
	p=$(prefix) ; \
	softdir=$${softdir/#$$p} ; \
	softdir=$${softdir/#\/} ; \
	ln  -fs ../$${softdir}/neat-control.py $(DESTDIR)$(bindir)/neat-control; \
	ln  -fs ../$${softdir}/neat-control.py $(DESTDIR)$(bindir)/redhat-control-network; \
	ln  -fs ../$${softdir}/netconf.py $(DESTDIR)$(sbindir)/redhat-config-network; \
	ln  -fs ../$${softdir}/netconf-cmd.py $(DESTDIR)$(sbindir)/redhat-config-network-cmd; \
	ln  -fs ../$${softdir}/netconf.py $(DESTDIR)$(sbindir)/redhat-config-network-druid; \
	ln  -fs ../$${softdir}/netconf.py $(DESTDIR)$(sbindir)/neat; \
	ln  -fs ../$${softdir}/netconf-tui.py $(DESTDIR)$(sbindir)/redhat-config-network-tui; \
	ln  -fs ../$${softdir}/netconf-tui.py $(DESTDIR)$(sbindir)/neat-tui; \
	ln  -fs ../$${softdir}/netconf.py $(DESTDIR)$(sbindir)/internet-druid ;

uninstall-local:
	rm -fr $(DESTDIR)$(pkgdatadir)
	rm -f  $(DESTDIR)$(bindir)/neat-control 
	rm -f  $(DESTDIR)$(bindir)/redhat-control-network
	rm -f  $(DESTDIR)$(sbindir)/redhat-config-network
	rm -f  $(DESTDIR)$(sbindir)/redhat-config-network-tui
	rm -f  $(DESTDIR)$(sbindir)/redhat-config-network-cmd
	rm -f  $(DESTDIR)$(sbindir)/redhat-config-network-druid
	rm -f  $(DESTDIR)$(sbindir)/neat
	rm -f  $(DESTDIR)$(sbindir)/neat-tui
	rm -f  $(DESTDIR)$(sbindir)/neat-druid

docs:
	cd $(srcdir)
	python @PYDOC@ -w $(PYTHON_FILES)
	mv *.html doc

pycheck:
	pychecker -F $(top_srcdir)/pycheckrc $(PYTHON_FILES)

clean:
	rm -f *.pyo *.pyc *~ *\#
	rm -f ${BUILT_SOURCES}
