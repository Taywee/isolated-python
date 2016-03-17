# Do not make other RPMs that depend on this one

%define pybasever 3.5
%define pythonroot /opt/isolated-python

%define _libdir64 %{pythonroot}/lib
%define _includedir %{pythonroot}/include
%define _bindir %{pythonroot}/bin
%define _mandir %{pythonroot}/share/man

Summary: An interpreted, interactive, object-oriented programming language.  Will be isolated to %{pythonroot}
Name: isolated-python
Version: 3.5.1
Release: 0
License: Python
Group: Development/Languages
URL: https://github.com/Taywee/isolated-python
Source0: %{name}-%{pybasever}.tar.gz

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

BuildRequires: make

BuildRequires: bzip2 >= 1.0.2-4
BuildRequires: db4-devel >= 4.7.25-2
BuildRequires: expat-devel >= 2.1.0-1
BuildRequires: gettext >= 0.10.40-6
BuildRequires: gmp-devel >= 4.3.2-2
BuildRequires: gdbm-devel >= 1.8.3-1
BuildRequires: libffi-devel >= 3.0.13-1
BuildRequires: openssl-devel >= 1.0.1
BuildRequires: pkg-config
BuildRequires: readline-devel >= 5.2-3
BuildRequires: tcl-devel >= 8.5.8-2
BuildRequires: sqlite-devel >= 3.7.3-1
BuildRequires: zlib-devel >= 1.2.3-3

%ifos aix5.1 || %ifos aix5.2 || %ifos aix5.3
Requires: AIX-rpm >= 5.1.0.0
Requires: AIX-rpm < 5.4.0.0
%endif

%ifos aix6.1 || %ifos aix7.1
Requires: AIX-rpm >= 6.1.0.0
%endif

%description
Python is an interpreted, interactive, object-oriented programming
language often compared to Tcl, Perl, Scheme or Java. Python includes
modules, classes, exceptions, very high level dynamic data types and
dynamic typing. Python supports interfaces to many system calls and
libraries, as well as to various windowing systems (X11, Motif, Tk,
Mac and MFC).

Programmers can write new built-in modules for Python in C or C++.
Python can be used as an extension language for applications that need
a programmable interface. This package contains most of the standard
Python modules, as well as modules for interfacing to the Tix widget
set for Tk and RPM.

Note that documentation for Python is provided in the python-docs
package.


%prep
%setup -q -n %{name}
rm -rf Modules/expat Modules/zlib

%build
# setup environment for 64-bit build
export AR="ar -X32_64"
export NM="nm -X32_64"

# build 64-bit version
export OBJECT_MODE=64
export LDFLAGS="$LDFLAGS -L%{_prefix}/lib64 -pthread"
autoconf
./configure \
    --prefix=%{pythonroot} \
    --libdir=%{_libdir64} \
    --mandir=%{_mandir} \
    --with-gcc="$CC -maix64 -I/opt/freeware/include -DAIX_GENUINE_CPLUSCPLUS -Wl,-brtl" \
    --with-cxx-main="$CXX -maix64 -I/opt/freeware/include -DAIX_GENUINE_CPLUSCPLUS -Wl,-brtl" \
    --enable-shared \
%ifos aix5.1 || %ifos aix5.2 || %ifos aix5.3
    --disable-ipv6 \
%else
    --enable-ipv6 \
%endif
    --with-threads \
    --with-system-expat \
    --with-system-ffi \
    OPT="-O2"

gmake %{?_smp_mflags}

%install
[ "%{buildroot}" != "/" ] && rm -rf "%{buildroot}"

export OBJECT_MODE=64
gmake DESTDIR=%{buildroot} install

