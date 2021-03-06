# dont want lto on a static lib
%define _disable_lto 1

%define _disable_rebuild_configure 1
%ifnarch riscv64
%global optflags %{optflags} -O3
%endif

# (tpg) enable PGO build
%ifnarch riscv64
%bcond_without pgo
%else
%bcond_with pgo
%endif

Summary:	A GNU general-purpose parser generator
Name:		bison
Version:	3.7.6
Release:	1
License:	GPLv3
Group:		Development/Other
Url:		http://www.gnu.org/software/bison/bison.html
Source0:	ftp://ftp.gnu.org/pub/gnu/bison/bison-%{version}.tar.xz
Source100:	%{name}.rpmlintrc
Patch0:		bison-1.32-extfix.patch
Patch1:		bison-3.3.1-clang.patch
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

%build
%if %{with pgo}
export LLVM_PROFILE_FILE=%{name}-%p.profile.d
export LD_LIBRARY_PATH="$(pwd)"
CFLAGS="%{optflags} -fprofile-instr-generate" \
CXXFLAGS="%{optflags} -fprofile-instr-generate" \
FFLAGS="$CFLAGS" \
FCFLAGS="$CFLAGS" \
LDFLAGS="%{ldflags} -fprofile-instr-generate" \
%configure \
	--disable-rpath \
	--enable-threads

%make_build

%make_build check ||:

unset LD_LIBRARY_PATH
unset LLVM_PROFILE_FILE
llvm-profdata merge --output=%{name}.profile *.profile.d
rm -f *.profile.d
make clean
# We can't add -fprofile-instr-use= here because it breaks running
# configure again (mismatching macros in early parts)
%endif
%configure \
	--disable-rpath \
	--enable-threads || (cat config.log && exit 1)

%make_build \
%if %{with pgo}
	CFLAGS="%{optflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
	CXXFLAGS="%{optflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
	LDFLAGS="%{ldflags} -fprofile-instr-use=$(realpath %{name}.profile)" \
%endif

%check
%make_build check ||:

%install
%make_install

mv %{buildroot}%{_bindir}/yacc %{buildroot}%{_bindir}/yacc.bison
mv %{buildroot}%{_mandir}/man1/yacc.1 %{buildroot}%{_mandir}/man1/yacc.bison.1

%find_lang %{name}
%find_lang %{name}-runtime
%find_lang %{name}-gnulib
cat %{name}-runtime.lang >> %{name}.lang
cat %{name}-gnulib.lang >> %{name}.lang

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
%{_infodir}/bison.info*
%{_mandir}/man1/*
# Not very useful, but mandated by POSIX.2
%{_libdir}/liby.a
