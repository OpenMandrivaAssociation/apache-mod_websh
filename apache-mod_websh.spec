#Module-Specific definitions
%define mod_name mod_websh
%define mod_conf 24_%{mod_name}.conf
%define mod_so %{mod_name}.so

Summary:	Tcl scripting as a DSO module for the apache web server
Name:		apache-%{mod_name}
Version:	3.5.0
Release:	19
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
    --enable-static \
    --enable-threads \
    --with-httpdinclude=%{_includedir}/apache

perl -pi -e "s|^HTTPD_INCLUDES.*|HTTPD_INCLUDES = $INC|g" Makefile

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
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean

%files
%doc INSTALL README src/ChangeLog src/license.terms doc/html/* doc/quickref.xml
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
%{_var}/www/html/addon-modules/*




%changelog
* Sat Feb 11 2012 Oden Eriksson <oeriksson@mandriva.com> 3.5.0-19mdv2012.0
+ Revision: 773235
- rebuild

* Tue May 24 2011 Oden Eriksson <oeriksson@mandriva.com> 3.5.0-18
+ Revision: 678441
- mass rebuild

* Mon Jan 03 2011 Oden Eriksson <oeriksson@mandriva.com> 3.5.0-17mdv2011.0
+ Revision: 627740
- don't force the usage of automake1.7

* Sun Oct 24 2010 Oden Eriksson <oeriksson@mandriva.com> 3.5.0-16mdv2011.0
+ Revision: 588087
- rebuild

* Mon Mar 08 2010 Oden Eriksson <oeriksson@mandriva.com> 3.5.0-15mdv2010.1
+ Revision: 516254
- rebuilt for apache-2.2.15

* Sat Aug 01 2009 Oden Eriksson <oeriksson@mandriva.com> 3.5.0-14mdv2010.0
+ Revision: 407084
- fix build
- rebuild

* Wed Jan 07 2009 Oden Eriksson <oeriksson@mandriva.com> 3.5.0-13mdv2009.1
+ Revision: 326510
- rebuild

* Fri Dec 05 2008 Adam Williamson <awilliamson@mandriva.org> 3.5.0-12mdv2009.1
+ Revision: 310156
- update tcl_version.diff for new tcl
- rebuild for new tcl

* Mon Jul 14 2008 Oden Eriksson <oeriksson@mandriva.com> 3.5.0-11mdv2009.0
+ Revision: 235129
- rebuild

* Thu Jun 05 2008 Oden Eriksson <oeriksson@mandriva.com> 3.5.0-10mdv2009.0
+ Revision: 215672
- fix rebuild
- hard code %%{_localstatedir}/lib to ease backports

* Thu Dec 20 2007 Olivier Blin <blino@mandriva.org> 3.5.0-9mdv2008.1
+ Revision: 135823
- restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Sat Sep 08 2007 Oden Eriksson <oeriksson@mandriva.com> 3.5.0-9mdv2008.0
+ Revision: 82702
- rebuild

* Fri Sep 07 2007 Anssi Hannula <anssi@mandriva.org> 3.5.0-8mdv2008.0
+ Revision: 81992
- rebuild for new soname of tcl

* Fri Aug 10 2007 Oden Eriksson <oeriksson@mandriva.com> 3.5.0-7mdv2008.0
+ Revision: 61273
- make it find the latest tcl


* Sat Mar 10 2007 Oden Eriksson <oeriksson@mandriva.com> 3.5.0-7mdv2007.1
+ Revision: 140777
- rebuild

* Sun Nov 12 2006 Oden Eriksson <oeriksson@mandriva.com> 3.5.0-6mdv2007.1
+ Revision: 83316
- rebuild
- remove macro to make iurt able to build the package
- bunzip patches and sources

  + Stefan van der Eijk <stefan@mandriva.org>
    - Import apache-mod_websh

* Mon Aug 07 2006 Oden Eriksson <oeriksson@mandriva.com> 3.5.0-4mdv2007.0
- rebuild

* Sun Jan 01 2006 Oden Eriksson <oeriksson@mandriva.com> 3.5.0-3mdk
- really rebuilt against apache-2.2.0
- rebuilt against soname aware deps (tcl/tk)
- fix deps

* Thu Dec 15 2005 Oden Eriksson <oeriksson@mandriva.com> 3.5.0-2mdk
- rebuilt against apache-2.2.0

* Mon Nov 28 2005 Oden Eriksson <oeriksson@mandriva.com> 3.5.0-1mdk
- fix versioning

* Sun Jul 31 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.54_3.5.0-2mdk
- fix deps

* Fri Jun 03 2005 Oden Eriksson <oeriksson@mandriva.com> 2.0.54_3.5.0-1mdk
- rename the package
- the conf.d directory is renamed to modules.d
- use new rpm-4.4.x pre,post magic

* Sun Mar 20 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.53_3.5.0-4mdk
- use the %1

* Mon Feb 28 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.53_3.5.0-3mdk
- fix %%post and %%postun to prevent double restarts
- fix bug #6574

* Wed Feb 16 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.53_3.5.0-2mdk
- spec file cleanups, remove the ADVX-build stuff

* Tue Feb 08 2005 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.53_3.5.0-1mdk
- rebuilt for apache 2.0.53

* Wed Sep 29 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.52_3.5.0-1mdk
- built for apache 2.0.52

* Fri Sep 17 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.51_3.5.0-1mdk
- built for apache 2.0.51

* Tue Jul 13 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 2.0.50_3.5.0-1mdk
- built for apache 2.0.50
- remove redundant provides

* Tue Jun 15 2004 Oden Eriksson <oden.eriksson@kvikkjokk.net> 2.0.49_3.5.0-1mdk
- built for apache 2.0.49

