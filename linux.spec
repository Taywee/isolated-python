# Do not make other RPMs that depend on this one

%global pybasever 3.5
%global pyshortver 35
%global pyroot /opt/ea-python
%global pybindir %{pyroot}/bin
%global pysbindir %{pyroot}/sbin
%global libdir %{pyroot}/lib
%global pylibdir %{libdir}/python%{pybasever}
%global dynload_dir %{pylibdir}/lib-dynload
%global pydatadir %{pyroot}/share
%global pymandir %{pydatadir}/man
%global pyinfodir %{pydatadir}/info
%global pyincludedir %{pyroot}/include
%global pylibexecdir %{pyroot}/libexec
%global abiflags m
%global ldversion %{pybasever}%{abiflags}

# options
%global with_computed_gotos yes

# We want to byte-compile the .py files within the packages using the new
# python3 binary.
# 
# Unfortunately, rpmbuild's infrastructure requires us to jump through some
# hoops to avoid byte-compiling with the system python 2 version:
#   /usr/lib/rpm/redhat/macros sets up build policy that (amongst other things)
# defines __os_install_post.  In particular, "brp-python-bytecompile" is
# invoked without an argument thus using the wrong version of python
# (/usr/bin/python, rather than the freshly built python), thus leading to
# numerous syntax errors, and incorrect magic numbers in the .pyc files.  We
# thus override __os_install_post to avoid invoking this script:
%global __os_install_post /usr/lib/rpm/brp-compress \
  %{!?__debug_package:/usr/lib/rpm/brp-strip %{__strip}} \
  /usr/lib/rpm/brp-strip-static-archive %{__strip} \
  /usr/lib/rpm/brp-strip-comment-note %{__strip} %{__objdump}
# to remove the invocation of brp-python-bytecompile, whilst keeping the
# invocation of brp-python-hardlink (since this should still work for python3
# pyc/pyo files)

Summary: An interpreted, interactive, object-oriented programming language.  Will be isolated to %{pyroot}
Name: ea-python
Version: 3.5.3
Release: 0
License: Python
Group: Development/Languages
URL: https://github.com/Taywee/isolated-python
Source: https://github.com/Taywee/%{name}/archive/%{pybasever}.tar.gz

# Autoreq: 0
BuildRequires: autoconf
BuildRequires: bzip2
BuildRequires: bzip2-devel
BuildRequires: expat-devel
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

BuildRoot: %{_tmppath}/%{name}-%{version}-root

Requires: bzip2
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
%setup -q -n %{name}
sed --in-place \
    --expression="s|http://docs.python.org/library|http://docs.python.org/%{pybasever}/library|g" \
    Lib/pydoc.py || exit 1

%build
topdir=$(pwd)
export CFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC -fwrapv"
export CXXFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC -fwrapv"
export CPPFLAGS="`pkg-config --cflags-only-I libffi`"
export OPT="$RPM_OPT_FLAGS -D_GNU_SOURCE -fPIC -fwrapv"
export LINKCC="gcc"
export CFLAGS="$CFLAGS `pkg-config --cflags openssl`"
# No rpath changes yet
export LDFLAGS="$RPM_LD_FLAGS `pkg-config --libs-only-L openssl` -Wl,-rpath=%{libdir}"
#export LDFLAGS="$RPM_LD_FLAGS `pkg-config --libs-only-L openssl`"

ConfName=optimized
BinaryName=python
SymlinkName=python%{pybasever}
PathFixWithThisBinary=true

%configure \
  --bindir=%{pybindir} \
  --datadir=%{pydatadir} \
  --exec-prefix=%{pyroot} \
  --includedir=%{pyincludedir} \
  --infodir=%{pyinfodir} \
  --libdir=%{libdir} \
  --libexecdir=%{pylibexecdir} \
  --mandir=%{pymandir} \
  --prefix=%{pyroot} \
  --sbindir=%{pysbindir} \
  --enable-ipv6 \
  --enable-shared \
  --with-computed-gotos=%{with_computed_gotos} \
  --with-dbmliborder=gdbm:ndbm:bdb \
  --with-system-expat \
  --with-system-ffi \
  --without-ensurepip \
  --enable-loadable-sqlite-extensions

make EXTRA_CFLAGS="$CFLAGS" %{?_smp_mflags}

%install
topdir=$(pwd)
rm -fr %{buildroot}
mkdir -p %{buildroot}%{pyroot} %{buildroot}%{pyroot}/share/man

make install DESTDIR=%{buildroot} INSTALL="install -p"
install -d -m 0755 %{buildroot}%{pylibdir}/site-packages/__pycache__
install -m755 -d %{buildroot}%{pylibdir}/Tools
install Tools/README %{buildroot}%{pylibdir}/Tools/
cp -ar Tools/freeze %{buildroot}%{pylibdir}/Tools/
cp -ar Tools/i18n %{buildroot}%{pylibdir}/Tools/
cp -ar Tools/pynche %{buildroot}%{pylibdir}/Tools/
cp -ar Tools/scripts %{buildroot}%{pylibdir}/Tools/

