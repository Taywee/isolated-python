# Do not make other RPMs that depend on this one

%define pybasever 3.5
%define pythonroot /opt/ea-python

%define _libdir64 %{pythonroot}/lib
%define _includedir %{pythonroot}/include
%define _bindir %{pythonroot}/bin
%define _mandir %{pythonroot}/share/man

Summary: An interpreted, interactive, object-oriented programming language.  Will be isolated to %{pythonroot}
Name: ea-python
Version: 3.5.3
Release: 2
License: Python
Group: Development/Languages
URL: https://github.com/Taywee/isolated-python
Source0: %{name}-%{pybasever}.tar.gz

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

# Needed to remove dependencies on /usr/local/bin/python
Autoreq: 0

#%ifos aix5.1 || %ifos aix5.2 || %ifos aix5.3
#Requires: AIX-rpm >= 5.1.0.0
#Requires: AIX-rpm < 5.4.0.0
#%endif
#
#%ifos aix6.1 || %ifos aix7.1
#Requires: AIX-rpm >= 6.1.0.0
#%endif

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
rm -rf Modules/expat Modules/zlib

%build
# setup environment for 64-bit build
export AR="ar -X64"
export NM="nm -X64"

# build 64-bit version
export OBJECT_MODE=64
export LDFLAGS="$LDFLAGS -L/usr/local/lib -pthread -Wl,-blibpath:%{_libdir64}:/usr/local/lib:/usr/lib:/lib"
autoconf
./configure \
    --prefix=%{pythonroot} \
    --libdir=%{_libdir64} \
    --mandir=%{_mandir} \
    --with-gcc="$CC -maix64 -I/usr/local/include -DAIX_GENUINE_CPLUSCPLUS -Wl,-brtl" \
    --with-cxx-main="$CXX -maix64 -I/usr/local/include -DAIX_GENUINE_CPLUSCPLUS -Wl,-brtl" \
%ifos aix5.1 || %ifos aix5.2 || %ifos aix5.3
    --disable-ipv6 \
%else
    --enable-ipv6 \
%endif
    --with-threads \
    --with-system-expat \
    OPT="-O2"

gmake %{?_smp_mflags}

%install
[ "%{buildroot}" != "/" ] && rm -rf "%{buildroot}"

export OBJECT_MODE=64
gmake DESTDIR=%{buildroot} install

/usr/bin/strip -X64 %{buildroot}%{_bindir}/* || :

export LD_LIBRARY_PATH=%{buildroot}%{_libdir64}

find %{buildroot}%{_libdir64} -name '*.py' | xargs %{buildroot}%{_bindir}/python3 -mpy_compile || :

cp libpython%{pybasever}m.a %{buildroot}%{_libdir64}/libpython%{pybasever}m.a
chmod 0644 %{buildroot}%{_libdir64}/libpython%{pybasever}m.a

ln -sf ../../libpython%{pybasever}m.a %{buildroot}%{_libdir64}/python%{pybasever}/config-%{pybasever}m/libpython%{pybasever}m.a
ln -sf ../../libpython%{pybasever}m.so %{buildroot}%{_libdir64}/python%{pybasever}/config-%{pybasever}m/libpython%{pybasever}m.so
cp -r Modules/* %{buildroot}%{_libdir64}/python%{pybasever}/config-%{pybasever}m/
ln -s config-%{pybasever}m %{buildroot}%{_libdir64}/python%{pybasever}/config

# Do not take blank lines or test files
find %{buildroot} -type d | grep -vE '%{buildroot}%{_libdir64}/python%{pybasever}/test' | sed "s|%{buildroot}|%dir |" | grep -vE '^%dir $' > allfiles
# Do not take files with whitespace
find %{buildroot} -type f -o -type l | grep -vE '%{buildroot}%{_libdir64}/python%{pybasever}/test' | sed "s|%{buildroot}||" | grep -vF ' ' >> allfiles

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files -f allfiles
%defattr(-,root,system)
%doc LICENSE README
%doc Misc/README.valgrind Misc/valgrind-python.supp
%doc Misc/gdbinit

%changelog
* Wed Jul 27 2016 Taylor C. Richberger <taywee@gmx.com> - 3.5.3-2
- Static linking

* Wed Jul 20 2016 Taylor C. Richberger <taywee@gmx.com> - 3.5.3-1
- Fix symlinks

* Thu May 19 2016 Taylor C. Richberger <taywee@gmx.com> - 3.5.1-2
- Trim out huge test files

* Wed May 18 2016 Taylor C. Richberger <taywee@gmx.com> - 3.5.1-1
- Should work.  Used auto-finding of files instead of more painful manual specification

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