/usr/bin/strip -X32_64 %{buildroot}%{_bindir}/* || :

cp libpython%{pybasever}m.a %{buildroot}%{_libdir64}/libpython%{pybasever}m.a
chmod 0644 %{buildroot}%{_libdir64}/libpython%{pybasever}m.a

find %{buildroot}%{_libdir64}/python%{pybasever}/lib-dynload -type d | sed "s|%{buildroot}|%dir |" >> dynfiles
find %{buildroot}%{_libdir64}/python%{pybasever}/lib-dynload -type f | \
  grep -v "_ctypes_test.so$" | \
  grep -v "_testcapi.so$" | \
  sed "s|%{buildroot}||" >> dynfiles

ln -sf ../../libpython%{pybasever}m.a %{buildroot}%{_libdir64}/python%{pybasever}/config/libpython%{pybasever}m.a
ln -sf ../../libpython%{pybasever}m.so %{buildroot}%{_libdir64}/python%{pybasever}/config/libpython%{pybasever}m.so

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files -f dynfiles
%defattr(-,root,system)
%doc LICENSE README
%{_bindir}/pydoc*
%{_bindir}/python*
%{_mandir}/man?/*
%dir %{_libdir64}/python%{pybasever}
%{_libdir64}/python%{pybasever}/LICENSE.txt
%dir %{_libdir64}/python%{pybasever}/site-packages
%{_libdir64}/python%{pybasever}/site-packages/README
%{_libdir64}/python%{pybasever}/*.py*
%{_libdir64}/python%{pybasever}/*.doc
%dir %{_libdir64}/python%{pybasever}/bsddb
%{_libdir64}/python%{pybasever}/bsddb/*.py*
%{_libdir64}/python%{pybasever}/compiler
%dir %{_libdir64}/python%{pybasever}/ctypes
%{_libdir64}/python%{pybasever}/ctypes/*.py*
%{_libdir64}/python%{pybasever}/ctypes/macholib
%{_libdir64}/python%{pybasever}/curses
%dir %{_libdir64}/python%{pybasever}/distutils
%{_libdir64}/python%{pybasever}/distutils/*.py*
%{_libdir64}/python%{pybasever}/distutils/README
%{_libdir64}/python%{pybasever}/distutils/command
%dir %{_libdir64}/python%{pybasever}/email
%{_libdir64}/python%{pybasever}/email/*.py*
%{_libdir64}/python%{pybasever}/email/mime
%{_libdir64}/python%{pybasever}/encodings
%{_libdir64}/python%{pybasever}/hotshot
%{_libdir64}/python%{pybasever}/idlelib
%{_libdir64}/python%{pybasever}/importlib
%dir %{_libdir64}/python%{pybasever}/json
%{_libdir64}/python%{pybasever}/json/*.py*
%dir %{_libdir64}/python%{pybasever}/lib2to3
%{_libdir64}/python%{pybasever}/lib2to3/*.py*
%{_libdir64}/python%{pybasever}/lib2to3/Grammar*
%{_libdir64}/python%{pybasever}/lib2to3/Pattern*
%{_libdir64}/python%{pybasever}/lib2to3/fixes
%{_libdir64}/python%{pybasever}/lib2to3/pgen2
%{_libdir64}/python%{pybasever}/logging
%{_libdir64}/python%{pybasever}/multiprocessing
%{_libdir64}/python%{pybasever}/plat-aix?
%{_libdir64}/python%{pybasever}/pydoc_data
%dir %{_libdir64}/python%{pybasever}/sqlite3
%{_libdir64}/python%{pybasever}/sqlite3/*.py*
%dir %{_libdir64}/python%{pybasever}/unittest
%{_libdir64}/python%{pybasever}/unittest/*.py*
%{_libdir64}/python%{pybasever}/wsgiref*
%{_libdir64}/python%{pybasever}/xml
%{_bindir}/pydoc*
%{_bindir}/python*

# Libs
%{_libdir64}/libpython%{pybasever}m.a
%{_libdir64}/libpython%{pybasever}m.so

# Devel
%doc Misc/README.valgrind Misc/valgrind-python.supp
%doc Misc/gdbinit
%{_includedir}/*
%{_libdir64}/pkgconfig/*
%{_libdir64}/python%{pybasever}/config

# Tools
%defattr(-,root,system,-)
%{_bindir}/2to3*
%{_bindir}/idle*
%{_bindir}/smtpd*.py*

%changelog
* Tue Mar 15 2016 Taylor C. Richberger <taywee@gmx.com> - 3.5.1-0
- started development on the present version.  Will be bumped to release 1 when
  compiles and installs properly.

* Fri Aug 02 2013 Michael Perzl <michael@perzl.org> - 2.7.5-1
- updated to version 2.7.5

* Mon Jul 29 2013 Michael Perzl <michael@perzl.org> - 2.7.2-1
- updated to version 2.7.2

* Mon Jul 29 2013 Michael Perzl <michael@perzl.org> - 2.6.8-1
- updated to version 2.6.8

* Mon Jul 29 2013 Michael Perzl <michael@perzl.org> - 2.6.7-2
- fixed missing dependency of 'python-libs' to 'python'
- enable IPV6 on AIX version 6.1 and higher

* Sat Nov 19 2011 Michael Perzl <michael@perzl.org> - 2.6.7-1
- updated to version 2.6.7

* Wed Aug 26 2009 Michael Perzl <michael@perzl.org> - 2.6.2-1
- first version for AIX V5.1 and higher
