AUTOMAKE_OPTIONS = foreign 1.4

SUBDIRS=doc src po

EXTRA_DIST= redhat-config-network.spec doc/configurationfiles.txt doc/detailed_spec \
	doc/overview neat.desktop neat.console neat.pam

sysdir=$(sysconfdir)/X11/applnk/System

install-data-local:
	$(mkinstalldirs) $(sysconfdir)/security/console.apps
	$(INSTALL_DATA) neat.console $(sysconfdir)/security/console.apps/neat
	$(mkinstalldirs) $(sysconfdir)/pam.d
	$(INSTALL_DATA) neat.pam $(sysconfdir)/pam.d/neat
	$(mkinstalldirs) $(prefix)/bin/
	ln -fs consolehelper $(prefix)/bin/neat
	$(mkinstalldirs) $(datadir)/kontrol-panel/icons $(sysconfdir)/X11/serverconfig $(sysconfdir)/X11/applnk/System/
	$(INSTALL_DATA) neat.desktop $(datadir)/kontrol-panel
	$(INSTALL_DATA) neat.desktop $(sysconfdir)/X11/serverconfig
	$(INSTALL_DATA) neat.desktop $(sysconfdir)/X11/applnk/System/neat.desktop

srpm: distcheck
	rpmbuild --define "_sourcedir `pwd`" --define "_srcrpmdir `pwd`" --define "_specdir `pwd`" -ts @PACKAGE@-@VERSION@.tar.gz
