AUTOMAKE_OPTIONS = foreign 1.4

SUBDIRS=doc src intl po

EXTRA_DIST= redhat-config-network.spec neat.desktop neat.console neat.pam internet-druid.console internet-druid.desktop 

#neatconsoledir=$(sysconfdir)/security/console.apps/neat
#neatconsole_DATA=neat.console 

#interconsoledir=$(sysconfdir)/security/console.apps/neat
#tconsole_DATA=neat.console 

#pamdir=$(sysconfdir)/pam.d/neat
#pam_DATA=neat.pam 

icons1dir=$(datadir)/kontrol-panel
icons2dir=$(sysconfdir)/X11/serverconfig
icons3dir=$(sysconfdir)/X11/applnk/System
icons1_DATA=neat.desktop internet-druid.desktop
icons2_DATA=neat.desktop internet-druid.desktop
icons3_DATA=neat.desktop internet-druid.desktop

sysdir=$(sysconfdir)/X11/applnk/System

install-data-local:
	$(mkinstalldirs) $(DESTDIR)$(sysconfdir)/security/console.apps
	$(INSTALL_DATA) $(srcdir)/neat.console $(DESTDIR)$(sysconfdir)/security/console.apps/neat
	$(INSTALL_DATA) $(srcdir)/internet-druid.console $(DESTDIR)$(sysconfdir)/security/console.apps/internet-druid
	$(mkinstalldirs) $(DESTDIR)$(sysconfdir)/pam.d
	$(INSTALL_DATA) $(srcdir)/neat.pam $(DESTDIR)$(sysconfdir)/pam.d/neat
	$(INSTALL_DATA) $(srcdir)/neat.pam $(DESTDIR)$(sysconfdir)/pam.d/internet-druid
	$(mkinstalldirs) $(DESTDIR)$(prefix)/bin/
	ln -fs consolehelper $(DESTDIR)$(prefix)/bin/neat
	ln -fs consolehelper $(DESTDIR)$(prefix)/bin/internet-druid

srpm: distcheck
	rpmbuild --define "_sourcedir `pwd`" --define "_srcrpmdir `pwd`" --define "_specdir `pwd`" -ts @PACKAGE@-@VERSION@.tar.gz
