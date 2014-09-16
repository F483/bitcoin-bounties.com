#!/bin/bash

if [ -f /home/bitcoin_bounties/www/config/flags/emergencystop ]; then
  service apache2 stop
  bitcoin-cli stop
  # TODO stop counterpartyd
fi

