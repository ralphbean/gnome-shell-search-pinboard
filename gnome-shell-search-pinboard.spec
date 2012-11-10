%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?pyver: %global pyver %(%{__python} -c "import sys ; print sys.version[:3]")}

%global modname gs_search_pinboard
%global busname org.gnome.pinboard.search

Name:           gnome-shell-search-pinboard
Version:        1.0.0
Release:        1%{?dist}
Summary:        Search your pinboard.in account from the gnome-shell

License:        GPLv3+
URL:            https://github.com/ralphbean/%{name}
Source0:        https://pypi.python.org/packages/source/g/%{name}/%{name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python2-devel
BuildRequires:  python-setuptools-devel
BuildRequires:  pygobject3

Requires:       gnome-shell
Requires:       pygobject3
Requires:       python-requests
Requires:       python-keyring
Requires:       python-beautifulsoup4

%description
gnome-shell-search-pinboard includes results from your pinboard.in
account in gnome-shell search results.

%prep
%setup -q

%build
%{__python} setup.py build

%install
%{__python} setup.py install -O1 --skip-build \
    --install-data=%{_datadir} --root %{buildroot}

# Glade file
mkdir -p %{buildroot}%{_datadir}/gnome-shell-search-pinboard/
install -m 0644 data/popup.glade %{buildroot}%{_datadir}/gnome-shell-search-pinboard/popup.glade

# Search provider definition
mkdir -p %{buildroot}%{_datadir}/gnome-shell/search-providers
install -m 0644 conf/%{busname}.ini %{buildroot}%{_datadir}/gnome-shell/search-providers/

# DBus configuration
mkdir -p %{buildroot}%{_datadir}/dbus-1/services/
install -m 0644 conf/%{busname}.service \
    %{buildroot}%{_datadir}/dbus-1/services/%{busname}.service
mkdir -p %{buildroot}%{_sysconfdir}/dbus-1/system.d
install -m 0644 conf/%{busname}.conf \
    %{buildroot}%{_sysconfdir}/dbus-1/system.d/%{busname}.conf

# GSettings schema
mkdir -p %{buildroot}%{_datadir}/glib-2.0/schemas
install -m 0644 conf/%{busname}.gschema.xml %{buildroot}%{_datadir}/glib-2.0/schemas

%postun
if [ $1 -eq 0 ]; then
    glib-compile-schemas %{_datadir}/glib-2.0/schemas &> /dev/null || :
fi

%posttrans
glib-compile-schemas %{_datadir}/glib-2.0/schemas &> /dev/null || :


%files
%doc README.rst LICENSE
%{_bindir}/%{name}-daemon
%{_bindir}/%{name}-config

%{python_sitelib}/%{modname}/
%{python_sitelib}/gnome_shell_search_pinboard-%{version}-py%{pyver}.egg-info/

%{_datadir}/gnome-shell-search-pinboard/popup.glade
%{_datadir}/gnome-shell/search-providers/%{busname}.ini
%{_datadir}/dbus-1/services/%{busname}.service
%{_sysconfdir}/dbus-1/system.d/%{busname}.conf
%{_datadir}/glib-2.0/schemas/%{busname}.gschema.xml


%changelog
* Sat Nov 10 2012 Ralph Bean <rbean@redhat.com> - 1.0.0-1
- Full rewrite.  Fork from gnome-shell-search-github-repositories.
