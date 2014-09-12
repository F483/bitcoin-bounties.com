# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

import json
import requests
from decimal import Decimal
from requests.auth import HTTPBasicAuth
from config import settings
from apps.asset.models import PaymentLog
from apps.asset.managers.bitcoin import BitcoinManager
from apps.asset.managers.bitcoin import get_bitcoind_rpc

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

def get_asset_names():
    return (counterpartyd_querry({
      "method": "get_asset_names", "jsonrpc": "2.0", "id": 0,
    })['result'] + [u'XCP'])

def _sum_key(dictonary, key, move_decimal=0):
  value = sum(map(lambda x: Decimal(x[key]), dictonary))
  value = value / (Decimal("10.0") ** move_decimal)
  return value and value or Decimal("0.0")

class CounterpartyManager(BitcoinManager):

  def __init__(self, key=None, label=None):
    assert(key)
    assert(label)
    counterparty_assets = get_asset_names()
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

  def get_receive(self, address, txid):
    return super(BitcoinManager, self).get_receive(address, txid)

  def get_wallet_balance(self):
    return super(BitcoinManager, self).get_wallet_balance()

  def get_balance(self, address):
    result = counterpartyd_querry({
      "method": "get_balances",
      "params": {
        "filters": [
          {'field': 'address', 'op': '==', 'value': address},
          {'field': 'asset', 'op': '==', 'value': self.key},
        ]
      },
      "jsonrpc": "2.0",
      "id": 0,
    })['result']
    return _sum_key(result, 'quantity', self.decimal_places)

  def get_transaction_fee_buffer(self):
    return Decimal("0.0") # required in bitcoin see _findsourceaddress

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
    btcrpc = get_bitcoind_rpc()
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
    asset = self.key
    def reformat(tx):
      btctx = btcrpc.gettransaction(tx['tx_hash'])
      return {
        "txid" : tx['tx_hash'], 
        "address" : tx['destination'],
        "asset" : asset,
        "amount" : (tx['quantity'] / (Decimal("10.0") ** self.decimal_places)), 
        "timereceived" : btctx['timereceived'],
        "confirmations" : blockcount - tx['block_index'] + 1,
      }
    txlist = map(reformat, result)
    return sorted(txlist, key=lambda tx: tx["timereceived"], reverse=True)

  def get_qrcode_address_data(self, address):
    return address # TODO counterparty link standard?

  def get_qrcode_request_data(self, address, amount):
    return address # TODO counterparty link standard?

  def get_address_link(self, address):
    return "http://www.blockscan.com/address.aspx?q=%s" % address

  def _findsourceaddress(self, balances, amount):
    balances = sorted(balances.items(), key=lambda b: b[1])
    for balance in balances:
      address = balance[0]
      assetbalance = balance[1]
      btcbalance = super(CounterpartyManager, self).get_balance(address)
      btcbuffer = super(CounterpartyManager, self).get_transaction_fee_buffer()
      if assetbalance >= amount and btcbalance >= btcbuffer:
        return address
    return None
  
  def _findsourceaddresses(self, outputs):
    unprocessed = []
    processed = []
    balances = dict(self.get_address_balances())
    for output in outputs:
      source = self._findsourceaddress(balances, output["amount"])
      if source:
        output["source"] = source
        processed.append(output)
        balances[source] = balances[source] - output["amount"]
      else:
        unprocessed.append(output)
    if unprocessed:
      print ""
      print "TODO squash addresses for unprocessed outputs"
      print unprocessed
    return processed
    
  def _send(self, source, destination, quantity):
    unsigned_tx = counterpartyd_querry({
      "method": "create_send",
      "params": {
        "source" : source,
        "destination" : destination,
        "quantity" : quantity, 
        'asset': self.key,
      },
      "jsonrpc": "2.0",
      "id": 0,
    })["result"]
    signed_tx = counterpartyd_querry({
      "method": "sign_tx",
      "params": {'unsigned_tx_hex': unsigned_tx},
      "jsonrpc": "2.0",
      "id": 0,
    })["result"]
    txid = counterpartyd_querry({
      "method": "broadcast_tx",
      "params": {'signed_tx_hex': signed_tx},
      "jsonrpc": "2.0",
      "id": 0,
    })["result"]
    return txid

  def counterpartysend(self, source, destination, quantity):
    txid = self._send(source, destination, quantity)
    log = PaymentLog()
    log.chainheight = self.get_chain_height()
    log.address = destination
    log.asset = self.key
    log.txid = txid
    log.save()
    return log

  def send(self, outputs):
    outputs = sorted(outputs, key=lambda o: o["amount"])
    # check if enough funds in hot wallet
    if not self.sufficient_hot_funds(outputs):
      signals.insufficent_hot_funds.send(sender=self.send, asset=self.key)
      raise Exception("INSUFFICIENT FUNDS IN HOT WALLET")
    outputs = self._findsourceaddresses(outputs)
    logs = {}
    for output in outputs:
      log = self.counterpartysend(
        output["source"], 
        output["destination"], 
        int(output["amount"] * 10 ** self.decimal_places)
      )
      logs[output["destination"]] = log
    return logs