install -m755 -d %{buildroot}%{pylibdir}/Doc
cp -ar Doc/tools %{buildroot}%{pylibdir}/Doc/
cp -ar Tools/demo %{buildroot}%{pylibdir}/Tools/
rm -f %{buildroot}%{pylibdir}/email/test/data/audiotest.au %{buildroot}%{pylibdir}/test/audiotest.au

# Switch all shebangs to refer to the specific Python version.
LD_LIBRARY_PATH=%{buildroot}%{libdir} %{buildroot}%{pybindir}/python%{pybasever} \
  Tools/scripts/pathfix.py \
  -i "%{pybindir}/python%{pybasever}" \
  %{buildroot}

# Remove shebang lines from .py files that aren't executable, and
# remove executability from .py files that don't have a shebang line:
find %{buildroot} -name \*.py \
  \( \( \! -perm /u+x,g+x,o+x -exec sed -e '/^#!/Q 0' -e 'Q 1' {} \; \
  -print -exec sed -i '1d' {} \; \) -o \( \
  -perm /u+x,g+x,o+x ! -exec grep -m 1 -q '^#!' {} \; \
  -exec chmod a-x {} \; \) \)

# .xpm and .xbm files should not be executable:
find %{buildroot} \
  \( -name \*.xbm -o -name \*.xpm -o -name \*.xpm.1 \) \
  -exec chmod a-x {} \;

# Remove executable flag from files that shouldn't have it:
chmod a-x \
  %{buildroot}%{pylibdir}/distutils/tests/Setup.sample \
  %{buildroot}%{pylibdir}/Tools/README

# Get rid of DOS batch files:
find %{buildroot} -name \*.bat -exec rm {} \;

# Get rid of backup files:
find %{buildroot}/ -name "*~" -exec rm -f {} \;
find . -name "*~" -exec rm -f {} \;
rm -f %{buildroot}%{pylibdir}/LICENSE.txt
# Junk, no point in putting in -test sub-pkg
rm -f %{buildroot}/%{pylibdir}/idlelib/testcode.py*

# Fix end-of-line encodings:
find %{buildroot}/ -name \*.py -exec sed -i 's/\r//' {} \;

# Fixup permissions for shared libraries from non-standard 555 to standard 755:
find %{buildroot} \
    -perm 555 -exec chmod 755 {} \;

# Do bytecompilation with the newly installed interpreter.
# This is similar to the script in macros.pybytecompile
# compile *.pyo
find %{buildroot} -type f -a -name "*.py" -print0 | \
    LD_LIBRARY_PATH="%{buildroot}%{dynload_dir}/:%{buildroot}%{libdir}" \
    PYTHONPATH="%{buildroot}%{pylibdir} %{buildroot}%{pylibdir}/site-packages" \
    xargs -0 %{buildroot}%{pybindir}/python%{pybasever} -O -c 'import py_compile, sys; [py_compile.compile(f, dfile=f.partition("%{buildroot}")[2]) for f in sys.argv[1:]]' || :
# compile *.pyc
find %{buildroot} -type f -a -name "*.py" -print0 | \
    LD_LIBRARY_PATH="%{buildroot}%{dynload_dir}/:%{buildroot}%{libdir}" \
    PYTHONPATH="%{buildroot}%{pylibdir} %{buildroot}%{pylibdir}/site-packages" \
    xargs -0 %{buildroot}%{pybindir}/python%{pybasever} -O -c 'import py_compile, sys; [py_compile.compile(f, dfile=f.partition("%{buildroot}")[2], optimize=0) for f in sys.argv[1:]]' || :

# Remove all references to the buildroot, just for good measure
find %{buildroot} -type f -exec sed -i 's|%{buildroot}||' {} \;

# Delete test files
rm -rf '%{buildroot}%{libdir}/python%{pybasever}/test'
find '%{buildroot}' -name '* *' -delete

find %{buildroot} -type d |  sed "s|%{buildroot}|%dir |" | grep -vE '^%dir $' > allfiles
find %{buildroot} -type f -o -type l | sed "s|%{buildroot}||" | grep -vE '^$' >> allfiles

%clean
rm -rf %{buildroot}

%files -f allfiles
%defattr(-,root,root)
%doc LICENSE README
%doc Misc/README.valgrind Misc/valgrind-python.supp
%doc Misc/gdbinit

%changelog
* Tue May 24 2016 Taylor C. Richberger <taywee@gmx.com> - 3.5.1-1
- Simplify file list

* Wed Mar 23 2016 Taylor C. Richberger <taywee@gmx.com> - 3.5.1-0
- started development on the present version.  Will be bumped to release 1 when
  compiles and installs properly.
