#
# Conditional build:
%bcond_without	doc		# API documentation
%bcond_without	tests		# unit tests (note: spawn hundreds of threads, opens >1k descriptors)
%bcond_with	benchmark	# benchmark tests

%define		module	template
Summary:	Async http client/server framework
Summary(pl.UTF-8):	Szkielet asynchronicznego klienta/serwera http
Name:		python3-aiohttp
Version:	3.14.5
Release:	2
License:	Apache v2.0, MIT
Group:		Libraries/Python
#Source0Download: https://pypi.org/simple/aiohttp/
Source0:	https://files.pythonhosted.org/packages/source/a/aiohttp/aiohttp-%{version}.tar.gz
# Source0-md5:	c31a05528821715778ebe0e56374c4dc
Patch0:		disable-towncrier.patch
Patch1:		docs-no-mermaid.patch
URL:		https://pypi.org/project/aiohttp/
BuildRequires:	llhttp-devel >= 9.3.0
BuildRequires:	python3-Cython >= 3.2.5
BuildRequires:	python3-devel >= 1:3.10
BuildRequires:	python3-pkgconfig
BuildRequires:	python3-setuptools >= 1:77.0
%if %{with tests}
BuildRequires:	python3-aiodns >= 3.3.0
BuildRequires:	python3-aiohappyeyeballs >= 2.5.0
BuildRequires:	python3-aiosignal >= 1.4.0
%if "%{_ver_lt %{py3_ver} 3.11}" == "1"
BuildRequires:	python3-async_timeout >= 4.0
BuildRequires:	python3-async_timeout < 6
%endif
BuildRequires:	python3-attrs >= 17.3.0
%if "%{py3_ver}" != "3.14"
BuildRequires:	python3-backports.zstd
%endif
BuildRequires:	python3-blockbuster
BuildRequires:	python3-brotli >= 1.2
BuildRequires:	python3-freezegun
BuildRequires:	python3-frozenlist >= 1.1.1
BuildRequires:	python3-gunicorn
BuildRequires:	python3-isal
BuildRequires:	python3-multidict >= 4.5
BuildRequires:	python3-multidict < 8
BuildRequires:	python3-propcache >= 0.2.0
# for test_proxy_functional
#BuildRequires:	python3-proxy.py >= 2.4.4rc5
BuildRequires:	python3-pytest >= 3.8.2
BuildRequires:	python3-pytest-cov
BuildRequires:	python3-pytest-mock
BuildRequires:	python3-pytest-timeout
BuildRequires:	python3-pytest-xdist
BuildRequires:	python3-pytest_codspeed
# for tests/autobahn (with Docker)
#BuildRequires:	python3-python-on-whales
BuildRequires:	python3-re_assert
BuildRequires:	python3-setuptools_git
BuildRequires:	python3-trustme
BuildRequires:	python3-uvloop
# for tests/autobahn
#BuildRequires:	python3-wait-for-it
BuildRequires:	python3-yarl >= 1.25.1
BuildRequires:	python3-yarl < 2
BuildRequires:	python3-zlib-ng
%endif
BuildRequires:	rpm-build >= 4.6
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.749
BuildRequires:	sed >= 4.0
%if %{with doc}
BuildRequires:	python3-aiohttp_theme
BuildRequires:	python3-myst_parser
BuildRequires:	python3-sphinx_issues
BuildRequires:	sphinx-pdg-3
%endif
%if %{with benchmark}
# causes pytest_codspeed to disable some functionality
BuildConflicts:	python3-pytest-benchmark
%endif
Requires:	python3-modules >= 1:3.10
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
%patch -P1 -p1

