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

# Needed to remove dependencies on /usr/local/bin/python
Autoreq: 0
BuildRequires: autoconf
BuildRequires: bzip2
BuildRequires: bzip2-devel
BuildRequires: db4-devel >= 4.7
BuildRequires: expat-devel >= 2.1.0
BuildRequires: findutils
BuildRequires: gcc-c++
BuildRequires: gdbm-devel
BuildRequires: glibc-devel
BuildRequires: gmp-devel
BuildRequires: libffi-devel
BuildRequires: ncurses-devel
BuildRequires: net-tools
BuildRequires: openssl-devel
BuildRequires: pkgconfig
BuildRequires: readline-devel
BuildRequires: sqlite-devel
BuildRequires: tar
BuildRequires: xz-devel
BuildRequires: zlib-devel

Requires: bzip2
Requires: db4
Requires: expat
Requires: gdbm
Requires: glibc
Requires: gmp
Requires: libffi
Requires: ncurses
Requires: net-tools
Requires: openssl
Requires: readline
Requires: sqlite
Requires: tar
Requires: xz
Requires: zlib

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
%setup -q -n %{name}-%{pybasever}

%build
export CFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC -fwrapv"
export CXXFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC -fwrapv"
export CPPFLAGS="`pkg-config --cflags-only-I libffi`"
export OPT="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC -fwrapv"
export LINKCC="gcc"
export CFLAGS="$CFLAGS `pkg-config --cflags openssl`"
export LDFLAGS="$RPM_LD_FLAGS `pkg-config --libs-only-L openssl` -Wl,-rpath=%{_libdir64}"

autoconf
%configure \
    --prefix=%{pythonroot} \
    --libdir=%{_libdir64} \
    --mandir=%{_mandir} \
    --with-dbmliborder=gdbm:ndbm:bdb \
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

gmake DESTDIR=%{buildroot} install

/usr/bin/strip %{buildroot}%{_bindir}/* || :

cp libpython%{pybasever}m.a %{buildroot}%{_libdir64}/libpython%{pybasever}m.a
chmod 0644 %{buildroot}%{_libdir64}/libpython%{pybasever}m.a

ln -sf ../../libpython%{pybasever}m.a %{buildroot}%{_libdir64}/python%{pybasever}/config-%{pybasever}m/libpython%{pybasever}m.a
ln -sf ../../libpython%{pybasever}m.so %{buildroot}%{_libdir64}/python%{pybasever}/config-%{pybasever}m/libpython%{pybasever}m.so
cp -r Modules/* %{buildroot}%{_libdir64}/python%{pybasever}/config-%{pybasever}m/

ls -1 %{buildroot}%{_libdir64}/*.a | sed 's|%{buildroot}||' >> libfiles
ls -1 %{buildroot}%{_libdir64}/*.so | sed 's|%{buildroot}||' >> libfiles
find %{buildroot}%{_libdir64}/python%{pybasever} -type d | sed "s|%{buildroot}|%dir |" >> libfiles
find %{buildroot}%{_libdir64}/python%{pybasever} -type f | \
  grep -v '_ctypes_test.so$' | \
  grep -v '_testcapi.so$' | \
  grep -v 'launcher manifest.xml$' | \
  grep -v '\(dev\)' | \
  sed 's|%{buildroot}||' >> libfiles

ln -s config-%{pybasever}m %{buildroot}%{_libdir64}/python%{pybasever}/config

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files -f libfiles
%defattr(-,root,system)
%doc LICENSE README
%{_bindir}/*
%{_mandir}/man?/*

# Devel
%doc Misc/README.valgrind Misc/valgrind-python.supp
%doc Misc/gdbinit
%{_includedir}/*
%{_libdir64}/pkgconfig/*
%{_libdir64}/python%{pybasever}/config

# Tools
%defattr(-,root,system,-)

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
