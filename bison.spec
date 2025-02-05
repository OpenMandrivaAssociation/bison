%define _disable_rebuild_configure 1
%global optflags %{optflags} -Oz

# (tpg) enable PGO build
%bcond_without pgo

Summary:	A GNU general-purpose parser generator
Name:		bison
Version:	3.8.2
Release:	9
License:	GPLv3
Group:		Development/Other
Url:		https://www.gnu.org/software/bison/bison.html
Source0:	ftp://ftp.gnu.org/pub/gnu/bison/bison-%{version}.tar.xz
Source100:	%{name}.rpmlintrc
Patch0:		bison-1.32-extfix.patch
Patch1:		bison-3.8.1-clang.patch
Patch2:		bison-3.8.2-clang-no-Wmaybe-uninitialized.patch
Patch3:		https://github.com/akimd/bison/commit/a166d5450e3f47587b98f6005f9f5627dbe21a5b.patch
BuildRequires:	help2man
BuildRequires:	m4 >= 1.4
BuildRequires:	perl-Locale-gettext
# needed for tests
BuildRequires:	autoconf
BuildRequires:	flex
Requires:	m4 >= 1.4
Requires(post,preun):	chkconfig
Obsoletes:	%{mklibname bison -d -s} < 2.6.2

%description
Bison is a general purpose parser generator which converts a grammar
description for an LALR context-free grammar into a C program to parse
that grammar.  Bison can be used to develop a wide range of language
parsers, from ones used in simple desk calculators to complex programming
languages.  Bison is upwardly compatible with Yacc, so any correctly
written Yacc grammar should work with Bison without any changes.  If
you know Yacc, you shouldn't have any trouble using Bison (but you do need
to be very proficient in C programming to be able to use Bison).  Many
programs use Bison as part of their build process. Bison is only needed
on systems that are used for development.

If your system will be used for C development, you should install Bison
since it is used to build many C programs.

%prep
%autosetup -p1

# Avoid regenerating the info pages
sed -i '2iexport TZ=UTC' build-aux/mdate-sh

%build
%if %{with pgo}
export LD_LIBRARY_PATH="$(pwd)"

CFLAGS="%{optflags} -fprofile-generate" \
CXXFLAGS="%{optflags} -fprofile-generate" \
LDFLAGS="%{build_ldflags} -fprofile-generate" \
%configure \
	--disable-rpath \
	--enable-threads

%make_build

%make_build check ||:

unset LD_LIBRARY_PATH
llvm-profdata merge --output=%{name}-llvm.profdata $(find . -name "*.profraw" -type f)
PROFDATA="$(realpath %{name}-llvm.profdata)"
rm -f *.profraw

make clean
# We can't add -fprofile-instr-use= here because it breaks running
# configure again (mismatching macros in early parts)
%endif
%configure \
	--disable-rpath \
	--enable-threads || (cat config.log && exit 1)

%make_build \
%if %{with pgo}
	CFLAGS="%{optflags} -fprofile-use=$PROFDATA" \
	CXXFLAGS="%{optflags} -fprofile-use=$PROFDATA" \
	LDFLAGS="%{build_ldflags} -fprofile-use=$PROFDATA"
%endif

%check
%make_build check ||:

%install
%make_install

mv %{buildroot}%{_bindir}/yacc %{buildroot}%{_bindir}/yacc.bison
mv %{buildroot}%{_mandir}/man1/yacc.1 %{buildroot}%{_mandir}/man1/yacc.bison.1

%find_lang %{name} --all-name

%post
%{_sbindir}/update-alternatives --install %{_bindir}/yacc yacc %{_bindir}/yacc.bison 10

%preun
if [ $1 -eq 0 ]; then
  %{_sbindir}/update-alternatives --remove yacc %{_bindir}/yacc.bison
fi

%files -f %{name}.lang
%doc %{_docdir}/%{name}
%{_bindir}/*
%dir %{_datadir}/bison
%{_datadir}/bison/*
%{_datadir}/aclocal/*
%doc %{_infodir}/bison.info*
%doc %{_mandir}/man1/*
# Not very useful, but mandated by POSIX.2
%{_libdir}/liby.a
