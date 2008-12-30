Summary:	A GNU general-purpose parser generator
Name:		bison
Version:	2.4.1
Release:	%mkrel 1
License:	GPL
Group:		Development/Other
URL:		http://www.gnu.org/software/bison/bison.html
Source0:	ftp://ftp.gnu.org/pub/gnu/bison/bison-%{version}.tar.bz2
Patch0:		bison-1.32-extfix.patch
# (cjw) disable the test that checks if the input file will not 
# be overwritten when the output filename is equal, because it 
# fails due to additional error messages after the correct one
Patch1:		bison-2.4-disable-input-overwrite-test.patch
Patch2:		bison-2.4-reap_subpipe.patch
Patch3:		bison-2.4.1-format_not_a_string_literal_and_no_format_arguments.diff
Requires(post): info-install
Requires(preun):info-install
Requires:	m4 >= 1.4
BuildRequires:	help2man
BuildRequires:	java-1.6.0-openjdk-devel
BuildRequires:	m4 >= 1.4
Conflicts:	byacc <= 1.9-16mdk
Buildroot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

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
%patch1 -p1 -b .broken_pipe
%patch2 -p1 -b .reap_subpipe
%patch3 -p0 -b .format_not_a_string_literal_and_no_format_arguments

%build
%configure2_5x
%make

%check
make check

%install
rm -rf %{buildroot}

%makeinstall_std

mv %{buildroot}%{_bindir}/yacc %{buildroot}%{_bindir}/yacc.bison

# Remove unpackaged files
rm %{buildroot}%{_libdir}/liby.a

%find_lang %{name}
%find_lang %{name}-runtime
cat %name-runtime.lang >> %name.lang

%post
%_install_info %{name}.info
%{_sbindir}/update-alternatives --install %{_bindir}/yacc yacc %{_bindir}/yacc.bison 10

%preun
%_remove_install_info %{name}.info
if [ $1 -eq 0 ]; then
  %{_sbindir}/update-alternatives --remove yacc %{_bindir}/yacc.bison
fi

%triggerpostun -- byacc <= 1.9-16mdk
%{_sbindir}/update-alternatives --install %{_bindir}/yacc yacc %{_bindir}/yacc.bison 10

%clean
rm -rf %{buildroot}

%files -f %{name}.lang
%defattr(-,root,root)
%doc COPYING NEWS README
%{_bindir}/*
%dir %{_datadir}/bison
%{_datadir}/bison/*
%{_datadir}/aclocal/*
%{_infodir}/bison.info*
%{_mandir}/man1/*
