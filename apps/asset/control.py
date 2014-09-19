# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

import os
import json
import requests
import bitcoinaddress
from decimal import Decimal, ROUND_DOWN
from requests.auth import HTTPBasicAuth
from bitcoinrpc.authproxy import AuthServiceProxy
from config import settings
from apps.common.utils.misc import chunks, fraction
from apps.userfund.models import UserFund
from apps.asset.models import PaymentLog, ColdStorage
from apps.asset.managers.bitcoin import BitcoinManager
from apps.asset.managers.counterparty import CounterpartyManager
from apps.asset.managers.counterparty import get_asset_names

_ASSETS = {}

def _assets():
  if _ASSETS:
    return _ASSETS
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
  # counterparty assets (always after BTC because of emergencystop)
  counterparty_assets = get_asset_names()
  for ca in counterparty_assets:
    assets[ca] = CounterpartyManager(key=ca, label='Counterparty %s' % ca)
  _ASSETS.update(assets)
  return _ASSETS

def get_manager(asset):
  return _assets()[asset]

def get_choices():
  choices = map(lambda item: (item[0], item[1].label), _assets().items())
  return sorted(choices, key=lambda c: c[1])

def get_hotwallet(asset):
  am = get_manager(asset)
  balances = am.get_address_balances()
  return map(lambda b: { "address" : b[0], "amount" : b[1] }, balances)

def details(asset):
  am = get_manager(asset)

  # coldstorages
  coldstorages = ColdStorage.objects.filter(asset=asset)
  coldstorages = filter(lambda cs: cs.imported == False, coldstorages)

  # userfunds
  userfunds = UserFund.objects.select_related('bounty') # join bounty
  userfunds = userfunds.filter(bounty__asset=asset)
  
  # funds
  funds_hot = am.get_wallet_balance()
  funds_cold = Decimal(sum(map(lambda cs: cs.amount, coldstorages)))
  funds_total = funds_hot + funds_cold
  funds_users = Decimal(sum(map(lambda uf: uf.bound_funds, userfunds)))
  funds_company = funds_total - funds_users

  result = {
    "asset" : asset,
    "label" : am.label,
    "funds_hot" : funds_hot,
    "funds_cold" : funds_cold,
    "funds_users" : funds_users,
    "funds_company" : funds_company,
    "funds_hot_fraction" : fraction(funds_hot, funds_total),
    "funds_cold_fraction" : fraction(funds_cold, funds_total),
    "funds_users_fraction" : fraction(funds_users, funds_total),
    "funds_company_fraction" : fraction(funds_company, funds_total),
    "funds_total" : funds_total,
    "coldstorages" : coldstorages,
  }
  return result

def overview():
  assets = map(lambda a: details(a[0]), _assets().items())
  assets = sorted(assets, key=lambda a: a["label"])
  assets = filter(lambda a: a["funds_total"] > Decimal("0.0"), assets)
  return chunks(assets, 2)

def cold_storage_add(user, asset, address):
  cs = ColdStorage()
  cs.asset = asset
  cs.address = address
  cs.created_by = user
  cs.updated_by = user
  cs.save()
  return cs

def cold_storage_send(asset, amount):
  am = get_manager(asset)

  # get cold storage
  coldstorages = ColdStorage.objects.filter(asset=asset)
  coldstorages = filter(lambda cs: cs.imported == False, coldstorages)
  if len(coldstorages) == 0:
    raise Exception("No cold storage wallet!")
  coldstorage = sorted(coldstorages, key=lambda cs: cs.amount)[0]

  # send to cold storage
  logs = am.send([{ "destination" : coldstorage.address, "amount" : amount }])
  coldstorage.payments.add(logs[coldstorage.address])

  return coldstorage

def cold_storage_import(asset, private_key):
  am = get_manager(asset)
  am.import_private_key(private_key)

def emergencystop():

  # set stop_crons flag
  with open(settings.STOP_CRONS_FILE, 'a'):
    os.utime(settings.STOP_CRONS_FILE, None)

  # set emergencystop flag
  with open(settings.EMERGENCY_STOP_FILE, 'a'):
    os.utime(settings.EMERGENCY_STOP_FILE, None)

