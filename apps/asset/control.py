# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

import json
import requests
import bitcoinaddress
from decimal import Decimal, ROUND_DOWN
from requests.auth import HTTPBasicAuth
from bitcoinrpc.authproxy import AuthServiceProxy
from config import settings
from apps.asset.models import PaymentLog
from apps.asset.managers.bitcoin import BitcoinManager
from apps.asset.managers.counterparty import CounterpartyManager
from apps.asset.managers.counterparty import counterpartyd_querry

def _assets():
  assets = {
    'BTC' : BitcoinManager(),
    # TODO 'LTC' : LitecoinManager(),
    # TODO 'BTSX' : BitSharesXManager(),
    # TODO 'NXT' : NXTManager(),
    # TODO 'PPC' : PeercoinManager(),
    # TODO 'DOGE' : DogecoinManager(),
    # TODO 'NMC' : NamecoinManager(),
    # TODO 'DRK' : DarkcoinManager(),
    # TODO 'MAID' : MaidSafeCoinManager(),
    # TODO 'XMR' :  MoneroManager(),
    # TODO 'BTCD' :  BitcoinDarkManager(),
  }
  counterparty_assets = [u'XCP'] + counterpartyd_querry({
    "method": "get_asset_names",
    "jsonrpc": "2.0",
    "id": 0,
  })['result']
  for ca in counterparty_assets:
    assets[ca] = CounterpartyManager(key=ca, label='Counterparty %s' % ca)
  return assets

ASSETS = _assets()

def get_manager(asset):
  return ASSETS[asset]

def get_choices():
  choices = map(lambda item: (item[0], item[1].label), ASSETS.items())
  return sorted(choices, key=lambda c: c[1])

