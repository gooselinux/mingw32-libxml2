%global __strip %{_mingw32_strip}
%global __objdump %{_mingw32_objdump}
%global _use_internal_dependency_generator 0
%global __find_requires %{_mingw32_findrequires}
%global __find_provides %{_mingw32_findprovides}
%define __debug_install_post %{_mingw32_debug_install_post}

Name:           mingw32-libxml2
Version:        2.7.6
Release:        2%{?dist}
Summary:        MinGW Windows libxml2 XML processing library


License:        MIT
Group:          Development/Libraries
URL:            http://xmlsoft.org/
Source0:        ftp://xmlsoft.org/libxml2/libxml2-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

# Not required for MinGW.
#Patch0:         libxml2-multilib.patch

# MinGW-specific patches.
Patch1000:      mingw32-libxml2-2.7.2-with-modules.patch
Patch1001:      mingw32-libxml2-static-build-compile-fix.patch
Patch1002:      libxml2-gnome-bug-561340-fix.patch

BuildArch:      noarch

BuildRequires:  mingw32-filesystem >= 52
BuildRequires:  mingw32-gcc
BuildRequires:  mingw32-binutils

BuildRequires:  mingw32-dlfcn
BuildRequires:  mingw32-gettext
BuildRequires:  mingw32-iconv
BuildRequires:  mingw32-zlib

BuildRequires:  autoconf, automake, libtool

Requires:       pkgconfig


%description
MinGW Windows libxml2 XML processing library.


%package static
Summary:        Static version of the MinGW Windows XML processing library
Requires:       %{name} = %{version}-%{release}
Group:          Development/Libraries

%description static
Static version of the MinGW Windows XML processing library.


%{_mingw32_debug_package}


%prep
%setup -q -n libxml2-%{version}

%patch1000 -p1
%patch1001 -p0
%patch1002 -p0

# Patched configure.in, so rebuild configure.
libtoolize --force --copy
autoreconf


%build
# LibXML2 can't build static and shared libraries in one go, so we
# build LibXML2 twice here
mkdir build_static
pushd build_static
    LDFLAGS="-no-undefined" \
    %{_mingw32_configure} --without-python --with-modules --enable-static --disable-shared --with-threads=win32 CFLAGS="$CFLAGS -DLIBXML_STATIC_FOR_DLL"
    make %{?_smp_mflags}
popd

mkdir build_shared
pushd build_shared
    LDFLAGS="-no-undefined" \
    %{_mingw32_configure} --without-python --with-modules --disable-static --enable-shared --with-threads=win32
    make %{?_smp_mflags}
popd


%install
rm -rf $RPM_BUILD_ROOT

# First install all the files belonging to the shared build
make -C build_shared DESTDIR=$RPM_BUILD_ROOT install

