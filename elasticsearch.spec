# TODO
# - register user
# - pldize initscript
# - system jars:
#   jts-1.12.jar
#   lucene-*-3.6.2.jar
#   spatial4j-0.3.jar
Summary:	A distributed, highly available, RESTful search engine
Name:		elasticsearch
Version:	0.20.2
Release:	0.1
License:	Apache v2.0
Group:		Daemons
Source0:	https://download.elasticsearch.org/elasticsearch/elasticsearch/%{name}-%{version}.tar.gz
# Source0-md5:	fe50d6f4b11e9e0d1ccf661b32f15fbc
Source1:	%{name}.init
Source2:	%{name}.logrotate
Source3:	config-logging.yml
Source4:	%{name}.sysconfig
Source5:	%{name}.tmpfiles
URL:		http://www.elasticsearch.org/
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

rm lib/jna-3.3.0.jar
rm lib/log4j-1.2.17.jar
rm lib/snappy-java-1.0.4.1.jar
rm -r lib/sigar/

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{_javadir}/%{name}/bin
install -p bin/elasticsearch $RPM_BUILD_ROOT%{_javadir}/%{name}/bin
install -p bin/elasticsearch.in.sh $RPM_BUILD_ROOT%{_javadir}/%{name}/bin
install -p bin/plugin $RPM_BUILD_ROOT%{_javadir}/%{name}/bin

# libs
install -d $RPM_BUILD_ROOT%{_javadir}/%{name}/lib
cp -a lib/* $RPM_BUILD_ROOT%{_javadir}/%{name}/lib

# config
install -d $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
cp -p config/elasticsearch.yml $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
cp -p %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/logging.yml

# data
install -d $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}

# logs
install -d $RPM_BUILD_ROOT%{_localstatedir}/log/%{name}
install -Dp %{SOURCE2} $RPM_BUILD_ROOT/etc/logrotate.d/%{name}

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
/sbin/chkconfig --add %{name}
%service -n %{name} restart

%preun
if [ $1 -eq 0 ]; then
	/sbin/chkconfig --del %{name}
	%service %{name} stop
fi

%files
%defattr(644,root,root,755)
%doc LICENSE.txt NOTICE.txt README.textile
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/%{name}
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%{_sysconfdir}/tmpfiles.d/elasticsearch.conf

%dir %{_javadir}/%{name}

%dir %{_javadir}/%{name}/bin
%attr(755,root,root) %{_javadir}/%{name}/bin/elasticsearch
%attr(755,root,root) %{_javadir}/%{name}/bin/elasticsearch.in.sh
%attr(755,root,root) %{_javadir}/%{name}/bin/plugin

%dir %{_javadir}/%{name}/lib
%{_javadir}/%{name}/lib/%{name}-%{version}.jar
%{_javadir}/%{name}/lib/jts-1.12.jar
%{_javadir}/%{name}/lib/spatial4j-0.3.jar
%{_javadir}/%{name}/lib/lucene-analyzers-3.6.2.jar
%{_javadir}/%{name}/lib/lucene-core-3.6.2.jar
%{_javadir}/%{name}/lib/lucene-highlighter-3.6.2.jar
%{_javadir}/%{name}/lib/lucene-memory-3.6.2.jar
%{_javadir}/%{name}/lib/lucene-queries-3.6.2.jar

%dir %{_javadir}/%{name}/plugins

%defattr(-,elasticsearch,elasticsearch,-)
%dir %{_localstatedir}/lib/%{name}
%{_localstatedir}/run/%{name}
%dir %{_localstatedir}/log/%{name}
