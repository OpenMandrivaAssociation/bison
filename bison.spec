%define staticdevelname %mklibname bison -d -s

Summary:	A GNU general-purpose parser generator
Name:		bison
Version:	2.7
Release:	2
License:	GPL
Group:		Development/Other
URL:		http://www.gnu.org/software/bison/bison.html
Source0:	ftp://ftp.gnu.org/pub/gnu/bison/bison-%{version}.tar.xz
Patch0:		bison-1.32-extfix.patch
Requires:	m4 >= 1.4
BuildRequires:	help2man
BuildRequires:	m4 >= 1.4
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
%setup -q
%patch0 -p1 -b .extfix

%build
%configure2_5x \
	--disable-rpath \
	--enable-threads

%make

%check
make check

%install
%makeinstall_std

mv %{buildroot}%{_bindir}/yacc %{buildroot}%{_bindir}/yacc.bison


%find_lang %{name}
%find_lang %{name}-runtime
cat %{name}-runtime.lang >> %{name}.lang

rm -f %{buildroot}%{_mandir}/man1/yacc.1

# (tpg) this is not needed at all
rm -rf %{buildroot}%{_libdir}/liby.a

%post
%{_sbindir}/update-alternatives --install %{_bindir}/yacc yacc %{_bindir}/yacc.bison 10

%preun
if [ $1 -eq 0 ]; then
  %{_sbindir}/update-alternatives --remove yacc %{_bindir}/yacc.bison
fi

%triggerpostun -- byacc <= 1.9-16mdk
%{_sbindir}/update-alternatives --install %{_bindir}/yacc yacc %{_bindir}/yacc.bison 10

%files -f %{name}.lang
%doc COPYING NEWS README
%{_bindir}/*
%dir %{_datadir}/bison
%{_datadir}/bison/*
%{_datadir}/aclocal/*
%{_infodir}/bison.info*
%{_mandir}/man1/*
