Summary: The network configuration tool for Red Hat Linux
Name: netconf
Version: 0.1
Release: 1
URL: http://www.redhat.com/ 
Source0: %{name}-%{version}.tar.gz
License: GPL
Group: Applications/System 
BuildRoot: %{_tmppath}/%{name}-%{version}-root

%description
Netconf is the network configuration tool for Red Hat Linux, supporting
ethernet, ASDL, ISDN and PPP. It can also configure firewalls and
masquerading, and can use profiles.


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
* Fri Jun 29 2001 Trond Eivind Glomsrød <teg@redhat.com>
- Initial build. Don't obsolete older tools just yet...



