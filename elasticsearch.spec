# TODO
# - register user
# - pldize initscript
Summary:	A distributed, highly available, RESTful search engine
Name:		elasticsearch
Version:	0.19.9
Release:	0.2
License:	Apache v2.0
Group:		Daemons
Source0:	https://github.com/downloads/elasticsearch/elasticsearch/%{name}-%{version}.tar.gz
# Source0-md5:	fbf1ca717239ee477f4742b47393b63f
Source1:	%{name}.init
Source2:	%{name}.logrotate
Source3:	config-logging.yml
Source4:	%{name}.sysconfig
Source5:	%{name}.tmpfiles
URL:		http://www.elasticsearch.com/
BuildRequires:	rpmbuild(macros) >= 1.228
Requires(post,preun):	/sbin/chkconfig
Requires:	java-jna >= 3.2.4
Requires:	java-log4j >= 1.2.14
Requires:	java-sigar >= 1.6.4
Requires:	java-snappy >= 1.0.4
Requires:	jpackage-utils
Requires:	jre
Requires:	rc-scripts
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
A distributed, highly available, RESTful search engine.

%prep
%setup -q

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{_javadir}/%{name}/bin
install -p bin/elasticsearch $RPM_BUILD_ROOT%{_javadir}/%{name}/bin
install -p bin/elasticsearch.in.sh $RPM_BUILD_ROOT%{_javadir}/%{name}/bin
install -p bin/plugin $RPM_BUILD_ROOT%{_javadir}/%{name}/bin

# libs
install -d $RPM_BUILD_ROOT%{_javadir}/%{name}/lib
install -p lib/%{name}-%{version}.jar $RPM_BUILD_ROOT%{_javadir}/%{name}/lib

# config
install -d $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
install config/elasticsearch.yml $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/logging.yml

# data
install -d $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}

# logs
install -d $RPM_BUILD_ROOT%{_localstatedir}/log/%{name}
install -D %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/%{name}

# plugins
install -d $RPM_BUILD_ROOT%{_javadir}/%{name}/plugins

# sysconfig and init
install -d $RPM_BUILD_ROOT/etc/{rc.d/init.d,sysconfig}
install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
cp -p %{SOURCE4} $RPM_BUILD_ROOT/etc/sysconfig/%{name}

install -d $RPM_BUILD_ROOT%{_localstatedir}/{run,lock/subsys}/%{name}

install -D %{SOURCE5} $RPM_BUILD_ROOT%{_sysconfdir}/tmpfiles.d/elasticsearch.conf

%clean
rm -rf $RPM_BUILD_ROOT

%pre
# create elasticsearch group
if ! getent group elasticsearch >/dev/null; then
	groupadd -r elasticsearch
fi

# create elasticsearch user
if ! getent passwd elasticsearch >/dev/null; then
	useradd -r -g elasticsearch -d %{_javadir}/%{name} \
		-s /sbin/nologin -c "You know, for search" elasticsearch
fi

%post
/sbin/chkconfig --add elasticsearch
%service -n elasticsearch restart

%preun
if [ $1 -eq 0 ]; then
	%service elasticsearch stop
	/sbin/chkconfig --del elasticsearch
fi

%files
%defattr(644,root,root,755)
%doc LICENSE.txt NOTICE.txt README.textile
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/%{name}
%{_sysconfdir}/tmpfiles.d/elasticsearch.conf
%attr(754,root,root) /etc/rc.d/init.d/%{name}

%dir %{_javadir}/%{name}
%{_javadir}/elasticsearch/bin/*
%{_javadir}/elasticsearch/lib/%{name}-%{version}.jar
%dir %{_javadir}/elasticsearch/plugins
%config(noreplace) %{_sysconfdir}/%{name}

%dir %{_javadir}/elasticsearch/bin
%dir %{_javadir}/elasticsearch/lib

%defattr(-,elasticsearch,elasticsearch,-)
%dir %{_localstatedir}/lib/%{name}
%{_localstatedir}/run/%{name}
%dir %{_localstatedir}/log/%{name}
