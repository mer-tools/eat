#!/bin/sh

if [ $((`id -u`)) = "0" ]; then
	echo "Please do not run this as root"
	exit 1
fi

EATKEY=/var/opt/eat/sshkey-host/id_eat_dsa
EATCONFIG=/var/opt/eat/sshkey-host/config

if [ -e ~/.ssh/id_eat_dsa ]; then
	echo "eat ssh-key already installed for $USER"
	exit 1
fi

if [ ! -e "$EATKEY" ] || [ ! -e "$EATCONFIG" ]; then
	echo Error: $EATKEY or $EATCONFIG missing.
	exit 1
fi

echo "Installing eat ssh-key for $USER. To remove it run remove-eat-key.sh"

if [ ! -d ~/.ssh ]; then
        mkdir -p ~/.ssh
fi

cat $EATKEY > ~/.ssh/id_eat_dsa
chmod 600 ~/.ssh/id_eat_dsa
cat $EATKEY.pub > ~/.ssh/id_eat_dsa.pub
chmod 600 ~/.ssh/id_eat_dsa.pub

if [ -e ~/.ssh/config ]; then
        cp ~/.ssh/config ~/.ssh/config.backup
fi

cp $EATCONFIG ~/.ssh/
chown $USER:$USER ~/.ssh/id_eat_dsa
chown $USER:$USER ~/.ssh/id_eat_dsa.pub
chown $USER:$USER ~/.ssh/config

echo "done"
exit $?

