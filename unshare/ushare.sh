#!/bin/bash

ROTFS=$PWD/unshare-container3
ulimit -S -c unlimited

if [ ! -d $ROTFS ]; then
	mkdir -p $ROTFS/{bin,proc,var/www,var/log,etc}
	cd $ROTFS/bin/
	cp /bin/busybox .
	for P in $(./busybox --list); do ln -s busybox $P; done;
	cp /usr/local/bin/dumb-init .
	cd $ROTFS/etc/
	cp /etc/mime.types .
	cd $ROTFS/var/www
	cp $ROTFS/../www/* .
fi

cd $ROTFS/bin
rm cont_prog*
cp ../../cont_prog .

cd $ROTFS/..
sudo PATH=/bin unshare --fork --pid /usr/sbin/chroot unshare-container3/ /bin/dumb-init cont_prog 
