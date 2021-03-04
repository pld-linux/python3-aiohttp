#
# Conditional build:
%bcond_without	doc	# API documentation
%bcond_without	tests	# unit tests

%define		module	template
Summary:	Async http client/server framework
Summary(pl.UTF-8):	Szkielet asynchronicznego klienta/serwera http
Name:		python3-aiohttp
Version:	3.7.4
Release:	1
License:	Apache v2.0
Group:		Libraries/Python
#Source0Download: https://pypi.org/simple/aiohttp/
Source0:	https://files.pythonhosted.org/packages/source/a/aiohttp/aiohttp-%{version}.tar.gz
# Source0-md5:	586eb4e4dcb1e41242ede0c5bcfd4014
# adjusted from https://github.com/aio-libs/aiohttp/commit/9afc44b052643213da15c9583ecbd643ca999601.patch
Patch0:		%{name}-brotli.patch
URL:		https://pypi.org/project/aiohttp/
BuildRequires:	python3-devel >= 1:3.6
BuildRequires:	python3-setuptools
%if %{with tests}
BuildRequires:	python3-async_timeout >= 3.0
BuildRequires:	python3-attrs >= 17.3.0
BuildRequires:	python3-brotli
BuildRequires:	python3-chardet >= 2.0
BuildRequires:	python3-freezegun
BuildRequires:	python3-gunicorn
%if "%{py3_ver}" < "3.7"
BuildRequires:	python3-idna-ssl
%endif
BuildRequires:	python3-multidict >= 4.5
BuildRequires:	python3-pytest >= 3.8.2
BuildRequires:	python3-pytest-cov
BuildRequires:	python3-pytest-mock
BuildRequires:	python3-re_assert
BuildRequires:	python3-typing_extensions >= 3.6.5
BuildRequires:	python3-yarl >= 1.0
%endif
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.714
# if using noarchpackage, replace with:
#BuildRequires:	rpmbuild(macros) >= 1.752
BuildRequires:	sed >= 4.0
%if %{with doc}
BuildRequires:	python3-aiohttp_theme
BuildRequires:	python3-sphinxcontrib-asyncio
BuildRequires:	python3-sphinxcontrib-blockdiag
BuildRequires:	sphinx-pdg-3
%endif
# replace with other requires if defined in setup.py
Requires:	python3-modules >= 1:3.6
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Async http client/server framework.

%description -l pl.UTF-8
Szkielet asynchronicznego klienta/serwera http.

%package apidocs
Summary:	aiohttp API documentation
Summary(pl.UTF-8):	Dokumentacja API aiohttp
Group:		Documentation
%{?noarchpackage}

%description apidocs
API documentation for aiohttp.

%description apidocs -l pl.UTF-8
Dokumentacja API aiohttp.

%prep
%setup -q -n aiohttp-%{version}
%patch0 -p1

%{__sed} -i -e '1s,/usr/bin/env python3,%{__python3},' examples/*.py examples/legacy/*.py

# adjust for python 3.7+
%{__sed} -i -e '/^from async_generator/d; /^ *@async_generator/d; s/await yield_/yield/' tests/*.py

# until we have pytest >= 6:
%{__sed} -i -e '/assert_outcomes/ s/errors=/error=/' tests/test_pytest_plugin.py

%build
%py3_build

%if %{with tests}
# test_data_stream_exc_chain uses network, fails
# test_async_iterable_payload_default_content_type, test_async_iterable_payload_explicit_content_type fail with TypeError (need update?)
# test_mark_formdata_as_processed requires network
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
PYTEST_PLUGINS="pytest_cov.plugin,pytest_mock" \
%{__python3} -m pytest tests -k 'not (test_data_stream_exc_chain or test_async_iterable_payload_default_content_type or test_async_iterable_payload_explicit_content_type or test_mark_formdata_as_processed)'
%endif

%if %{with doc}
%{__make} -C docs html \
	SPHINXBUILD=sphinx-build-3
%endif

%install
rm -rf $RPM_BUILD_ROOT

%py3_install

%{__rm} -r $RPM_BUILD_ROOT%{py3_sitedir}/aiohttp/.hash
%{__rm} $RPM_BUILD_ROOT%{py3_sitedir}/aiohttp/*.{c,h,pxd,pxi,pyx}

install -d $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}
cp -pr examples/* $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc CHANGES.rst CONTRIBUTORS.txt README.rst
%dir %{py3_sitedir}/aiohttp
%attr(755,root,root) %{py3_sitedir}/aiohttp/*.so
%{py3_sitedir}/aiohttp/*.py
%{py3_sitedir}/aiohttp/*.pyi
%{py3_sitedir}/aiohttp/py.typed
%{py3_sitedir}/aiohttp/__pycache__
%{py3_sitedir}/aiohttp-%{version}-py*.egg-info
%{_examplesdir}/%{name}-%{version}

%if %{with doc}
%files apidocs
%defattr(644,root,root,755)
%doc docs/_build/html/*
%endif