# Install all the files from the static build in a seperate folder
# and move the static libraries to the right location
make -C build_static DESTDIR=$RPM_BUILD_ROOT/build_static install
mv $RPM_BUILD_ROOT/build_static%{_mingw32_libdir}/*.a $RPM_BUILD_ROOT%{_mingw32_libdir}

# Manually merge the libtool files
sed -i s/"old_library=''"/"old_library='libxml2.a'"/ $RPM_BUILD_ROOT%{_mingw32_libdir}/libxml2.la

# Drop the folder which was temporary used for installing the static bits
rm -rf $RPM_BUILD_ROOT/build_static

# Remove manpages which duplicate Fedora native.
rm -rf $RPM_BUILD_ROOT%{_mingw32_mandir}


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%{_mingw32_bindir}/libxml2-2.dll
%{_mingw32_bindir}/xml2-config
%{_mingw32_bindir}/xmlcatalog.exe
%{_mingw32_bindir}/xmllint.exe
%{_mingw32_libdir}/libxml2.dll.a
%{_mingw32_libdir}/libxml2.la
%{_mingw32_libdir}/pkgconfig/libxml-2.0.pc
%{_mingw32_libdir}/xml2Conf.sh
%{_mingw32_includedir}/libxml2
%{_mingw32_datadir}/aclocal/*
%{_mingw32_docdir}/libxml2-%{version}/
%{_mingw32_datadir}/gtk-doc/html/libxml2/


%files static
%defattr(-,root,root,-)
%{_mingw32_libdir}/libxml2.a


%changelog
* Fri Feb  4 2011 Andrew Beekhof <abeekhof@redhat.com> - 2.7.6-2
- Rebuild for new version of mingw32-zlib/mingw32-glib2
  Related: rhbz#658833

* Tue Dec 28 2010 Andrew Beekhof <abeekhof@redhat.com> - 2.7.6-1.4
- Rebuild everything with gcc-4.4
  Related: rhbz#658833

* Fri Dec 24 2010 Andrew Beekhof <abeekhof@redhat.com> - 2.7.6-1.3
- The use of ExclusiveArch conflicts with noarch, using an alternate COLLECTION to limit builds
  Related: rhbz#658833

* Wed Dec 22 2010 Andrew Beekhof <abeekhof@redhat.com> - 2.7.6-1.2
- Only build mingw packages on x86_64
  Related: rhbz#658833

* Wed Dec 22 2010 Andrew Beekhof <abeekhof@redhat.com> - 2.7.6-1.1
- Bump the revision to avoid tag collision
  Related: rhbz#658833

* Fri Nov 20 2009 Erik van Pienbroek <epienbro@fedoraproject.org> - 2.7.6-1
- Update to 2.7.6
- Updated the configure arguments so that the native Win32 thread API
  will be used instead of pthreads

* Fri Sep 25 2009 Erik van Pienbroek <epienbro@fedoraproject.org> - 2.7.5-2
- Added a patch to fix GNOME bug #561340

* Thu Sep 24 2009 Erik van Pienbroek <epienbro@fedoraproject.org> - 2.7.5-1
- Update to 2.7.5

* Fri Sep 18 2009 Erik van Pienbroek <epienbro@fedoraproject.org> - 2.7.4-3
- Rebuild because of broken mingw32-gcc/mingw32-binutils

* Sat Sep 12 2009 Erik van Pienbroek <epienbro@fedoraproject.org> - 2.7.4-2
- Always use the native win32 thread API even when pthreads is available
- Dropped a patch which isn't necessary anymore

* Fri Sep 11 2009 Erik van Pienbroek <epienbro@fedoraproject.org> - 2.7.4-1
- Update to 2.7.4
- Drop upstreamed libxml2-2.7.3-ficora-parse.patch patch
- Added a new patch to fix compatibility with the w32 port of pthreads
- Use %%global instead of %%define
- Automatically generate debuginfo subpackage

* Mon Aug 10 2009 Daniel Veillard <veillard@redhat.com> - 2.7.3-3
- two patches for parsing problems CVE-2009-2414 and CVE-2009-2416

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.7.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon May  4 2009 Erik van Pienbroek <epienbro@fedoraproject.org> - 2.7.3-1
- Update to 2.7.3

* Fri Apr  3 2009 Erik van Pienbroek <epienbro@fedoraproject.org> - 2.7.2-9
- Fixed %%defattr line
- Added -static subpackage. Applications which want to link
  against this static library needs to add -DLIBXML_STATIC to the CFLAGS
- This package shouldn't own %%{_mingw32_libdir}/pkgconfig

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.7.2-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Fri Feb 20 2009 Richard W.M. Jones <rjones@redhat.com> - 2.7.2-7
- Rebuild for mingw32-gcc 4.4

* Mon Jan 26 2009 Richard W.M. Jones <rjones@redhat.com> - 2.7.2-6
- Rerun autoreconf after patching configure.in (Erik van Pienbroek).
- Rebuild libtool for Rawhide / libtool 2.
- Add BRs dlfcn and iconv.

* Fri Jan 23 2009 Richard W.M. Jones <rjones@redhat.com> - 2.7.2-5
- Use _smp_mflags.
- Disable static libraries.

* Tue Jan 13 2009 Richard W.M. Jones <rjones@redhat.com> - 2.7.2-4
- Requires pkgconfig.

* Sat Oct 25 2008 Richard W.M. Jones <rjones@redhat.com> - 2.7.2-3
- Enable modules support for libxslt.

* Fri Oct 17 2008 Richard W.M. Jones <rjones@redhat.com> - 2.7.2-1
- Resynch to native Fedora package + patch.

* Wed Sep 24 2008 Richard W.M. Jones <rjones@redhat.com> - 2.7.1-2
- Rename mingw -> mingw32.

* Mon Sep 22 2008 Daniel P. Berrange <berrange@redhat.com> - 2.7.1-1
- Update to 2.7.1 release

* Sun Sep 21 2008 Richard W.M. Jones <rjones@redhat.com> - 2.6.32-5
- Remove manpages which duplicate Fedora native.

* Wed Sep 10 2008 Richard W.M. Jones <rjones@redhat.com> - 2.6.32-4
- Remove static libraries.
- List libdir files explicitly.

* Fri Sep  5 2008 Richard W.M. Jones <rjones@redhat.com> - 2.6.32-3
- Use RPM macros from mingw-filesystem.
- BuildArch is noarch.

* Mon Jul  7 2008 Richard W.M. Jones <rjones@redhat.com> - 2.6.32-1
- Initial RPM release, largely based on earlier work from several sources.
