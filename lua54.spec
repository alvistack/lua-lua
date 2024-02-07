# Copyright 2024 Wong Hoi Sing Edison <hswong3i@pantarei-design.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

%define debug_package %{nil}

%global source_date_epoch_from_changelog 0

Name: lua54
Epoch: 100
Version: 5.4.6
Release: 1%{?dist}
Summary: Small Embeddable Language with Procedural Syntax
License: GPL-3.0-or-later
URL: https://github.com/lua/lua/tags
Source0: %{name}_%{version}.orig.tar.gz
# PATCH-FIX-SUSE tweak the buildsystem to produce what is needed for SUSE
Patch0: lua-build-system.patch
# PATCH-FIX-UPSTREAM attrib_test.patch https://is.gd/6DYPgG mcepl@suse.com
# Fix failing test
Patch1: attrib_test.patch
Patch2: files_test.patch
Patch3: main_test.patch
Patch6: shared_link.patch
# PATCH-FIX-UPSTREAM luabugsX.patch https://www.lua.org/bugs.html#5.4.4-X
BuildRequires: libtool
BuildRequires: pkgconfig
BuildRequires: readline-devel
Provides: Lua(API) = 5.4

%description
Lua is a programming language originally designed for extending
applications, but is also frequently used as a general-purpose,
stand-alone language.

Lua combines procedural syntax (similar to Pascal) with
data description constructs based on associative arrays and extensible
semantics. Lua is dynamically typed, interpreted from byte codes, and
has automatic memory management, making it suitable for configuration,
scripting, and rapid prototyping. Lua is implemented as a small library
of C functions, written in ANSI C.

%package -n lua-devel
Summary: Development files for lua
Requires: lua54-libs = %{epoch}:%{version}-%{release}
Requires: lua54 = %{epoch}:%{version}-%{release}
Provides: lua-devel = %{version}
Provides: Lua(devel) = 5.4
Provides: pkgconfig(lua) = %{version}

%description -n lua-devel
Lua is a programming language originally designed for extending
applications, but is also frequently used as a general-purpose,
stand-alone language.

This package contains files needed for embedding lua into your
application.

%package -n lua54-libs
Summary: The Lua integration library

%description -n lua54-libs
Lua is a programming language originally designed for extending
applications, but is also frequently used as a general-purpose,
stand-alone language.

Lua combines procedural syntax (similar to Pascal) with
data description constructs based on associative arrays and extensible
semantics. Lua is dynamically typed, interpreted from byte codes, and
has automatic memory management, making it suitable for configuration,
scripting, and rapid prototyping. Lua is implemented as a small library
of C functions, written in ANSI C.

%package -n lua54-doc
Summary: Documentation for Lua, a small embeddable language
BuildArch: noarch

%description -n lua54-doc
Lua is a programming language originally designed for extending
applications, but is also frequently used as a general-purpose,
stand-alone language.

Lua combines procedural syntax (similar to Pascal) with
data description constructs based on associative arrays and extensible
semantics. Lua is dynamically typed, interpreted from byte codes, and
has automatic memory management, making it suitable for configuration,
scripting, and rapid prototyping. Lua is implemented as a small library
of C functions, written in ANSI C.

%prep
%setup -T -c -n %{name}_%{version}-%{release}
tar -zx -f %{S:0} --strip-components=1 -C .
%autopatch -p1

# manpage
cat doc/lua.1  | sed 's/TH LUA 1/TH LUA54 1/' > doc/lua5.4.1
cat doc/luac.1 | sed 's/TH LUAC 1/TH LUAC54 1/' > doc/luac5.4.1

%build
sed -i -e "s@lib/lua/@%{_lib}/lua/@g" src/luaconf.h
make linux-readline %{_smp_mflags} VERBOSE=1 -C src \
    CC="cc" \
    MYCFLAGS="%{optflags} -std=gnu99 -D_GNU_SOURCE -fPIC -DLUA_COMPAT_MODULE" \
    V=5.4 \
    LIBTOOL="libtool --quiet"

%install
%make_install \
    LIBTOOL="libtool --quiet" \
    INSTALL_TOP="%{buildroot}%{_prefix}" \
    INSTALL_LIB="%{buildroot}%{_libdir}"

find %{buildroot} -type f -name "*.la" -delete -print

# create pkg-config file
cat > lua54.pc <<-EOF
prefix=%{_prefix}
exec_prefix=%{_prefix}
libdir=%{_libdir}
includedir=%{_includedir}/lua5.4
INSTALL_LMOD=%{_datadir}/lua/5.4
INSTALL_CMOD=%{_libdir}/lua/5.4

Name: Lua 5.4
Description: An Extensible Extension Language
Version: %{version}
Libs: -llua54 -lm
Cflags: -I\${includedir}
EOF
install -D -m 644 lua54.pc %{buildroot}%{_libdir}/pkgconfig/lua54.pc

# Compat link with older unprefixed library and with soname 0 from deb/etc
ln -s %{_libdir}/liblua54.so.5.4.0 %{buildroot}%{_libdir}/liblua54.so.5.4
ln -s %{_libdir}/liblua54.so.5.4.0 %{buildroot}%{_libdir}/liblua54.so.0
ln -s %{_libdir}/liblua54.so.5.4.0 %{buildroot}%{_libdir}/liblua.so.5.4

%post -n lua54-libs -p /sbin/ldconfig
%postun -n lua54-libs -p /sbin/ldconfig

%files
%dir %{_libdir}/lua
%dir %{_libdir}/lua/5.4
%dir %{_datadir}/lua
%dir %{_datadir}/lua/5.4
%{_bindir}/*
%{_mandir}/man1/*

%files -n lua54-libs
%{_libdir}/*.so.*

%files -n lua-devel
%dir %{_includedir}/lua5.4
%{_includedir}/lua5.4/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/*.pc

%files -n lua54-doc
%doc doc/*

%changelog
