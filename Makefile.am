AUTOMAKE_OPTIONS = foreign 1.4

SUBDIRS=doc src po

EXTRA_DIST= redhat-config-network.spec doc/configurationfiles.txt doc/detailed_spec doc/overview

sysdir=$(sysconfdir)/X11/applnk/System
sys_DATA=neat.desktop

install-data-local:
	$(mkinstalldirs) $(sysconfdir)/security/console.apps
	$(INSTALL_DATA) neat.console $(sysconfdir)/security/console.apps/neat
	$(mkinstalldirs) $(sysconfdir)/pam.d
	$(INSTALL_DATA) neat.pam $(sysconfdir)/pam.d/neat
	$(mkinstalldirs) $(prefix)/bin/
	ln -fs consolehelper $(prefix)/bin/neat
	$(mkinstalldirs) $(datadir)/kontrol-panel/icons
	$(INSTALL_DATA) neat.desktop $(datadir)/kontrol-panel
	$(INSTALL_DATA) src/pixmaps/neat.png $(datadir)/kontrol-panel/icons
				
srpm: distcheck
	rpmbuild --define "_sourcedir `pwd`" --define "_srcrpmdir `pwd`" --define "_specdir `pwd`" -ts @PACKAGE@-@VERSION@.tar.gz
