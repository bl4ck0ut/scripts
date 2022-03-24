#!/bin/bash
#: Title       : Silent Kali Setup
#: Date Created: Wed 03.23.2022
#: Author      : Charley Pfaff
#: Description : Very basic script to setup the latest kali 2022.1 since it is missing a few things
#
# --------------------------------------------------------------
#
# This script is the primary api file that will write out data based on 
# a query that is selected. This data can be used to query or grep against
# or used to be called with parameters.
# 
# requirnemts:
# Latest Kali at the time 2022.1
# 
# 
# example usage: 
# chmod 777 silentshell.sh
# ./silentshell.sh
#
# What this does is:
# 1.pulls the latest silentbridge
# 2.installs python 2.7 with pip
# 3.installs bridge-essentials
# 4. echo's usages of silentbridge
# -----------------------------------------------------------------------
#
# improvments
# 
# - Where do I start variables for interfaces
# - variables for locations for compiling tools
# - better error handling and logging
# 
#
# --------------------------------------------------------------
# ChangeLog
# - Located in git history
# --------------------------------------------------------------
sudo apt update
sudo apt upgrade
sudo apt install autoconf

echo which interface do you want to connect to the wall
read WALL_ETH

echo which interface do you want to connect to the computer
read COMP_ETH

echo which interface do you want to use for your comms
read COMMS_ETH


#setup silentbridge on Kali
mkdir ~/silentbridge
cd ~/silentbridge
git clone https://github.com/s0lst1c3/silentbridge.git
cd silentbridge
sudo python2.7 ./quick-setup


#setup and install python 2.7 for silentbrige dependencies
cd ~
mkdir tmp
cd tmp
wget https://www.python.org/ftp/python/2.7.15/Python-2.7.15.tgz
tar zxvf Python-2.7.15.tgz 
cd Python-2.7.15 
./configure --prefix=$HOME/opt/python-2.7.15 --with-ensurepip=install
make
make install


#setup Path for execution by 
export PATH=/home/kali/opt/python-2.7.15/bin:$PATH
python --version
pip --version


pip install scapy
pip install nanpy
pip install netifaces


#setup and install bridge utils since this is not included in Kali 2022 anymore
cd ~/tmp
wget https://www.kernel.org/pub/linux/utils/net/bridge-utils/bridge-utils-1.6.tar.xz
7z e bridge-utils-1.6.tar.xz
tar xvf bridge-utils-1.6.tar
cd bridge-utils-1.6
#sudo automake
autoconf
#sudo autoupdate
#sudo autoconf
./configure --prefix=/usr 
make
sudo make install 

#sudo and execute silentbridge

echo "export PATH=/home/kali/opt/python-2.7.15/bin:$PATH"

echo "cd /home/kali/silentbridge/silentbridge"

echo "python ./silentbridge --create-bridge --upstream $WALL_ETH --phy $COMP_ETH --sidechannel $COMMS_ETH"

echo "To destroy the bridge ./silentbridge --destroy-bridge"




