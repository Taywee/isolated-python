# Do not make other RPMs that depend on this one

%global pybasever 3.5
%global pyshortver 35
%global pyroot /opt/isolated-python
%global pybindir %{pyroot}/bin
%global libdir %{pyroot}/lib
%global pylibdir %{libdir}/python%{pybasever}
%global dynload_dir %{pylibdir}/lib-dynload
%global pymandir %{pyroot}/share/man
%global abiflags m
%global ldversion %{pybasever}%{abiflags}

# options
%global with_computed_gotos yes

Summary: An interpreted, interactive, object-oriented programming language.  Will be isolated to %{pyroot}
Name: isolated-python
Version: 3.5.1
Release: 0
License: Python
Group: Development/Languages
URL: https://github.com/Taywee/isolated-python
Source: https://github.com/Taywee/%{name}/archive/%{pybasever}.tar.gz

# Autoreq: 0
BuildRequires: autoconf
BuildRequires: bzip2
BuildRequires: bzip2-devel
BuildRequires: libdb-devel
BuildRequires: expat-devel >= 2.1.0
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

Requires: expat >= 2.1.0

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
#export LDFLAGS="$RPM_LD_FLAGS `pkg-config --libs-only-L openssl` -Wl,-rpath=%{_libdir64}"
export LDFLAGS="$RPM_LD_FLAGS `pkg-config --libs-only-L openssl`"

ConfName=optimized
BinaryName=python
SymlinkName=python%{pybasever}
PathFixWithThisBinary=true

