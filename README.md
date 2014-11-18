# bitcoin-bounties.com

Bitcoin Bounties is a site where anyone can easily post, fund or claim rewards with bitcoin.

# Installation for development

bitcoin-bounties.com is made with python/django.

### Dependencies for Ubuntu

    # install apt packages
    sudo apt-get -qy install apache2 postgresql libapache2-mod-wsgi # only for server
    sudo apt-get -qy install gettext python2.7-dev

### Project Setup

    # Clone repository
    cd where/you/keep/your/repos
    git clone https://github.com/F483/bitcoin-bounties.com
    cd bitcoin-bounties.com

    # python virtualenv
    virtualenv -p /usr/bin/python2 env  # create virtualenv
    source env/bin/activate             # activate virtualenv

    # Install python packages
    python setup.py develop

