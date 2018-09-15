#!/bin/bash

## Changed to directory and clone
cd /opt/ 
git clone https://github.com/bammv/sguil.git

## stop sguil
so-sguild-stop

## create backups 
mkdir /opt/sguil_bak
tar zcvf /opt/sguil_bak/lib.bak.tgz /usr/lib/sguild/ 
tar zcvf /opt/sguil_bak/sguild.tgz /usr/bin/sguild

## copy the library 
rsync -avh /opt/sguil/server/lib/* /usr/lib/sguild/

## copy sguild
cp /opt/sguil/server/sguild /usr/bin/sguild

## edit sguil.conf
printf "set HTTPS 1\n" >> /etc/sguild/sguild.conf
printf "set HTTPS_PORT 4433\n" >> /etc/sguild/sguild.conf
printf "set HTML_PATH {/opt/sguil/server/html}\n" >> /etc/sguild/sguild.conf

## edit sguild 
sed -i 's/cert.pem/wcert.pem/g' /usr/bin/sguild
sed -i 's/privkey.pem/wprivkey.pem/g' /usr/bin/sguild


## create the certs
openssl req -newkey rsa:2048 -new -nodes -x509 -days 3650 -keyout /etc/sguild/certs/wprivkey.pem -out /etc/sguild/certs/wcert.pem


## start sguil
so-sguild-start





