AUTOMAKE_OPTIONS = foreign 1.4

SUBDIRS = doc src po

EXTRA_DIST= system-config-network.spec neat.desktop.in neat.console neat.pam \
	internet-druid.console internet-druid.desktop.in \
	neat-control.desktop.in pycheckrc \
	intltool-extract.in intltool-merge.in intltool-update.in \
	ChangeLog system-config-network-cmd.console \
	system-config-network.sh TODO

iconsdir=$(pkgdatadir)

icons_DATA=neat.desktop internet-druid.desktop neat-control.desktop

icons_in_files=$(icons_DATA:.desktop=.desktop.in)

CLEANFILES=$(icons_DATA) $(notdir $(wildcard *~)) $(notdir $(wildcard *\#)) $(notdir $(wildcard \.\#*))
DISTCLEANFILES=intltool-extract intltool-merge intltool-update
MAINTAINERCLEANFILES=ChangeLog

@INTLTOOL_DESKTOP_RULE@

sysdir=$(sysconfdir)/X11/applnk/System

.PHONY: rp3 changelog srpm archive tag-srpm srpm force-tag-srpm

install-data-local:
	$(mkinstalldirs) $(DESTDIR)$(sysconfdir)/security/console.apps
	$(mkinstalldirs) $(DESTDIR)$(sysconfdir)/pam.d
	$(mkinstalldirs) $(DESTDIR)$(prefix)/bin/

	for i in neat system-config-network ; do \
		$(INSTALL_DATA) $(srcdir)/neat.console $(DESTDIR)$(sysconfdir)/security/console.apps/$$i; \
		$(INSTALL_DATA) $(srcdir)/neat.pam $(DESTDIR)$(sysconfdir)/pam.d/$$i; \
		ln -fs consolehelper $(DESTDIR)$(prefix)/bin/$$i; \
	done

	install -m 0755 $(srcdir)/system-config-network.sh $(DESTDIR)$(sbindir)/system-config-network

# system-config-network-cmd needs a special console file

	$(INSTALL_DATA) $(srcdir)/system-config-network-cmd.console $(DESTDIR)$(sysconfdir)/security/console.apps/system-config-network-cmd; \
	$(INSTALL_DATA) $(srcdir)/neat.pam $(DESTDIR)$(sysconfdir)/pam.d/system-config-network-cmd; \
	ln -fs consolehelper $(DESTDIR)$(prefix)/bin/system-config-network-cmd ; 


	for i in internet-druid system-config-network-druid; do \
		$(INSTALL_DATA) $(srcdir)/internet-druid.console $(DESTDIR)$(sysconfdir)/security/console.apps/$$i; \
		$(INSTALL_DATA) $(srcdir)/neat.pam $(DESTDIR)$(sysconfdir)/pam.d/$$i; \
		ln -fs consolehelper $(DESTDIR)$(prefix)/bin/$$i; \
	done

uninstall-local:
	rm -f  $(DESTDIR)$(sbindir)/system-control-network
	for i in neat system-config-network system-config-network-cmd; do \
		rm -f $(DESTDIR)$(sysconfdir)/security/console.apps/$$i; \
		rm -f $(DESTDIR)$(sysconfdir)/pam.d/$$i; \
		rm -f $(DESTDIR)$(prefix)/bin/$$i; \
	done

	for i in internet-druid system-config-network-druid; do \
		rm -f $(DESTDIR)$(sysconfdir)/security/console.apps/$$i; \
		rm -f $(DESTDIR)$(sysconfdir)/pam.d/$$i; \
		rm -f $(DESTDIR)$(prefix)/bin/$$i; \
	done

changelog:
	rcs2log -v | sed -e 's|/usr/local/CVS/redhat-config-network/||g' \
		-e 's|@.*\.redhat\.com|@redhat.com|g' > ChangeLog

clean-local:
	rm -f neat.desktop
	rm -f neat-control.desktop
	rm -f *~ *\#

distclean-local:
	rm -f $(top_builddir)/po/po2tbl.sed

PKGNAME=$(subst system-config,redhat-config,$(PACKAGE))
VERSION=@VERSION@
CVSTAG=r$(subst .,-,$(VERSION))-$(subst .,-,$(RPM_RELEASE))

archive: changelog
	@rm -rf /tmp/${PKGNAME}-$(VERSION) /tmp/${PKGNAME}
	@CVSROOT=`cat CVS/Root`;cd /tmp; cvs -d $$CVSROOT export -r$(CVSTAG) ${PKGNAME}
	@cd /tmp/${PKGNAME};./autogen.sh;make distcheck
	@mv /tmp/${PKGNAME}/${PACKAGE}-$(VERSION).tar.gz  $(top_builddir)./
	@rm -rf /tmp/${PKGNAME}
	@echo "The archive is in ${PACKAGE}-$(VERSION).tar.gz"

force-tag:
	cvs ci -m "release $(VERSION)-$(RPM_RELEASE) moved"
	cvs tag -cR -F $(CVSTAG) .

tag:
	cvs ci -m "release $(VERSION)-$(RPM_RELEASE)"
	cvs tag -cR $(CVSTAG) .

tag-srpm: changelog tag archive
	LANG=C rpmbuild --define "_sourcedir `pwd`" --define "_srcrpmdir $(top_builddir)" --define "_specdir `pwd`" -ts $(top_builddir)/@PACKAGE@-@VERSION@.tar.gz

force-tag-srpm: force-tag archive
	LANG=C rpmbuild --define "_sourcedir `pwd`" --define "_srcrpmdir $(top_builddir)" --define "_specdir `pwd`" -ts $(top_builddir)/@PACKAGE@-@VERSION@.tar.gz

srpm: distcheck changelog
	LANG=C rpmbuild --define "_sourcedir `pwd`" --define "_srcrpmdir $(top_builddir)" --define "_specdir `pwd`" -ts $(top_builddir)/@PACKAGE@-@VERSION@.tar.gz

newversion:
	perl -p -i -e 'if (/RELEASE=(.*)/) { $$newrel = $$1 + 1;s/RELEASE=.*/RELEASE=$$newrel/; };' configure.in
	$(MAKE) srpm

potfile:
	sh -c '(find . -name "*.desktop.in";find ./src -name "*.py";find ./src/netconfpkg/gui -name "*.glade") > po/POTFILES.in'
