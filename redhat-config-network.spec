Summary: The NEtwork Adminstration Tool for Red Hat Linux
Name: redhat-config-network
Version: 0.3.0
Release: 2
URL: http://www.redhat.com/ 
Source0: %{name}-%{version}.tar.gz
License: GPL
Group: Applications/System 
BuildArch: noarch
Requires: initscripts >= 5.99
BuildRoot: %{_tmppath}/%{name}-%{version}-root

%description
Netconf is the network configuration tool for Red Hat Linux, supporting
ethernet, ASDL, ISDN and PPP. It can also configure firewalls and
masquerading, and can use profiles.


%prep
%setup -q
%configure

%build

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/usr/share/redhat-config-network
/usr/sbin/*

%changelog
* Thu Jul 11 2001 Phil Knirsch <phil@redhat.de> 0.3.0-2
- Fixed critical problem during profile saving.

* Thu Jul 10 2001 Phil Knirsch <phil@redhat.de> 0.3.0-1
- 0.3.0-1
- Final touches for beta2. Most stuff should work now.

* Thu Jul 10 2001 Phil Knirsch <phil@redhat.de> 0.2.2-2
- Added some missing files.

* Tue Jul 10 2001 Trond Eivind Glomsrød <teg@redhat.com>
- 0.2.2

* Tue Jul 10 2001 Trond Eivind Glomsrød <teg@redhat.com>
- 0.2.1

* Mon Jul  9 2001 Trond Eivind Glomsrød <teg@redhat.com>
- 0.2
- New name - redhat-config-network. 
  Shortcut: neat (NEtwork Administration Tool)

* Fri Jul 06 2001 Trond Eivind Glomsrød <teg@redhat.com>
- Require a recent version of initscripts
- Initial build. Don't obsolete older tools just yet...
