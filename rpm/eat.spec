Name: eat
Version: 0.2.0
# build.meego.com proposed patch > Release:7.1
Release: 8.1
Summary: Test automation enabler meta packages
Group: Development/Tools
License: LGPL 2.1
URL: https://github.com/mer-tools/eat
Source0: %{name}-%{version}.tar.gz  
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

%package device
Summary: Device side enablers for test automation
Requires: openssh-server
Requires: oneshot
Requires(pre): coreutils
Conflicts: eat-host

Requires(post): /usr/bin/getent, /bin/ln, /bin/touch, /bin/sed, /bin/grep, /etc/login.defs, /usr/bin/add-oneshot

%description device
Settings for device side of test automation. Includes ssh-key for passwordless root logins

%prep
%setup -q -n %{name}-%{version}

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p %{buildroot}/var/opt/eat/sshkey-device
cp src/sshkeys/authorized_keys2 %{buildroot}/var/opt/eat/sshkey-device/
mkdir -p %{buildroot}/var/opt/eat/sshkey-host
cp src/sshkeys/id_eat_dsa %{buildroot}/var/opt/eat/sshkey-host/id_eat_dsa
cp src/sshkeys/config %{buildroot}/var/opt/eat/sshkey-host/config
cp src/sshkeys/authorized_keys2 %{buildroot}/var/opt/eat/sshkey-host/id_eat_dsa.pub

mkdir -p %{buildroot}/etc/xdg/autostart/
cat > %{buildroot}/etc/xdg/autostart/eat-store-env.desktop << EOF
[Desktop Entry]
Exec=/usr/bin/eat-store-env
X-Moblin-Priority=High
EOF

mkdir -p %{buildroot}%{_libdir}/systemd/user
cat > %{buildroot}%{_libdir}/systemd/user/eat-store-env.service << EOF
[Unit]
Description=Store the environment to integrate into user session
After=xorg.target
Requires=dbus.socket xorg.target 
Type=oneshot

[Service]
ExecStart=/usr/bin/eat-store-env

EOF

mkdir -p %{buildroot}%{_libdir}/systemd/user/nemo-mobile-session.target.wants
ln -sf ../eat-store-env.service %{buildroot}%{_libdir}/systemd/user/nemo-mobile-session.target.wants/

mkdir -p %{buildroot}/usr/bin
cat > %{buildroot}/usr/bin/eat-store-env << EOF
#!/bin/sh
export | sed "s/^declare -x /export /g" > \$HOME/.eat-stored-env
EOF

chmod +x %{buildroot}/usr/bin/eat-store-env

cat > %{buildroot}/usr/bin/eat-add-device-key << EOF
#!/bin/sh
echo -n "Adding EAT ssh keys to authorized_keys for \$USER.."
if [ ! -d \$HOME/.ssh ]; then
	mkdir -p \$HOME/.ssh
	chmod go-rwx \$HOME/.ssh
fi

echo "" >> \$HOME/.ssh/authorized_keys
echo command=\"/usr/bin/eat-run-command\" \`cat /var/opt/eat/sshkey-device/authorized_keys2\` >> \$HOME/.ssh/authorized_keys
chmod go-rwx \$HOME/.ssh/authorized_keys
echo "done"
EOF

chmod +x %{buildroot}/usr/bin/eat-add-device-key

cat > %{buildroot}/usr/bin/eat-install-host-key << EOF
#!/bin/sh
echo -n "Installing EAT host private key into ~/.ssh for logging into devices.."
if [ ! -d \$HOME/.ssh ]; then
	mkdir -p \$HOME/.ssh
	chmod go-rwx \$HOME/.ssh
fi
cp /var/opt/eat/sshkey-host/id_eat_dsa \$HOME/.ssh
cp /var/opt/eat/sshkey-host/id_eat_dsa.pub \$HOME/.ssh
chmod go-rwx \$HOME/.ssh/id_eat_dsa
chmod go-rwx \$HOME/.ssh/id_eat_dsa.pub
echo "done"
EOF

chmod a+x %{buildroot}/usr/bin/eat-install-host-key

cat > %{buildroot}/usr/bin/eat-run-command << EOF
#!/bin/sh
if [ -z "\$SSH_ORIGINAL_COMMAND" ]; then
        # No command given, launch a login shell
	SSH_ORIGINAL_COMMAND="bash --login"
fi
if [ -e \$HOME/.eat-stored-env ]; then
   env -i sh -c ". \$HOME/.eat-stored-env; \$SSH_ORIGINAL_COMMAND"
else
   \$SSH_ORIGINAL_COMMAND
fi
EOF
chmod a+x %{buildroot}/usr/bin/eat-run-command

install -d %{buildroot}/%{_libdir}/oneshot.d
cat > %{buildroot}/%{_libdir}/oneshot.d/10-eat-device-key << EOF
#!/bin/sh
exec /usr/bin/eat-add-device-key
EOF
chmod a+x %{buildroot}/%{_libdir}/oneshot.d/10-eat-device-key

%clean
rm -rf %{buildroot}

%post
if [ "$1" -eq 1 ]; then
    %{_bindir}/add-oneshot 10-eat-device-key
    %{_bindir}/add-oneshot --user 10-eat-device-key
fi

%files host
%defattr(-,root,root,-)
%config /var/opt/eat/sshkey-host/id_eat_dsa
%config /var/opt/eat/sshkey-host/config
%config /var/opt/eat/sshkey-host/id_eat_dsa.pub
%dir /var/opt/eat
%dir /var/opt/eat/sshkey-host
/usr/bin/eat-install-host-key

%files device
%defattr(-,root,root,-)
/etc/xdg/autostart/eat-store-env.desktop
%{_libdir}/oneshot.d/10-eat-device-key
%{_libdir}/systemd/user/eat-store-env.service
%{_libdir}/systemd/user/nemo-mobile-session.target.wants/eat-store-env.service
/var/opt/eat/sshkey-device
/usr/bin/eat-add-device-key
/usr/bin/eat-store-env
/usr/bin/eat-run-command
%dir /var/opt/eat
