SUBDIRS=netconfpkg pixmaps doc

PYTHON_FILES = netconf.py netconf-tui.py neat-control.py

GLADE_FILES = maindialog.glade neat-control.glade

EXTRA_DIST = $(PYTHON_FILES) $(GLADE_FILES) providerdb glade-strings.c module-info isdnup

sbin_PROGRAMS = userisdnctl
userisdnctl_SOURCES = userisdnctl.c isdn.h isdnif.h

execdir = $(sbindir)

all-local: 
	rm -f redhat-config-network
	rm -f redhat-config-network-cmd
	rm -f redhat-config-network-druid
	rm -f  redhat-control-network
	ln -s netconf.py redhat-config-network
	ln -s netconf.py redhat-config-network-cmd
	ln -s netconf.py redhat-config-network-druid
	ln -s neat-control.py redhat-control-network

dist-local: glade-strings.c 

glade-strings.c:  $(GLADE_FILES) $(wildcard $(srcdir)/netconfpkg/gui/*.glade)
	libglade-xgettext -c -o $(srcdir)/glade-strings.c $^

pythondir = $(pkgdatadir)
###python_DATA = $(PYTHON_FILES)

gladedir = $(pkgdatadir)/netconfpkg/gui
glade_DATA = $(GLADE_FILES)

providerdir = $(pkgdatadir)
provider_DATA = providerdb

moduleinfodir = $(pkgdatadir)
moduleinfo_DATA = module-info

install-exec-local:
	mkdir -p $(DESTDIR)$(pkgdatadir) $(DESTDIR)$(sbindir) $(DESTDIR)$(bindir)
	install -m 0755 $(srcdir)/netconf.py $(DESTDIR)$(pkgdatadir)/
	install -m 0755 $(srcdir)/netconf-tui.py $(DESTDIR)$(pkgdatadir)/
	install -m 0755 $(srcdir)/neat-control.py $(DESTDIR)$(pkgdatadir)/
	install -m 0755 $(srcdir)/isdnup $(DESTDIR)$(sbindir)/
	softdir=$(pkgdatadir); \
	p=$(DESTDIR) ; \
	softdir=$${softdir/#$$p} ; \
	p=$(prefix) ; \
	softdir=$${softdir/#$$p} ; \
	softdir=$${softdir/#\/} ; \
	ln  -fs ../$${softdir}/neat-control.py $(DESTDIR)$(bindir)/neat-control; \
	ln  -fs ../$${softdir}/neat-control.py $(DESTDIR)$(bindir)/redhat-control-network; \
	ln  -fs ../$${softdir}/netconf.py $(DESTDIR)$(sbindir)/redhat-config-network; \
	ln  -fs ../$${softdir}/netconf.py $(DESTDIR)$(sbindir)/redhat-config-network-cmd; \
	ln  -fs ../$${softdir}/netconf.py $(DESTDIR)$(sbindir)/redhat-config-network-druid; \
	ln  -fs ../$${softdir}/netconf.py $(DESTDIR)$(sbindir)/neat; \
	ln  -fs ../$${softdir}/netconf-tui.py $(DESTDIR)$(sbindir)/neat-tui; \
	ln  -fs ../$${softdir}/netconf.py $(DESTDIR)$(sbindir)/internet-druid ;

uninstall-local:
	rm -fr $(DESTDIR)$(pkgdatadir)
	rm -f  $(DESTDIR)$(sbindir)/isdnup
	rm -f  $(DESTDIR)$(bindir)/neat-control 
	rm -f  $(DESTDIR)$(bindir)/redhat-control-network
	rm -f  $(DESTDIR)$(sbindir)/redhat-config-network
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
	rm -f *.pyo *.pyc
	rm -f ${BUILT_SOURCES}
