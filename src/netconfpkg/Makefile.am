SUBDIRS=gui

GENCLASS_FILES = DeviceList.py ProfileList.py HardwareList.py \
                ProviderList.py NetworkList.py	Firewall.py 

IDL_FILES = \
	DeviceList.idl \
	Firewall.idl \
	HardwareList.idl \
	NetworkList.idl \
	ProfileList.idl \
	ProviderList.idl

PYTHON_FILES = \
	__init__.py \
	Conf.py \
	ConfPAP.py \
	ConfSMB.py \
	genClass.py \
	NCCallback.py \
	NCCipe.py \
	NCCompression.py \
	NCDeviceList.py \
	NCDevice.py \
	NCDialup.py \
	NC_functions.py \
	NCHardwareList.py \
	NCisdnhardware.py \
	NCProfileList.py \
	NCWireless.py \
	PasswordCrypt.py 

BUILT_SOURCES = $(patsubst %.py,%.pyc,$(GENCLASS_FILES) $(PYTHON_FILES)) $(GENCLASS_FILES)

EXTRA_DIST = $(IDL_FILES) $(PYTHON_FILES)

netconfpkgdir = $(pkgdatadir)/netconfpkg
netconfpkg_DATA = $(PYTHON_FILES) $(BUILT_SOURCES)

execdir = $(sbindir)

clean:
	rm -f *.pyo *.pyc
	rm -f ${BUILT_SOURCES}

DeviceList.py: $(srcdir)/DeviceList.idl $(srcdir)/genClass.py $(srcdir)/NCDeviceList.py $(srcdir)/NCDevice.py $(srcdir)/NCDialup.py $(srcdir)/NCCallback.py

HardwareList.py: $(srcdir)/HardwareList.idl $(srcdir)/genClass.py $(srcdir)/NCHardwareList.py 

ProfileList.py: $(srcdir)/ProfileList.idl $(srcdir)/genClass.py $(srcdir)/NCProfileList.py 

%.py: %.idl $(srcdir)/genClass.py
	python $(srcdir)/genClass.py -f -c $(srcdir)/$*.idl $@ NC

%.pyc: %.py
	@echo "Compiling because of " $*
	python /usr/lib/python1.5/compileall.pyc -l -d . $(srcdir)
