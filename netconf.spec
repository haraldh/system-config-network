Summary: The network configuration tool for Red Hat Linux
Name: netconf
Version: 0.2
Release: 1
URL: http://www.redhat.com/ 
Source0: %{name}-%{version}.tar.gz
License: GPL
Group: Applications/System 
BuildArch: noarch
Requires: initscripts >= 5.99
BuildRoot: %{_tmppath}/%{name}-%{version}-root

%description
Netconf is the network configuration tool for Red Hat Linux, supporting
ethernet, ASDL, ISDN and PPP.
Different setups can be used as profiles which can be easily switched either
on the commandline or directly via the tool again.

%prep
%setup -q
aclocal
automake --add-missing
autoconf
%configure

%build

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/usr/share/netconf
/usr/sbin/*

%changelog
* Fri Jul 06 2001 Trond Eivind Glomsrød <teg@redhat.com>
- Require a recent version of initscripts

* Thu Jul 05 2001 Phil Knirsch <phil@redhat.de>
- Updated description.

* Fri Jun 29 2001 Trond Eivind Glomsrød <teg@redhat.com>
- Initial build. Don't obsolete older tools just yet...
