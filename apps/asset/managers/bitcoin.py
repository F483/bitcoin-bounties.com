# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

import json
import requests
import bitcoinaddress
from apps.common.utils.misc import chunks
from decimal import Decimal
from requests.auth import HTTPBasicAuth
from bitcoinrpc.authproxy import AuthServiceProxy
from config import settings
from apps.asset.models import PaymentLog
from apps.asset.managers.asset import AssetManager

def get_bitcoind_rpc():
  return AuthServiceProxy(settings.BITCOIND_RPC)

class BitcoinManager(AssetManager):

  def __init__(self):
    super(BitcoinManager, self).__init__(
      key='BTC', label='Bitcoin', decimal_places=8
    )

  def get_chain_height(self):
    return get_bitcoind_rpc().getblockcount()

  def get_tx_height(self, txid):
    rpc = get_bitcoind_rpc()
    return rpc.getblock(rpc.gettransaction(txid)['blockhash'])['height']

  def get_balance(self, address):
    all_unspent = get_bitcoind_rpc().listunspent()
    unspent = filter(lambda tx: tx['address'] == address, all_unspent)
    balance = sum(map(lambda x: Decimal(x['amount']), unspent))
    return balance and balance or Decimal("0.0")

  def get_wallet_addresses(self):
    rpc = get_bitcoind_rpc()
    addresses = []
    accounts = rpc.listaccounts().keys()
    for account in accounts:
      addresses = addresses + rpc.getaddressesbyaccount(account)
    return addresses

  def get_wallet_balance(self):
    return get_bitcoind_rpc().getbalance()

  def get_transaction_fee_buffer(self):
    return Decimal("0.0005")

  def get_received(self, address):
    received = get_bitcoind_rpc().getreceivedbyaddress(address)
    return received and received or Decimal("0.0")

  def get_receive(self, address, txid):
    tx = get_bitcoind_rpc().gettransaction(txid)
    details = filter(lambda d: d['address'] == address, tx["details"])
    amount = abs(details and details[0]["amount"] or Decimal("0.0"))
    return {
      "txid" : tx['txid'], 
      "address" : address,
      "asset" : self.key,
      "amount" : amount, 
      "timereceived" : tx['timereceived'],
      "confirmations" : tx['confirmations'],
    }

  def get_receives(self, address):
    txlist = get_bitcoind_rpc().listtransactions("", 900000000000000000)
    valid = lambda tx: tx["category"] == "receive" and tx["address"] == address
    asset = self.key
    def reformat(tx):
      return {
        "txid" : tx['txid'], 
        "address" : tx['address'],
        "asset" : asset,
        "amount" : tx['amount'], 
        "timereceived" : tx['timereceived'],
        "confirmations" : tx['confirmations'],
      }
    txlist = map(reformat, filter(valid, txlist))
    return sorted(txlist, key=lambda tx: tx["timereceived"], reverse=True)

  def new_address(self):
    return get_bitcoind_rpc().getnewaddress()

  def validate(self, address):
    return bitcoinaddress.validate(address)

  def send(self, outputs):
    rpc = get_bitcoind_rpc()
    # check if enough funds in hot wallet
    if not self.sufficient_hot_funds(outputs):
      signals.insufficent_hot_funds.send(sender=self.send, asset=self.key)
      raise Exception("INSUFFICIENT FUNDS IN HOT WALLET")
    logs = {}
    max_outputs = 20
    for chunk in list(chunks(outputs, max_outputs)):
      dests = dict(map(lambda o: (o["destination"], float(o["amount"])), chunk))
      txid = rpc.sendmany("", dests)
      for output in chunk:
        address = output["destination"]
        log = PaymentLog()
        log.chainheight = self.get_chain_height()
        log.address = address
        log.asset = self.key
        log.txid = txid
        log.save()
        logs[address] = log
    return logs

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

  def get_private_key(self, address):
    try:
        return get_bitcoind_rpc().dumpprivkey(address)
    except:
        return None

