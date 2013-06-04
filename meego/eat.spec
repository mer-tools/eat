Name: eat
Version: 0.2.0
# build.meego.com proposed patch > Release:7.1
Release:7.1
Summary: Test automation enabler meta packages
Group: Development/Tools
License: LGPL 2.1
URL: http://meego.com
Source0: %{name}-%{version}.tar.gz  
BuildRoot: mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-root

%description
Contains dependecies and packages for enabling automated testing

%build
# nothing to build

%package host
Summary: Host side enablers for test automation
Requires: openssh-clients
Requires: testrunner-lite
Requires(pre): coreutils
Conflicts: eat-device

%description host
Settings for host side of test automation. Includes ssh-key to enable passwordless root logins to device

%package selftest
Summary: Run test packages found in device
Requires: testrunner-lite

%description selftest
Automatically runs all test packages found in the device.
Test execution is start by eat-selftest.sh script and
results are written to user's home under testresults directory

%package device
Summary: Device side enablers for test automation
Requires: openssh-server
Requires(pre): coreutils
Conflicts: eat-host

%description device
Settings for device side of test automation. Includes ssh-key for passwordless root logins

%package syslog-device
Summary: Test automation syslog settings for device

%description syslog-device
Configures syslog to be sent to the host machine

%package syslog-host
Summary: Test automation syslog settings for the host machine

%description syslog-host
Configures host machines syslog to receive syslog from the device under test

%prep
%setup -q -n %{name}-%{version}

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p %{buildroot}/root/.ssh
cp src/sshkeys/authorized_keys2 %{buildroot}/root/.ssh/authorized_keys2
mkdir -p %{buildroot}/var/opt/eat/sshkey-host
cp src/sshkeys/id_eat_dsa %{buildroot}/var/opt/eat/sshkey-host/id_eat_dsa
cp src/sshkeys/config %{buildroot}/var/opt/eat/sshkey-host/config
cp src/sshkeys/authorized_keys2 %{buildroot}/var/opt/eat/sshkey-host/id_eat_dsa.pub
mkdir -p %{buildroot}/etc/init.d
cp src/init/eat-syslog-host %{buildroot}/etc/init.d/eat-syslog-host
cp src/init/eat-syslog-device %{buildroot}/etc/init.d/eat-syslog-device
mkdir -p %{buildroot}/usr/bin
cp src/scripts/eat-clear-syslog.sh %{buildroot}/usr/bin/eat-clear-syslog.sh
cp src/scripts/eat-selftest.sh %{buildroot}/usr/bin/eat-selftest.sh
cp src/scripts/install-eat-key.sh %{buildroot}/usr/bin/install-eat-key.sh
cp src/scripts/remove-eat-key.sh %{buildroot}/usr/bin/remove-eat-key.sh
%ifarch %{arm}
cp src/init/eat-dns %{buildroot}/etc/init.d/eat-dns
mkdir -p %{buildroot}/etc/profile.d
cp src/scripts/eat-env.sh  %{buildroot}/etc/profile.d/eat-env.sh
mkdir -p %{buildroot}/etc/dbus-1
cp src/conf/session-local.conf %{buildroot}/etc/dbus-1/session-local.conf
%endif
%ifarch %{ix86}
cp src/init/usbnetworking %{buildroot}/etc/init.d/usbnetworking
%endif

%files selftest
%defattr(755,root,root,-)
%{_bindir}/eat-selftest.sh

%post selftest
cp /etc/inittab /etc/inittab.back
echo "ea:5:once:su - meego -c \"eat-selftest.sh 120\"" >> /etc/inittab

%postun selftest
mv /etc/inittab.back /etc/inittab

%clean
rm -rf %{buildroot}

%files syslog-device
%defattr(-,root,root,-)
/etc/init.d/eat-syslog-device

%post syslog-device
# enable configuration
/etc/init.d/eat-syslog-device start

%files syslog-host
%defattr(-,root,root,-)
/etc/init.d/eat-syslog-host

