#!/bin/bash
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

# TODO TEST THIS SCRIPT !!!!!

if [ "$(whoami)" != "root" ]; then
    echo "You don't have sufficient privileges!"
    exit 1
fi

SCRIPT=$0
SYSTEM=$1
TO_MANY_ARGS=$2

function print_help() {
  echo "Usage: $SCRIPT <system>"
  echo ""
  echo "  <system> APT_SERVER|APT_DEV"
  echo ""
}

##### CHECK ARGUMENTS #####
if [ ! $SYSTEM ] ; then
  print_help
  exit 1
fi

if [ $TO_MANY_ARGS ] ; then
  echo "ERROR: To many arguments given!"
  print_help
  exit 1
fi

##### SERVER APT PACKAGES #####
if [ "$SYSTEM" == "APT_SERVER" ]; then
  apt-get -qy install apache2
  apt-get -qy install postgresql
  apt-get -qy install libapache2-mod-wsgi
  apt-get -qy install python-imaging
  apt-get -qy install python-psycopg2
fi

##### DEVELOPMENT APT PACKAGES #####
if [ "$SYSTEM" == "APT_DEV" ]; then
  apt-get -qy install python-docutils
  apt-get -qy install sqlite3
fi

##### COMMON APT PACKAGES #####
apt-get -qy install mercurial
apt-get -qy install python-pip
apt-get -qy install gettext
#apt-get -qy install bitcoind # to outdated!
#apt-get -qy install libssl-dev # needed?
apt-get -qy install python-dev # needed for Fuzzy

##### PYTHON PACKAGES #####
python setup.py develop

##### UPGRADE ALL #####
apt-get upgrade

# TODO setup server database

##### SETUP APACHE #####
if [ "$SYSTEM" == "APT_SERVER" ]; then
  cp www/config/apache/bitcoin-bounties.com_live /etc/apache2/sites-available/bitcoin-bounties.com_live
  cp www/config/apache/bitcoin-bounties.com_testing /etc/apache2/sites-available/bitcoin-bounties.com_testing
  cp www/config/apache/bitcoin-bounties.com_maintenance /etc/apache2/sites-available/bitcoin-bounties.com_maintenance
  cp www/config/apache/bitcoin-bounties.com_construction /etc/apache2/sites-available/bitcoin-bounties.com_construction
  ln -s /etc/apache2/sites-available/bitcoin-bounties.com_construction /etc/apache2/sites-enabled/bitcoin-bounties.com
  /etc/init.d/apache2 restart
fi