%configure \
  --prefix=%{pyroot} \
  --libdir=%{libdir} \
  --mandir=%{pymandir} \
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
LD_LIBRARY_PATH=%{buildroot}%{pylibdir} %{buildroot}%{pybindir}/python%{pybasever} \
  Tools/scripts/pathfix.py \
  -i "%{buildroot}%{pybindir}/python%{pybasever}" \
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

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc LICENSE README
%dir %{pyroot}
%dir %{pybindir}
%dir %{libdir}
%dir %{pylibdir}
%dir %{pylibdir}/site-packages
%dir %{pylibdir}/site-packages/__pycache__
%dir %{pylibdir}/test
%dir %{pylibdir}/test/audiodata
%dir %{pylibdir}/test/capath
%dir %{pylibdir}/test/data
%dir %{pylibdir}/test/cjkencodings
%dir %{pylibdir}/test/decimaltestdata
%dir %{pylibdir}/test/xmltestdata
%dir %{pylibdir}/test/eintrdata
%dir %{pylibdir}/test/eintrdata/__pycache__
%dir %{pylibdir}/test/imghdrdata
%dir %{pylibdir}/test/subprocessdata
%dir %{pylibdir}/test/subprocessdata/__pycache__
%dir %{pylibdir}/test/sndhdrdata
%dir %{pylibdir}/test/support
%dir %{pylibdir}/test/support/__pycache__
%dir %{pylibdir}/test/tracedmodules
%dir %{pylibdir}/test/tracedmodules/__pycache__
%dir %{pylibdir}/test/encoded_modules
%dir %{pylibdir}/test/encoded_modules/__pycache__
%dir %{pylibdir}/test/test_import
%dir %{pylibdir}/test/test_import/data
%dir %{pylibdir}/test/test_import/data/circular_imports
%dir %{pylibdir}/test/test_import/data/circular_imports/subpkg
%dir %{pylibdir}/test/test_import/data/circular_imports/subpkg/__pycache__
%dir %{pylibdir}/test/test_import/data/circular_imports/__pycache__
%dir %{pylibdir}/test/test_import/__pycache__
%dir %{pylibdir}/test/test_importlib
%dir %{pylibdir}/test/test_importlib/namespace_pkgs
%dir %{pylibdir}/test/test_importlib/namespace_pkgs/both_portions
%dir %{pylibdir}/test/test_importlib/namespace_pkgs/both_portions/foo
%dir %{pylibdir}/test/test_importlib/namespace_pkgs/both_portions/foo/__pycache__
%dir %{pylibdir}/test/test_importlib/namespace_pkgs/not_a_namespace_pkg
%dir %{pylibdir}/test/test_importlib/namespace_pkgs/not_a_namespace_pkg/foo
%dir %{pylibdir}/test/test_importlib/namespace_pkgs/not_a_namespace_pkg/foo/__pycache__
%dir %{pylibdir}/test/test_importlib/namespace_pkgs/portion1
%dir %{pylibdir}/test/test_importlib/namespace_pkgs/portion1/foo
%dir %{pylibdir}/test/test_importlib/namespace_pkgs/portion1/foo/__pycache__
%dir %{pylibdir}/test/test_importlib/namespace_pkgs/portion2
%dir %{pylibdir}/test/test_importlib/namespace_pkgs/portion2/foo
%dir %{pylibdir}/test/test_importlib/namespace_pkgs/portion2/foo/__pycache__
%dir %{pylibdir}/test/test_importlib/namespace_pkgs/project1
%dir %{pylibdir}/test/test_importlib/namespace_pkgs/project1/parent
%dir %{pylibdir}/test/test_importlib/namespace_pkgs/project1/parent/child
%dir %{pylibdir}/test/test_importlib/namespace_pkgs/project1/parent/child/__pycache__
%dir %{pylibdir}/test/test_importlib/namespace_pkgs/project2
%dir %{pylibdir}/test/test_importlib/namespace_pkgs/project2/parent
%dir %{pylibdir}/test/test_importlib/namespace_pkgs/project2/parent/child
%dir %{pylibdir}/test/test_importlib/namespace_pkgs/project2/parent/child/__pycache__
%dir %{pylibdir}/test/test_importlib/namespace_pkgs/project3
%dir %{pylibdir}/test/test_importlib/namespace_pkgs/project3/parent
%dir %{pylibdir}/test/test_importlib/namespace_pkgs/project3/parent/child
%dir %{pylibdir}/test/test_importlib/namespace_pkgs/project3/parent/child/__pycache__
%dir %{pylibdir}/test/test_importlib/namespace_pkgs/module_and_namespace_package
%dir %{pylibdir}/test/test_importlib/namespace_pkgs/module_and_namespace_package/a_test
%dir %{pylibdir}/test/test_importlib/namespace_pkgs/module_and_namespace_package/__pycache__
%dir %{pylibdir}/test/test_importlib/builtin
%dir %{pylibdir}/test/test_importlib/builtin/__pycache__
%dir %{pylibdir}/test/test_importlib/extension
%dir %{pylibdir}/test/test_importlib/extension/__pycache__
%dir %{pylibdir}/test/test_importlib/frozen
%dir %{pylibdir}/test/test_importlib/frozen/__pycache__
%dir %{pylibdir}/test/test_importlib/import_
%dir %{pylibdir}/test/test_importlib/import_/__pycache__
%dir %{pylibdir}/test/test_importlib/source
%dir %{pylibdir}/test/test_importlib/source/__pycache__
%dir %{pylibdir}/test/test_importlib/__pycache__
%dir %{pylibdir}/test/test_asyncio
%dir %{pylibdir}/test/test_asyncio/__pycache__
%dir %{pylibdir}/test/test_email
%dir %{pylibdir}/test/test_email/data
%dir %{pylibdir}/test/test_email/__pycache__
%dir %{pylibdir}/test/test_json
%dir %{pylibdir}/test/test_json/__pycache__
%dir %{pylibdir}/test/__pycache__
%dir %{pylibdir}/asyncio
%dir %{pylibdir}/asyncio/__pycache__
%dir %{pylibdir}/collections
%dir %{pylibdir}/collections/__pycache__
%dir %{pylibdir}/concurrent
%dir %{pylibdir}/concurrent/futures
%dir %{pylibdir}/concurrent/futures/__pycache__
%dir %{pylibdir}/concurrent/__pycache__
%dir %{pylibdir}/encodings
%dir %{pylibdir}/encodings/__pycache__
%dir %{pylibdir}/email
%dir %{pylibdir}/email/mime
%dir %{pylibdir}/email/mime/__pycache__
%dir %{pylibdir}/email/__pycache__
%dir %{pylibdir}/ensurepip
%dir %{pylibdir}/ensurepip/_bundled
%dir %{pylibdir}/ensurepip/__pycache__
%dir %{pylibdir}/html
%dir %{pylibdir}/html/__pycache__
%dir %{pylibdir}/json
%dir %{pylibdir}/json/__pycache__
%dir %{pylibdir}/http
%dir %{pylibdir}/http/__pycache__
%dir %{pylibdir}/dbm
%dir %{pylibdir}/dbm/__pycache__
%dir %{pylibdir}/xmlrpc
%dir %{pylibdir}/xmlrpc/__pycache__
%dir %{pylibdir}/sqlite3
%dir %{pylibdir}/sqlite3/test
%dir %{pylibdir}/sqlite3/test/__pycache__
%dir %{pylibdir}/sqlite3/__pycache__
%dir %{pylibdir}/logging
%dir %{pylibdir}/logging/__pycache__
%dir %{pylibdir}/wsgiref
%dir %{pylibdir}/wsgiref/__pycache__
%dir %{pylibdir}/urllib
%dir %{pylibdir}/urllib/__pycache__
%dir %{pylibdir}/lib2to3
%dir %{pylibdir}/lib2to3/fixes
%dir %{pylibdir}/lib2to3/fixes/__pycache__
%dir %{pylibdir}/lib2to3/pgen2
%dir %{pylibdir}/lib2to3/pgen2/__pycache__
%dir %{pylibdir}/lib2to3/tests
%dir %{pylibdir}/lib2to3/tests/data
%dir %{pylibdir}/lib2to3/tests/data/fixers
%dir %{pylibdir}/lib2to3/tests/data/fixers/myfixes
%dir %{pylibdir}/lib2to3/tests/data/fixers/myfixes/__pycache__
%dir %{pylibdir}/lib2to3/tests/data/fixers/__pycache__
%dir %{pylibdir}/lib2to3/tests/data/__pycache__
%dir %{pylibdir}/lib2to3/tests/__pycache__
%dir %{pylibdir}/lib2to3/__pycache__
%dir %{pylibdir}/ctypes
%dir %{pylibdir}/ctypes/test
%dir %{pylibdir}/ctypes/test/__pycache__
%dir %{pylibdir}/ctypes/macholib
%dir %{pylibdir}/ctypes/macholib/__pycache__
%dir %{pylibdir}/ctypes/__pycache__
%dir %{pylibdir}/idlelib
%dir %{pylibdir}/idlelib/Icons
%dir %{pylibdir}/idlelib/idle_test
%dir %{pylibdir}/idlelib/idle_test/__pycache__
%dir %{pylibdir}/idlelib/__pycache__
%dir %{pylibdir}/distutils
%dir %{pylibdir}/distutils/command
%dir %{pylibdir}/distutils/command/__pycache__
%dir %{pylibdir}/distutils/tests
%dir %{pylibdir}/distutils/tests/__pycache__
%dir %{pylibdir}/distutils/__pycache__
%dir %{pylibdir}/xml
%dir %{pylibdir}/xml/dom
%dir %{pylibdir}/xml/dom/__pycache__
%dir %{pylibdir}/xml/etree
%dir %{pylibdir}/xml/etree/__pycache__
%dir %{pylibdir}/xml/parsers
%dir %{pylibdir}/xml/parsers/__pycache__
%dir %{pylibdir}/xml/sax
%dir %{pylibdir}/xml/sax/__pycache__
%dir %{pylibdir}/xml/__pycache__
%dir %{pylibdir}/importlib
%dir %{pylibdir}/importlib/__pycache__
%dir %{pylibdir}/turtledemo
%dir %{pylibdir}/turtledemo/__pycache__
%dir %{pylibdir}/multiprocessing
%dir %{pylibdir}/multiprocessing/dummy
%dir %{pylibdir}/multiprocessing/dummy/__pycache__
%dir %{pylibdir}/multiprocessing/__pycache__
%dir %{pylibdir}/unittest
%dir %{pylibdir}/unittest/test
%dir %{pylibdir}/unittest/test/testmock
%dir %{pylibdir}/unittest/test/testmock/__pycache__
%dir %{pylibdir}/unittest/test/__pycache__
%dir %{pylibdir}/unittest/__pycache__
%dir %{pylibdir}/venv
%dir %{pylibdir}/venv/scripts
%dir %{pylibdir}/venv/scripts/posix
%dir %{pylibdir}/venv/__pycache__
%dir %{pylibdir}/curses
%dir %{pylibdir}/curses/__pycache__
%dir %{pylibdir}/pydoc_data
%dir %{pylibdir}/pydoc_data/__pycache__
%dir %{pylibdir}/plat-linux
%dir %{pylibdir}/plat-linux/__pycache__
%dir %{pylibdir}/__pycache__
%dir %{pylibdir}/config-3.5m
%dir %{pylibdir}/config-3.5m/__pycache__
%dir %{dynload_dir}
%dir %{pylibdir}/Tools
%dir %{pylibdir}/Tools/freeze
%dir %{pylibdir}/Tools/freeze/test
%dir %{pylibdir}/Tools/freeze/test/__pycache__
%dir %{pylibdir}/Tools/freeze/__pycache__
%dir %{pylibdir}/Tools/i18n
%dir %{pylibdir}/Tools/i18n/__pycache__
%dir %{pylibdir}/Tools/pynche
%dir %{pylibdir}/Tools/pynche/X
%dir %{pylibdir}/Tools/pynche/__pycache__
%dir %{pylibdir}/Tools/scripts
%dir %{pylibdir}/Tools/scripts/__pycache__
%dir %{pylibdir}/Tools/demo
%dir %{pylibdir}/Tools/demo/__pycache__
%dir %{pylibdir}/Doc
%dir %{pylibdir}/Doc/tools
%dir %{pylibdir}/Doc/tools/extensions
%dir %{pylibdir}/Doc/tools/extensions/__pycache__
%dir %{pylibdir}/Doc/tools/pydoctheme
%dir %{pylibdir}/Doc/tools/pydoctheme/static
%dir %{pylibdir}/Doc/tools/static
%dir %{pylibdir}/Doc/tools/templates
%dir %{pylibdir}/Doc/tools/__pycache__
%dir %{libroot}/pkgconfig
%dir %{pyroot}/include
%dir %{pyroot}/include/python3.5m
%dir %{pyroot}/share
%dir %{pymandir}
%dir %{pymandir}/man1
%{pybindir}/*
%{pyroot}/include/python3.5m/*
%{libdir}/*
%{libdir}/pkgconfig/*
%{pylibdir}/*
%{pylibdir}/Doc/tools/*
%{pylibdir}/Doc/tools/__pycache__/*
%{pylibdir}/Doc/tools/extensions/*
%{pylibdir}/Doc/tools/extensions/__pycache__/*
%{pylibdir}/Doc/tools/pydoctheme/*
%{pylibdir}/Doc/tools/pydoctheme/static/*
%{pylibdir}/Doc/tools/static/*
%{pylibdir}/Doc/tools/templates/*
%{pylibdir}/Tools/*
%{pylibdir}/Tools/demo/*
%{pylibdir}/Tools/demo/__pycache__/*
%{pylibdir}/Tools/freeze/*
%{pylibdir}/Tools/freeze/__pycache__/*
%{pylibdir}/Tools/freeze/test/*
%{pylibdir}/Tools/freeze/test/__pycache__/*
%{pylibdir}/Tools/i18n/*
%{pylibdir}/Tools/i18n/__pycache__/*
%{pylibdir}/Tools/pynche/*
%{pylibdir}/Tools/pynche/X/*
%{pylibdir}/Tools/pynche/__pycache__/*
%{pylibdir}/Tools/scripts/*
%{pylibdir}/Tools/scripts/__pycache__/*
%{pylibdir}/__pycache__/*
%{pylibdir}/asyncio/*
%{pylibdir}/asyncio/__pycache__/*
%{pylibdir}/collections/*
%{pylibdir}/collections/__pycache__/*
%{pylibdir}/concurrent/*
%{pylibdir}/concurrent/__pycache__/*
%{pylibdir}/concurrent/futures/*
%{pylibdir}/concurrent/futures/__pycache__/*
%{pylibdir}/config-3.5m/*
%{pylibdir}/config-3.5m/__pycache__/*
%{pylibdir}/ctypes/*
%{pylibdir}/ctypes/__pycache__/*
%{pylibdir}/ctypes/macholib/*
%{pylibdir}/ctypes/macholib/__pycache__/*
%{pylibdir}/ctypes/test/*
%{pylibdir}/ctypes/test/__pycache__/*
%{pylibdir}/curses/*
%{pylibdir}/curses/__pycache__/*
%{pylibdir}/dbm/*
%{pylibdir}/dbm/__pycache__/*
%{pylibdir}/distutils/*
%{pylibdir}/distutils/__pycache__/*
%{pylibdir}/distutils/command/*
%{pylibdir}/distutils/command/__pycache__/*
%{pylibdir}/distutils/tests/*
%{pylibdir}/distutils/tests/__pycache__/*
%{pylibdir}/email/*
%{pylibdir}/email/__pycache__/*
%{pylibdir}/email/mime/*
%{pylibdir}/email/mime/__pycache__/*
%{pylibdir}/encodings/*
%{pylibdir}/encodings/__pycache__/*
%{pylibdir}/ensurepip/*
%{pylibdir}/ensurepip/__pycache__/*
%{pylibdir}/ensurepip/_bundled/*
%{pylibdir}/html/*
%{pylibdir}/html/__pycache__/*
%{pylibdir}/http/*
%{pylibdir}/http/__pycache__/*
%{pylibdir}/idlelib/*
%{pylibdir}/idlelib/Icons/*
%{pylibdir}/idlelib/__pycache__/*
%{pylibdir}/idlelib/idle_test/*
%{pylibdir}/idlelib/idle_test/__pycache__/*
%{pylibdir}/importlib/*
%{pylibdir}/importlib/__pycache__/*
%{pylibdir}/json/*
%{pylibdir}/json/__pycache__/*
%{dynload_dir}/*
%{pylibdir}/lib2to3/*
%{pylibdir}/lib2to3/__pycache__/*
%{pylibdir}/lib2to3/fixes/*
%{pylibdir}/lib2to3/fixes/__pycache__/*
%{pylibdir}/lib2to3/pgen2/*
%{pylibdir}/lib2to3/pgen2/__pycache__/*
%{pylibdir}/lib2to3/tests/*
%{pylibdir}/lib2to3/tests/__pycache__/*
%{pylibdir}/lib2to3/tests/data/*
%{pylibdir}/lib2to3/tests/data/__pycache__/*
%{pylibdir}/lib2to3/tests/data/fixers/*
%{pylibdir}/lib2to3/tests/data/fixers/__pycache__/*
%{pylibdir}/lib2to3/tests/data/fixers/myfixes/*
%{pylibdir}/lib2to3/tests/data/fixers/myfixes/__pycache__/*
%{pylibdir}/logging/*
%{pylibdir}/logging/__pycache__/*
%{pylibdir}/multiprocessing/*
%{pylibdir}/multiprocessing/__pycache__/*
%{pylibdir}/multiprocessing/dummy/*
%{pylibdir}/multiprocessing/dummy/__pycache__/*
%{pylibdir}/plat-linux/*
%{pylibdir}/plat-linux/__pycache__/*
%{pylibdir}/pydoc_data/*
%{pylibdir}/pydoc_data/__pycache__/*
%{pylibdir}/site-packages/*
%{pylibdir}/sqlite3/*
%{pylibdir}/sqlite3/__pycache__/*
%{pylibdir}/sqlite3/test/*
%{pylibdir}/sqlite3/test/__pycache__/*
%{pylibdir}/test/*
%{pylibdir}/test/__pycache__/*
%{pylibdir}/test/audiodata/*
%{pylibdir}/test/capath/*
%{pylibdir}/test/cjkencodings/*
%{pylibdir}/test/data/*
%{pylibdir}/test/decimaltestdata/*
%{pylibdir}/test/eintrdata/*
%{pylibdir}/test/eintrdata/__pycache__/*
%{pylibdir}/test/encoded_modules/*
%{pylibdir}/test/encoded_modules/__pycache__/*
%{pylibdir}/test/imghdrdata/*
%{pylibdir}/test/sndhdrdata/*
%{pylibdir}/test/subprocessdata/*
%{pylibdir}/test/subprocessdata/__pycache__/*
%{pylibdir}/test/support/*
%{pylibdir}/test/support/__pycache__/*
%{pylibdir}/test/test_asyncio/*
%{pylibdir}/test/test_asyncio/__pycache__/*
%{pylibdir}/test/test_email/*
%{pylibdir}/test/test_email/__pycache__/*
%{pylibdir}/test/test_email/data/*
%{pylibdir}/test/test_import/*
%{pylibdir}/test/test_import/__pycache__/*
%{pylibdir}/test/test_import/data/circular_imports/*
%{pylibdir}/test/test_import/data/circular_imports/__pycache__/*
%{pylibdir}/test/test_import/data/circular_imports/subpkg/*
%{pylibdir}/test/test_import/data/circular_imports/subpkg/__pycache__/*
%{pylibdir}/test/test_importlib/*
%{pylibdir}/test/test_importlib/__pycache__/*
%{pylibdir}/test/test_importlib/builtin/*
%{pylibdir}/test/test_importlib/builtin/__pycache__/*
%{pylibdir}/test/test_importlib/extension/*
%{pylibdir}/test/test_importlib/extension/__pycache__/*
%{pylibdir}/test/test_importlib/frozen/*
%{pylibdir}/test/test_importlib/frozen/__pycache__/*
%{pylibdir}/test/test_importlib/import_/*
%{pylibdir}/test/test_importlib/import_/__pycache__/*
%{pylibdir}/test/test_importlib/namespace_pkgs/*
%{pylibdir}/test/test_importlib/namespace_pkgs/both_portions/foo/*
%{pylibdir}/test/test_importlib/namespace_pkgs/both_portions/foo/__pycache__/*
%{pylibdir}/test/test_importlib/namespace_pkgs/module_and_namespace_package/*
%{pylibdir}/test/test_importlib/namespace_pkgs/module_and_namespace_package/__pycache__/*
%{pylibdir}/test/test_importlib/namespace_pkgs/module_and_namespace_package/a_test/*
%{pylibdir}/test/test_importlib/namespace_pkgs/not_a_namespace_pkg/foo/*
%{pylibdir}/test/test_importlib/namespace_pkgs/not_a_namespace_pkg/foo/__pycache__/*
%{pylibdir}/test/test_importlib/namespace_pkgs/portion1/foo/*
%{pylibdir}/test/test_importlib/namespace_pkgs/portion1/foo/__pycache__/*
%{pylibdir}/test/test_importlib/namespace_pkgs/portion2/foo/*
%{pylibdir}/test/test_importlib/namespace_pkgs/portion2/foo/__pycache__/*
%{pylibdir}/test/test_importlib/namespace_pkgs/project1/parent/child/*
%{pylibdir}/test/test_importlib/namespace_pkgs/project1/parent/child/__pycache__/*
%{pylibdir}/test/test_importlib/namespace_pkgs/project2/parent/child/*
%{pylibdir}/test/test_importlib/namespace_pkgs/project2/parent/child/__pycache__/*
%{pylibdir}/test/test_importlib/namespace_pkgs/project3/parent/child/*
%{pylibdir}/test/test_importlib/namespace_pkgs/project3/parent/child/__pycache__/*
%{pylibdir}/test/test_importlib/source/*
%{pylibdir}/test/test_importlib/source/__pycache__/*
%{pylibdir}/test/test_json/*
%{pylibdir}/test/test_json/__pycache__/*
%{pylibdir}/test/tracedmodules/*
%{pylibdir}/test/tracedmodules/__pycache__/*
%{pylibdir}/test/xmltestdata/*
%{pylibdir}/turtledemo/*
%{pylibdir}/turtledemo/__pycache__/*
%{pylibdir}/unittest/*
%{pylibdir}/unittest/__pycache__/*
%{pylibdir}/unittest/test/*
%{pylibdir}/unittest/test/__pycache__/*
%{pylibdir}/unittest/test/testmock/*
%{pylibdir}/unittest/test/testmock/__pycache__/*
%{pylibdir}/urllib/*
%{pylibdir}/urllib/__pycache__/*
%{pylibdir}/venv/*
%{pylibdir}/venv/__pycache__/*
%{pylibdir}/venv/scripts/posix/*
%{pylibdir}/wsgiref/*
%{pylibdir}/wsgiref/__pycache__/*
%{pylibdir}/xml/*
%{pylibdir}/xml/__pycache__/*
%{pylibdir}/xml/dom/*
%{pylibdir}/xml/dom/__pycache__/*
%{pylibdir}/xml/etree/*
%{pylibdir}/xml/etree/__pycache__/*
%{pylibdir}/xml/parsers/*
%{pylibdir}/xml/parsers/__pycache__/*
%{pylibdir}/xml/sax/*
%{pylibdir}/xml/sax/__pycache__/*
%{pylibdir}/xmlrpc/*
%{pylibdir}/xmlrpc/__pycache__/*
%{pymandir}/man1/*

%changelog
* Wed Mar 23 2016 Taylor C. Richberger <taywee@gmx.com> - 3.5.1-0
- started development on the present version.  Will be bumped to release 1 when
  compiles and installs properly.
