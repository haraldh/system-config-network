AUTOMAKE_OPTIONS = foreign 1.4

SUBDIRS = doc src po

EXTRA_DIST= redhat-config-network.spec neat.desktop.in neat.console neat.pam \
	internet-druid.console internet-druid.desktop.in \
	neat-control.desktop.in pycheckrc \
	intltool-extract.in intltool-merge.in intltool-update.in

icons1dir=$(datadir)/kontrol-panel
icons2dir=$(sysconfdir)/X11/sysconfig
icons3dir=$(sysconfdir)/X11/applnk/System

icons1_DATA=neat.desktop internet-druid.desktop neat-control.desktop
icons2_DATA=neat.desktop internet-druid.desktop neat-control.desktop
icons3_DATA=neat.desktop internet-druid.desktop neat-control.desktop

icons1_in_files=$(icons1_DATA:.desktop=.desktop.in)
icons2_in_files=$(icons2_DATA:.desktop=.desktop.in)
icons3_in_files=$(icons3_DATA:.desktop=.desktop.in)

@INTLTOOL_DESKTOP_RULE@

sysdir=$(sysconfdir)/X11/applnk/System

.PHONY: rp3 changelog srpm

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

uninstall-local:
	for i in neat redhat-config-network redhat-config-network-cmd; do \
		rm -f $(DESTDIR)$(sysconfdir)/security/console.apps/$$i; \
		rm -f $(DESTDIR)$(sysconfdir)/pam.d/$$i; \
		rm -f $(DESTDIR)$(prefix)/bin/$$i; \
	done

	for i in internet-druid redhat-config-network-druid; do \
		rm -f $(DESTDIR)$(sysconfdir)/security/console.apps/$$i; \
		rm -f $(DESTDIR)$(sysconfdir)/pam.d/$$i; \
		rm -f $(DESTDIR)$(prefix)/bin/$$i; \
	done

changelog:
	rcs2log | sed -e 's|/usr/local/CVS/redhat-config-network/||g' \
		-e 's|@.*\.redhat\.com|@redhat.com|g' > ChangeLog

dist: configure Makefile config.h changelog

srpm: distcheck rp3-1.1.10.tar.gz
	rpmbuild --define "_sourcedir `pwd`" --define "_srcrpmdir `pwd`" --define "_specdir `pwd`" -ts @PACKAGE@-@VERSION@.tar.gz


rp3-1.1.10.tar.gz: 
	ncftpget ftp://porkchop.redhat.com/mnt/redhat/beehive/comps/dist/7.2/rp3/1.1.10-3/SRPMS/rp3-1.1.10-3.src.rpm
	(rpm2cpio rp3-1.1.10-3.src.rpm |cpio -i rp3-1.1.10.tar.gz) && rm -f rp3-1.1.10-3.src.rpm
