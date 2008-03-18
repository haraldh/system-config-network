SUBDIRS=netconfpkg pixmaps 

PYTHON_FILES = netconf.py netconf_tui.py netconf_control.py netconf_cmd.py version.py

EXTRA_DIST = $(PYTHON_FILES) providerdb module-info

CLEANFILES := version.pyc $(notdir $(wildcard *~)) $(notdir $(wildcard *\#)) $(notdir $(wildcard \.\#*)) $(notdir $(wildcard *.pyc))

execdir = $(sbindir)


all-local: version.py 

providerdir = $(pkgdatadir)
provider_DATA = providerdb

moduleinfodir = $(pkgdatadir)
moduleinfo_DATA = module-info

install-exec-local: 
	mkdir -p $(DESTDIR)$(pkgdatadir) $(DESTDIR)$(sbindir) $(DESTDIR)$(bindir)
	install -m 0644 $(srcdir)/version.py $(DESTDIR)$(pkgdatadir)/
	install -m 0755 $(srcdir)/netconf.py $(DESTDIR)$(pkgdatadir)/
	install -m 0755 $(srcdir)/netconf_cmd.py $(DESTDIR)$(pkgdatadir)/
	install -m 0755 $(srcdir)/netconf_tui.py $(DESTDIR)$(pkgdatadir)/
	install -m 0755 $(srcdir)/netconf_control.py $(DESTDIR)$(pkgdatadir)/
	softdir=$(pkgdatadir); \
	p=$(DESTDIR) ; \
	softdir=$${softdir/#$$p} ; \
	p=$(prefix) ; \
	softdir=$${softdir/#$$p} ; \
	softdir=$${softdir/#\/} ; \
	ln  -fs ../$${softdir}/netconf_control.py $(DESTDIR)$(bindir)/system-control-network; \
	ln  -fs ../$${softdir}/netconf.py $(DESTDIR)$(sbindir)/system-config-network-gui; \
	ln  -fs ../$${softdir}/netconf_cmd.py $(DESTDIR)$(sbindir)/system-config-network-cmd; \
	ln  -fs ../$${softdir}/netconf_tui.py $(DESTDIR)$(sbindir)/system-config-network-tui; \
	#$(top_srcdir)/py-compile - $(DESTDIR)$(pkgdatadir)/*.py

uninstall-local:
	rm -fr $(DESTDIR)$(pkgdatadir)
	rm -f  $(DESTDIR)$(bindir)/system-control-network
	rm -f  $(DESTDIR)$(sbindir)/system-config-network-gui
	rm -f  $(DESTDIR)$(sbindir)/system-config-network-tui
	rm -f  $(DESTDIR)$(sbindir)/system-config-network-cmd
	rm -f $(DESTDIR)$(pkgdatadir)/*.py?

docs:
	cd $(srcdir)
	@PYTHON@ @pythondir@/../pydoc.py -w `find . -type d -o -name '*.py'|sed -e 's#^\./##g' -e 's#/#.#g' -e 's#\.py$$##g'` 
	mv *.html doc

pycheck:
	pychecker -F $(top_srcdir)/pycheckrc $(PYTHON_FILES)