%post syslog-host
# enable configuration
/etc/init.d/eat-syslog-host start


%files host
%defattr(660,root,root,-)
%config /var/opt/eat/sshkey-host/id_eat_dsa
%config /var/opt/eat/sshkey-host/config
%config /var/opt/eat/sshkey-host/id_eat_dsa.pub
%defattr(755,root,root,-)
%{_bindir}/eat-clear-syslog.sh
%{_bindir}/install-eat-key.sh
%{_bindir}/remove-eat-key.sh

%post host
# If home path is something else than /root
if [ "$HOME" != "/root" ]; then
	# Yes we're messing with the user's home directory
	mkdir -p ~/.ssh
	cat /var/opt/eat/sshkey-host/id_eat_dsa > ~/.ssh/id_eat_dsa
	cat /var/opt/eat/sshkey-host/id_eat_dsa.pub > ~/.ssh/id_eat_dsa.pub
	chmod 600 ~/.ssh/id_eat_dsa
	if [ -e ~/.ssh/config ]; then
		cp ~/.ssh/config ~/.ssh/config.backup
	fi
	cp /var/opt/eat/sshkey-host/config ~/.ssh 
	OWNER=`echo ~ | sed 's/\/home\///'`
	chown $OWNER:$OWNER ~/.ssh/id_eat_dsa
	chown $OWNER:$OWNER ~/.ssh/config
fi
# And we're messing also with root's home
mkdir -p /root/.ssh
cat /var/opt/eat/sshkey-host/id_eat_dsa > /root/.ssh/id_eat_dsa
cat /var/opt/eat/sshkey-host/id_eat_dsa.pub > /root/.ssh/id_eat_dsa.pub
chmod 600 /root/.ssh/id_eat_dsa
cp /var/opt/eat/sshkey-host/config /root/.ssh/ 

%postun host
# Again messing with the users home on purpose
if [ -e ~/.ssh/config ]; then
	rm ~/.ssh/config
	if [ -e ~/.ssh/config.backup ]; then
		mv ~/.ssh/config.backup ~/.ssh/config
	fi
fi
if [ -e ~/.ssh/id_eat_dsa ]; then
	rm ~/.ssh/id_eat_dsa*
fi
if [ -e /root/.ssh/config ]; then
	rm /root/.ssh/config
fi
if [ -e /root/.ssh/id_eat_dsa ]; then
	rm /root/.ssh/id_eat_dsa*
fi

%files device
%defattr(660,root,root,-)
# Yes, we're installing a ssh-key to root's home.
/root/.ssh/authorized_keys2
%defattr(-,root,root,-)
%ifarch %{arm}
/etc/init.d/eat-dns
/etc/profile.d/eat-env.sh
/etc/dbus-1/session-local.conf
%endif
%ifarch %{ix86}
/etc/init.d/usbnetworking
%endif

%post device
if [ -e /root/.ssh/authorized_keys ]
then
	cp /root/.ssh/authorized_keys /root/authorized_keys.back
fi
cat /root/.ssh/authorized_keys2 >> /root/.ssh/authorized_keys

# increase sshd startups
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
echo "#Added by eat" >> /etc/ssh/sshd_config
echo "MaxStartUps 1024" >> /etc/ssh/sshd_config

%ifarch %{arm}
/etc/init.d/eat-dns start
%endif

%preun device
%ifarch %{ix86}
/etc/rc.d/init.d/usbnetworking stop > /dev/null 2>&1 || :
%endif

%postun device
if [ -e /etc/ssh/sshd_config.backup ]; then
	mv /etc/ssh/sshd_config.backup /etc/ssh/sshd_config
fi

if [ -e /root/.ssh/authorized_keys.back ]
then
	mv /root/.ssh/authorized_keys.back /root/.ssh/authorized_keys
else
	rm /root/.ssh/authorizes_keys
fi

if [ -e /etc/profile.d/eat-env.sh ]
then
    rm /etc/profile.d/eat-env.sh
fi

