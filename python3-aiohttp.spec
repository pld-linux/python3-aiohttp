#
# Conditional build:
%bcond_without	doc	# API documentation
%bcond_without	tests	# unit tests

%define		module	template
Summary:	Async http client/server framework
Summary(pl.UTF-8):	Szkielet asynchronicznego klienta/serwera http
Name:		python3-aiohttp
Version:	3.11.11
Release:	1
License:	Apache v2.0
Group:		Libraries/Python
Source0:	https://files.pythonhosted.org/packages/source/a/aiohttp/aiohttp-%{version}.tar.gz
# Source0-md5:	17f04b60068122e998a60a3010679501
Patch0:		disable-towncrier.patch
URL:		https://pypi.org/project/aiohttp/
BuildRequires:	python3-devel >= 1:3.6
BuildRequires:	python3-setuptools
%if %{with tests}
#BuildRequires:	python3-aiodns >= 1.1
BuildRequires:	python3-aiohappyeyeballs
BuildRequires:	python3-aiosignal >= 1.1.2
BuildRequires:	python3-async_timeout >= 4.0
BuildRequires:	python3-async_timeout < 5
%if "%{ver_lt '%{py3_ver}' '3.8'}" == "1"
BuildRequires:	python3-asynctest = 0.13.0
%endif
BuildRequires:	python3-attrs >= 17.3.0
BuildRequires:	python3-brotli
BuildRequires:	python3-charset_normalizer >= 2.0
BuildRequires:	python3-charset_normalizer < 3
BuildRequires:	python3-cchardet
BuildRequires:	python3-freezegun
BuildRequires:	python3-frozenlist >= 1.1.1
BuildRequires:	python3-gunicorn
%if "%{py3_ver}" == "3.6"
BuildRequires:	python3-idna-ssl >= 1.0
%endif
BuildRequires:	python3-multidict >= 4.5
BuildRequires:	python3-multidict < 7
BuildRequires:	python3-pytest >= 3.8.2
BuildRequires:	python3-pytest-cov
BuildRequires:	python3-pytest-mock
BuildRequires:	python3-pytest-xdist
BuildRequires:	python3-re_assert
BuildRequires:	python3-trustme
%if "%{ver_lt '%{py3_ver}' '3.8'}" == "1"
BuildRequires:	python3-typing_extensions >= 3.6.5
%endif
BuildRequires:	python3-yarl >= 1.0
BuildRequires:	python3-yarl < 2
%endif
BuildRequires:	rpm-build >= 4.6
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.749
BuildRequires:	sed >= 4.0
%if %{with doc}
BuildRequires:	python3-aiohttp_theme
BuildRequires:	python3-sphinxcontrib-asyncio
BuildRequires:	python3-sphinxcontrib-blockdiag
BuildRequires:	sphinx-pdg-3
%endif
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
BuildArch:	noarch

%description apidocs
API documentation for aiohttp.

%description apidocs -l pl.UTF-8
Dokumentacja API aiohttp.

%prep
%setup -q -n aiohttp-%{version}
%patch -P0 -p1

%{__sed} -i -e '1s,/usr/bin/env python3,%{__python3},' examples/*.py

%build
%py3_build

%if %{with tests}
# test_data_stream_exc_chain uses network
# test_mark_formdata_as_processed requires network
# test_client_session_timeout_zero fails on builders
# test_requote_redirect_url_default uses network
# test_unsupported_upgrade is marked as xfail, but succeeds
%{__mv} tests/test_proxy_functional.py{,.disabled} # needs proxy_py binary
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
PYTEST_PLUGINS="pytest_cov,pytest_mock,xdist" \
%{__python3} -m pytest tests -k 'not (test_data_stream_exc_chain or test_mark_formdata_as_processed or test_client_session_timeout_zero or test_requote_redirect_url_default or test_c_parser_loaded or test_unsupported_upgrade)'
%endif

%if %{with doc}
%{__make} -C docs html \
	SPHINXBUILD=sphinx-build-3 \
	SPHINXOPTS="-n"
%endif

%install
rm -rf $RPM_BUILD_ROOT

%py3_install

%{__rm} -r $RPM_BUILD_ROOT%{py3_sitedir}/aiohttp/.hash
%{__rm} $RPM_BUILD_ROOT%{py3_sitedir}/aiohttp/*.{pxd,pxi,pyx}

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
%{py3_sitedir}/aiohttp/py.typed
%{py3_sitedir}/aiohttp/__pycache__
%dir %{py3_sitedir}/aiohttp/_websocket
%attr(755,root,root) %{py3_sitedir}/aiohttp/_websocket/*.so
%{py3_sitedir}/aiohttp/_websocket/*.py
%{py3_sitedir}/aiohttp/_websocket/__pycache__
%{py3_sitedir}/aiohttp-%{version}-py*.egg-info
%{_examplesdir}/%{name}-%{version}

%if %{with doc}
%files apidocs
%defattr(644,root,root,755)
%doc docs/_build/html/*
%endif
