SUBDIRS=netconfpkg pixmaps 

PYTHON_FILES = netconf.py netconf-tui.py neat-control.py netconf-cmd.py version.py

EXTRA_DIST = $(PYTHON_FILES) providerdb module-info

CLEANFILES := version.pyc $(notdir $(wildcard netconf_cmd.py*)) $(notdir $(wildcard *~)) $(notdir $(wildcard *\#)) $(notdir $(wildcard \.\#*)) $(notdir $(wildcard *.pyc))

execdir = $(sbindir)


all-local: version.py 
	rm -f system-config-network-gui
	rm -f system-config-network-cmd
	rm -f system-config-network-tui
	rm -f  system-control-network
	rm -f netconf_cmd.py
	ln -s $(srcdir)/netconf.py system-config-network-gui
	ln -s $(srcdir)/netconf-cmd.py system-config-network-cmd
	ln -s $(srcdir)/netconf-cmd.py netconf_cmd.py
	ln -s $(srcdir)/netconf-tui.py system-config-network-tui
	ln -s $(srcdir)/neat-control.py system-control-network
	chmod 0755 system-config-network-gui system-config-network-cmd 
	chmod 0755 system-config-network-tui system-control-network


providerdir = $(pkgdatadir)
provider_DATA = providerdb

moduleinfodir = $(pkgdatadir)
moduleinfo_DATA = module-info

install-exec-local: 
	mkdir -p $(DESTDIR)$(pkgdatadir) $(DESTDIR)$(sbindir) $(DESTDIR)$(bindir)
	install -m 0644 $(srcdir)/version.py $(DESTDIR)$(pkgdatadir)/
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
	ln  -fs ../$${softdir}/neat-control.py $(DESTDIR)$(bindir)/system-control-network; \
	ln  -fs ../$${softdir}/netconf.py $(DESTDIR)$(sbindir)/system-config-network-gui; \
	ln  -fs ../$${softdir}/netconf-cmd.py $(DESTDIR)$(sbindir)/system-config-network-cmd; \
	ln  -fs ../$${softdir}/netconf.py $(DESTDIR)$(sbindir)/neat; \
	ln  -fs ../$${softdir}/netconf-tui.py $(DESTDIR)$(sbindir)/system-config-network-tui; \
	ln  -fs ../$${softdir}/netconf-tui.py $(DESTDIR)$(sbindir)/neat-tui; \
	$(top_srcdir)/py-compile - $(DESTDIR)$(pkgdatadir)/*.py

uninstall-local:
	rm -fr $(DESTDIR)$(pkgdatadir)
	rm -f  $(DESTDIR)$(bindir)/neat-control
	rm -f  $(DESTDIR)$(bindir)/system-control-network
	rm -f  $(DESTDIR)$(sbindir)/system-config-network-gui
	rm -f  $(DESTDIR)$(sbindir)/system-config-network-tui
	rm -f  $(DESTDIR)$(sbindir)/system-config-network-cmd
	rm -f  $(DESTDIR)$(sbindir)/neat
	rm -f  $(DESTDIR)$(sbindir)/neat-tui
	rm -f $(DESTDIR)$(pkgdatadir)/*.py?

docs:
	cd $(srcdir)
	@PYTHON@ @pythondir@/../pydoc.py -w `find . -type d -o -name '*.py'|sed -e 's#^\./##g' -e 's#/#.#g' -e 's#\.py$$##g'` 
	mv *.html doc

pycheck:
	pychecker -F $(top_srcdir)/pycheckrc $(PYTHON_FILES)

