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

def _sum_key(dictonary, key, move_decimal=0):
  value = sum(map(lambda x: Decimal(x[key]), dictonary))
  value = value / (Decimal("10.0") ** move_decimal)
  return value and value or Decimal("0.0")

class AssetManager(object):

  def __init__(self, key=None, label=None, decimal_places=None):
    assert(key)
    assert(type(decimal_places) == type(1) and decimal_places >= 0)
    self.key = key
    self.label = label and label or key
    self.decimal_places = decimal_places

  def quantize(self, amount):
    atom = Decimal("1.0") / (Decimal("10.0") ** self.decimal_places)
    return amount.quantize(atom, rounding=ROUND_DOWN)

  def get_balance(self, address):
    raise NotImplementedError

  def get_wallet_balance(self):
    raise NotImplementedError

  def get_received(self, address):
    raise NotImplementedError

  def get_receives(self, address):
    """ Get a list of transactions where this address received assets.

    Returns: [
      { 
        "txid" : txid, 
        "address" : address,
        "amount" : amount, 
        "timereceived" : unixtime,
        "confirmations" : confirmations
      }, 
      ...
    ] 
    """
    raise NotImplementedError

  def new_address(self):
    raise NotImplementedError

  def validate(self, address):
    raise NotImplementedError

  def send(self, outputs):
    """
    Example: self.send([(address, amount), ...])
    Returns: [txid, ...]
    """
    raise NotImplementedError

  def get_qrcode_address_data(self, address):
    raise NotImplementedError

  def get_qrcode_request_data(self, address, amount):
    raise NotImplementedError

  def get_address_link(self, address):
    raise NotImplementedError

  def get_transaction_link(self, txid):
    raise NotImplementedError

class BitcoinManager(AssetManager):

  def __init__(self):
    super(BitcoinManager, self).__init__(
      key='BTC', label='Bitcoin', decimal_places=8
    )

  def bitcoind_rpc(self):
    return AuthServiceProxy(settings.BITCOIND_RPC)

  def get_balance(self, address):
    all_unspent = self.bitcoind_rpc().listunspent()
    unspent = filter(lambda tx: tx['address'] == address, all_unspent)
    return _sum_key(unspent, 'amount')

  def get_wallet_balance(self):
    raise NotImplementedError

  def get_received(self, address):
    received = self.bitcoind_rpc().getreceivedbyaddress(address)
    return received and received or Decimal("0.0")

  def get_receives(self, address):
    txlist = self.bitcoind_rpc().listtransactions("")
    valid = lambda tx: tx["category"] == "receive" and tx["address"] == address
    def reformat(tx):
      return {
        "txid" : tx['txid'], 
        "address" : tx['address'],
        "amount" : tx['amount'], 
        "timereceived" : tx['timereceived'],
        "confirmations" : tx['confirmations'],
      }
    txlist = map(reformat, filter(valid, txlist))
    return sorted(txlist, key=lambda tx: tx["timereceived"], reverse=True)

  def new_address(self):
    return self.bitcoind_rpc().getnewaddress()

  def validate(self, address):
    return bitcoinaddress.validate(address)

  def send(self, outputs):
    raise NotImplementedError

  def get_qrcode_address_data(self, address):
    return "bitcoin:%(address)s" % { "address" : address }

  def get_qrcode_request_data(self, address, amount):
    args = { "address" : address, "amount" : amount }
    return "bitcoin:%(address)s?amount=%(amount)0.8f" % args

  def get_address_link(self, address):
    # TODO testnet "http://tbtc.blockr.io/address/info/%s" address
    return "https://blockchain.info/address/%s" % address

  def get_transaction_link(self, txid):
    # TODO testnet "http://tbtc.blockr.io/tx/info/%s" % txid
    return "https://blockchain.info/tx/%s" % txid

def counterpartyd_querry(payload):
  response = requests.post(
    settings.COUNTERPARTYD_URL,
    data=json.dumps(payload),
    headers={'content-type': 'application/json'},
    auth=HTTPBasicAuth(
      settings.COUNTERPARTYD_USER,
      settings.COUNTERPARTYD_PASS
    )
  )
  return response.json()

class CounterpartyManager(BitcoinManager):

  def __init__(self, key=None, label=None):
    assert(key)
    assert(label)
    counterparty_assets = (counterpartyd_querry({
      "method": "get_asset_names", "jsonrpc": "2.0", "id": 0,
    })['result'] + [u'XCP'])
    assert(key in counterparty_assets)

    # get decimal_places
    response = counterpartyd_querry({
      "method": "get_asset_info",
      "params": {"assets" : [key]},
      "jsonrpc": "2.0",
      "id": 0,
    })
    decimal_places = response['result'][0]['divisible'] and 8 or 0

    super(BitcoinManager, self).__init__(key, label, decimal_places)

  def get_balance(self, address):
    payload = {
      "method": "get_balances",
      "params": {
        "filters": [
          {'field': 'address', 'op': '==', 'value': address},
        ],
      },
      "jsonrpc": "2.0",
      "id": 0,
    }
    result = counterpartyd_querry(payload)['result']
    result = filter(lambda x: x['asset'] == self.key, result)
    return _sum_key(result, 'quantity', self.decimal_places)

  def get_wallet_balance(self):
    raise NotImplementedError

  def get_received(self, address):
    result = counterpartyd_querry({
      "method": "get_sends",
      "params": {
        "filters": [
          {'field': 'destination', 'op': '==', 'value': address},
          {'field': 'asset', 'op': '==', 'value': self.key},
        ],
      },
      "jsonrpc": "2.0",
      "id": 0,
    })['result']
    return _sum_key(result, 'quantity', self.decimal_places)

  def get_receives(self, address):
    btcrpc = self.bitcoind_rpc()
    blockcount = btcrpc.getblockcount()
    result = counterpartyd_querry({
      "method": "get_sends",
      "params": {
        "filters": [
          {'field': 'destination', 'op': '==', 'value': address},
          {'field': 'asset', 'op': '==', 'value': self.key},
        ],
      },
      "jsonrpc": "2.0",
      "id": 0,
    })['result']
    def reformat(tx):
      btctx = btcrpc.gettransaction(tx['tx_hash'])
      return {
        "txid" : tx['tx_hash'], 
        "address" : tx['destination'],
        "amount" : (tx['quantity'] / (Decimal("10.0") ** self.decimal_places)), 
        "timereceived" : btctx['timereceived'],
        "confirmations" : blockcount - tx['block_index'] + 1,
      }
    txlist = map(reformat, result)
    return sorted(txlist, key=lambda tx: tx["timereceived"], reverse=True)

  def send(self, outputs):
    raise NotImplementedError("TODO implement")

  def get_qrcode_address_data(self, address):
    return address # TODO counterparty link standard?

  def get_qrcode_request_data(self, address, amount):
    return address # TODO counterparty link standard?

  def get_address_link(self, address):
    return "http://www.blockscan.com/address.aspx?q=%s" % address


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

