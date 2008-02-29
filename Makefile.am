AUTOMAKE_OPTIONS = foreign 1.4

SUBDIRS = doc src po m4

EXTRA_DIST= system-config-network.spec \
	system-config-network.desktop.in \
	system-config-network.console \
	system-config-network.pam \
	system-control-network.desktop.in \
	system-config-network-cmd.console \
	pycheckrc \
	intltool-extract.in intltool-merge.in intltool-update.in \
	ChangeLog \
	system-config-network.sh TODO \
	COPYING

iconsdir=$(pkgdatadir)

icons_DATA=system-config-network.desktop system-control-network.desktop

icons_in_files=$(icons_DATA:.desktop=.desktop.in)

CLEANFILES=$(icons_DATA) $(notdir $(wildcard *~)) $(notdir $(wildcard *\#)) $(notdir $(wildcard \.\#*))
DISTCLEANFILES=intltool-extract intltool-merge intltool-update translators.txt
MAINTAINERCLEANFILES=ChangeLog

@INTLTOOL_DESKTOP_RULE@

sysdir=$(sysconfdir)/X11/applnk/System

.PHONY: rp3 changelog srpm archive tag-srpm srpm force-tag-srpm

install-data-local:
	$(mkinstalldirs) $(DESTDIR)$(sysconfdir)/security/console.apps
	$(mkinstalldirs) $(DESTDIR)$(sysconfdir)/pam.d
	$(mkinstalldirs) $(DESTDIR)$(prefix)/bin/

	$(INSTALL_DATA) $(srcdir)/system-config-network.console $(DESTDIR)$(sysconfdir)/security/console.apps/system-config-network 
	$(INSTALL_DATA) $(srcdir)/system-config-network.pam $(DESTDIR)$(sysconfdir)/pam.d/system-config-network
	ln -fs consolehelper $(DESTDIR)$(prefix)/bin/system-config-network 

	install -m 0755 $(srcdir)/system-config-network.sh $(DESTDIR)$(sbindir)/system-config-network

#	# system-config-network-cmd needs a special console file
	$(INSTALL_DATA) $(srcdir)/system-config-network-cmd.console $(DESTDIR)$(sysconfdir)/security/console.apps/system-config-network-cmd
	$(INSTALL_DATA) $(srcdir)/system-config-network.pam $(DESTDIR)$(sysconfdir)/pam.d/system-config-network-cmd
	ln -fs consolehelper $(DESTDIR)$(prefix)/bin/system-config-network-cmd 

uninstall-local:
	rm -f  $(DESTDIR)$(sbindir)/system-control-network
	for i in system-config-network system-config-network-cmd; do \
		rm -f $(DESTDIR)$(sysconfdir)/security/console.apps/$$i; \
		rm -f $(DESTDIR)$(sysconfdir)/pam.d/$$i; \
		rm -f $(DESTDIR)$(prefix)/bin/$$i; \
	done

ChangeLog changelog:
	@git log --since="5 years ago" --no-merges -B HEAD > ChangeLog


clean-local:
	rm -f system-config-network.desktop
	rm -f system-control-network.desktop
	rm -f *~ *\#

distclean-local:
	rm -f $(top_builddir)/po/po2tbl.sed

VERSION=@VERSION@
SCMTAG=r$(subst .,-,$(VERSION))-$(subst .,-,$(RPM_RELEASE))

check-clean-tree:
	@git-diff --quiet --exit-code|| (echo "****** Local uncommited changes";exit 1) || exit 1
	@git-diff --cached --quiet --exit-code|| (echo "****** Local uncommited changes";exit 1) || exit 1

tag: check-clean-tree
	@if [ "$$(git-rev-parse HEAD 2>/dev/null)" != "$$(git-rev-parse $(SCMTAG) 2>/dev/null)" ] ; then \
		git tag $(SCMTAG); \
	fi

force-tag: check-clean-tree
	git tag -f $(SCMTAG)

archive: tag
	@test -d  /tmp/${PACKAGE}-$(VERSION) && chmod u+w -R /tmp/${PACKAGE}-$(VERSION) || :
	@rm -rf /tmp/${PACKAGE}-$(VERSION) /tmp/${PACKAGE}
	@git clone -l $$orig . /tmp/${PACKAGE}-$(VERSION)
	@cd /tmp/${PACKAGE}-$(VERSION);git checkout -b compile $(SCMTAG);./autogen.sh;make;make distcheck
	@mv /tmp/${PACKAGE}-$(VERSION)/${PACKAGE}-$(VERSION).tar.gz  $(top_builddir)
	@rm -rf /tmp/${PACKAGE}-$(VERSION)
	@echo "The archive is in ${PACKAGE}-$(VERSION).tar.gz"

srpm: archive
	@LANG=C rpmbuild --define "_sourcedir `pwd`" --define "_srcrpmdir $(top_builddir)" --define "_specdir `pwd`" -ts $(top_builddir)/@PACKAGE@-@VERSION@.tar.gz
	@$(MAKE) ${PACKAGE}.spec
	@echo " ${PACKAGE}-$(VERSION).tar.gz ${PACKAGE}.spec "

newversion:
	perl -p -i -e 'if (/RELEASE=(.*)/) { $$newrel = $$1 + 1;s/RELEASE=.*/RELEASE=$$newrel/; };' configure.in
	$(MAKE) srpm

potfile:
	chmod u+w -R  po
	sh -c '(find . -maxdepth 1 -type f -name "*.desktop.in";find ./src/netconfpkg/gui -type f -name "*.glade";find ./src -type f -name "*.py"|fgrep -v version.py|fgrep -v pygettext.py;echo src/version.py.in) |sed -e "s#^\./##g"|sort -u > po/POTFILES.in'
	sh -c '(find . -maxdepth 1 -type l -name "*.desktop.in";find ./src -type l -name "*.py";find ./src/netconfpkg/gui -type l -name "*.glade";echo src/version.py;echo pygettext.py;echo po/pygettext.py) |sed -e "s#^\./##g"|sort -u > po/POTFILES.skip'
	make 
	make -C po update-po

push: distcheck pull
	git push ssh://git.fedoraproject.org/git/hosted/system-config-network.git
	git fetch

pull:
	git fetch
	git rebase origin

diff:
	git diff origin
