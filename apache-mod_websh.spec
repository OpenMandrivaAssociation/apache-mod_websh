#Module-Specific definitions
%define mod_name mod_websh
%define mod_conf 24_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	Tcl scripting as a DSO module for the apache web server
Name:		apache-%{mod_name}
Version:	3.5.0
Release:	20
Group:		System/Servers
License:	Apache License
URL:		http://tcl.apache.org/websh/
Source0:	websh-%{version}.tar.bz2
Source1:	%{mod_conf}
Patch0:		%{mod_name}-register.patch
Patch1:		websh-tcl_version.diff
BuildRequires:	tcl >= 8.4.5
BuildRequires:	tcl-devel >= 8.4.5
BuildRequires:	autoconf2.5
BuildRequires:	automake
Requires:	tcl >= 8.4.5
Requires(pre): tcl >= 8.4.5
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	file

%description
Websh is a rapid development environment for building powerful,
fast, and reliable web applications. webshell is versatile and
handles everything from HTML generation to data-base driven
one-to-one page customization.

%prep

%setup -q -n websh-%{version}
%patch0 -p0
%patch1 -p0

cp %{SOURCE1} %{mod_conf}


# strip away annoying ^M
find . -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find . -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%build

cd src/unix
export WANT_AUTOCONF_2_5=1
rm -f missing
libtoolize --copy --force; aclocal; autoconf; automake --copy --foreign --add-missing --force-missing ||:

export INC="-I`%{_bindir}/apxs -q INCLUDEDIR` `apr-1-config --includes` `apu-1-config --includes`"

%configure2_5x --localstatedir=/var/lib \
    --enable-shared \
    --enable-threads \
    --with-httpdinclude=%{_includedir}/apache

perl -pi -e "s|^HTTPD_INCLUDES.*|HTTPD_INCLUDES = $INC|g" Makefile

cp configure.ac configure.in
make mod_websh.so

mkdir ../../.libs; mv mod_websh%{version}.so ../../.libs/mod_websh.so

%install

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

install -m0755 .libs/*.so %{buildroot}%{_libdir}/apache-extramodules/
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

install -d %{buildroot}%{_var}/www/html/addon-modules
ln -s ../../../..%{_docdir}/%{name}-%{version} %{buildroot}%{_var}/www/html/addon-modules/%{name}-%{version}

%post
/bin/systemctl daemon-reload >/dev/null 2>&1 || :

%postun
if [ "$1" = "0" ]; then
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi

%clean

%files
%doc INSTALL README src/ChangeLog src/license.terms doc/html/* doc/quickref.xml
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
%{_var}/www/html/addon-modules/*
