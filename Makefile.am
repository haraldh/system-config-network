AUTOMAKE_OPTIONS = foreign 1.4

SUBDIRS=doc src po

EXTRA_DIST= redhat-config-network.spec neat.desktop neat.console neat.pam internet-druid.console internet-druid.desktop 

#neatconsoledir=$(sysconfdir)/security/console.apps/neat
#neatconsole_DATA=neat.console 

#interconsoledir=$(sysconfdir)/security/console.apps/neat
#tconsole_DATA=neat.console 

#pamdir=$(sysconfdir)/pam.d/neat
#pam_DATA=neat.pam 

icons1dir=$(datadir)/kontrol-panel
icons2dir=$(sysconfdir)/X11/sysconfig
icons3dir=$(sysconfdir)/X11/applnk/System
icons1_DATA=neat.desktop internet-druid.desktop
icons2_DATA=neat.desktop internet-druid.desktop
icons3_DATA=neat.desktop internet-druid.desktop

sysdir=$(sysconfdir)/X11/applnk/System

install-data-local:
	$(mkinstalldirs) $(DESTDIR)$(sysconfdir)/security/console.apps
	$(mkinstalldirs) $(DESTDIR)$(sysconfdir)/pam.d
	$(mkinstalldirs) $(DESTDIR)$(prefix)/bin/

	for i in neat redhat-config-network redhat-config-network-cmd; do \
		$(INSTALL_DATA) $(srcdir)/neat.console $(DESTDIR)$(sysconfdir)/security/console.apps/$$i; \
		$(INSTALL_DATA) $(srcdir)/neat.pam $(DESTDIR)$(sysconfdir)/pam.d/$$i; \
		ln -fs consolehelper $(DESTDIR)$(prefix)/bin/$$i; \
	done

	for i in internet-druid redhat-config-network-druid; do \
		$(INSTALL_DATA) $(srcdir)/internet-druid.console $(DESTDIR)$(sysconfdir)/security/console.apps/$$i; \
		$(INSTALL_DATA) $(srcdir)/neat.pam $(DESTDIR)$(sysconfdir)/pam.d/$$i; \
		ln -fs consolehelper $(DESTDIR)$(prefix)/bin/$$i; \
	done


dist: configure Makefile config.h

srpm: distcheck
	rpmbuild --define "_sourcedir `pwd`" --define "_srcrpmdir `pwd`" --define "_specdir `pwd`" -ts @PACKAGE@-@VERSION@.tar.gz


