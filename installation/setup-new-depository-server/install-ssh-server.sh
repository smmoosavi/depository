#!/bin/bash

if dpkg -l | grep openssh-server; then
	echo "openssh-server has been installed."
else
	sudo apt-get update
	sudo apt-get install -y openssh-server
fi

SSH_SERVER_CONFIG_PATH="/etc/ssh/sshd_config"
SSH_SERVER_CONFIG_BACKUP_PATH="$SSH_SERVER_CONFIG_PATH.back"

if [ ! -f $SSH_SERVER_CONFIG_PATH ]; then
	echo "$SSH_SERVER_CONFIG_PATH  does not exist"
	exit -1
fi

if test -f $SSH_SERVER_CONFIG_BACKUP_PATH; then
	echo "Restore ssh-server config to default valus..."
	sudo cp $SSH_SERVER_CONFIG_BACKUP_PATH $SSH_SERVER_CONFIG_PATH
else
	echo "Create backup from ssh-server config..."
	sudo cp $SSH_SERVER_CONFIG_PATH $SSH_SERVER_CONFIG_BACKUP_PATH
fi

sudo sed "s/^#PasswordAuthentication.*/PasswordAuthentication no/"  -i $SSH_SERVER_CONFIG_PATH

sudo service ssh restart

mkdir -p ~/.ssh
cp authorized_keys ~/.ssh/authorized_keys

sudo mkdir -p /root/.ssh
sudo cp authorized_keys /root/.ssh/authorized_keys
