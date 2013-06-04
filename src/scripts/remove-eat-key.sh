#!/bin/sh

if [ $((`id -u`)) = "0" ]; then
	echo "please do not run this as root"
	exit 1
fi

if [ -e ~/.ssh/id_eat_dsa ]; then
	echo "removing eat ssh-key from $USER"
        rm ~/.ssh/id_eat_dsa*

	if [ -e ~/.ssh/config.backup ]; then
		mv ~/.ssh/config.backup ~/.ssh/config
	fi
else
	echo "eat key not installed for $USER"
fi

exit $?