%{__sed} -i -e '1s,/usr/bin/env python3,%{__python3},' examples/*.py

%build
export AIOHTTP_USE_SYSTEM_DEPS=1
%py3_build

%if %{with tests}
# tests/autobahn use docker
# test_data_stream_exc_chain uses network
# test_mark_formdata_as_processed requires network
# test_client_session_timeout_zero fails on builders
# test_requote_redirect_url_default uses network
# test_unsupported_upgrade is marked as xfail, but succeeds
# test_tcp_connector_ssl_shutdown_timeout_passed_to_create_connection requires network
# test_tcp_connector_ssl_shutdown_timeout_zero_not_passed requires network
# test_tcp_connector_ssl_shutdown_timeout_nonzero_passed requires network
# test_websocket_connection_cancellation hangs
# test_access_mock_special_resource timeouts
# test_no_warnings doesn't pass -P to subprocess
# disable parallelism because too many threads/sockets are used
%{__mv} tests/test_proxy_functional.py{,.disabled} # needs proxy.py module
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
PYTEST_PLUGINS="pytest_codspeed.plugin,pytest_cov,pytest_mock,pytest_timeout,xdist" \
PYTHONPATH=$(readlink -f build-3/lib.*) \
%{__python3} -P -m pytest tests \
	--numprocesses=0 \
	--ignore tests/autobahn \
%if %{without benchmark}
	--ignore tests/test_benchmarks_client.py \
	--ignore tests/test_benchmarks_client_request.py \
	--ignore tests/test_benchmarks_client_response.py \
	--ignore tests/test_benchmarks_client_ws.py \
	--ignore tests/test_benchmarks_cookie_helpers.py \
	--ignore tests/test_benchmarks_cookiejar.py \
	--ignore tests/test_benchmarks_http_websocket.py \
	--ignore tests/test_benchmarks_http_writer.py \
	--ignore tests/test_benchmarks_multipart.py \
	--ignore tests/test_benchmarks_web_fileresponse.py \
	--ignore tests/test_benchmarks_web_middleware.py \
	--ignore tests/test_benchmarks_web_request.py \
	--ignore tests/test_benchmarks_web_response.py \
	--ignore tests/test_benchmarks_web_urldispatcher.py \
%endif
	-k 'not (test_data_stream_exc_chain or test_mark_formdata_as_processed or test_client_session_timeout_zero or test_requote_redirect_url_default or test_unsupported_upgrade or test_tcp_connector_ssl_shutdown_timeout_passed_to_create_connection or test_tcp_connector_ssl_shutdown_timeout_zero_not_passed or test_tcp_connector_ssl_shutdown_timeout_nonzero_passed or test_websocket_connection_cancellation or test_access_mock_special_resource or test_no_warnings)'
%endif

%if %{with doc}
PYTHONPATH=$(pwd) \
%{__make} -C docs html \
	SPHINXBUILD=sphinx-build-3 \
	SPHINXOPTS="-n"
%endif

%install
rm -rf $RPM_BUILD_ROOT

export AIOHTTP_USE_SYSTEM_DEPS=1
%py3_install

%{__rm} $RPM_BUILD_ROOT%{py3_sitedir}/aiohttp/*.{pxd,pxi,pyx}
%{__rm} $RPM_BUILD_ROOT%{py3_sitedir}/aiohttp/_websocket/*.{pxd,pyx}

install -d $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}
cp -pr examples/* $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc CHANGES.rst CONTRIBUTORS.txt LICENSE.txt README.rst
%dir %{py3_sitedir}/aiohttp
%{py3_sitedir}/aiohttp/*.so
%{py3_sitedir}/aiohttp/*.py
%{py3_sitedir}/aiohttp/py.typed
%{py3_sitedir}/aiohttp/__pycache__
%dir %{py3_sitedir}/aiohttp/_websocket
%{py3_sitedir}/aiohttp/_websocket/*.so
%{py3_sitedir}/aiohttp/_websocket/*.py
%{py3_sitedir}/aiohttp/_websocket/__pycache__
%{py3_sitedir}/aiohttp-%{version}-py*.egg-info
%{_examplesdir}/%{name}-%{version}

%if %{with doc}
%files apidocs
%defattr(644,root,root,755)
%doc docs/_build/html/{_images,_modules,_static,*.html,*.js}
%endif
