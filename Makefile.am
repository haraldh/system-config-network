AUTOMAKE_OPTIONS = foreign 1.4

SUBDIRS=doc src po

EXTRA_DIST= netconf.spec doc/configurationfiles.txt doc/detailed_spec doc/overview

srpm: distcheck
	rpmbuild --define "_sourcedir `pwd`" --define "_srcrpmdir `pwd`" --define "_specdir `pwd`" -ts @PACKAGE@-@VERSION@.tar.gz
