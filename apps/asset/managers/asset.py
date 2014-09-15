# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from decimal import Decimal, ROUND_DOWN

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

  def get_receive(self, address, txid):
    txlist = filter(lambda tx: tx["txid"] == txid, self.get_receives(address))
    return txlist and txlist[0] or None

  def sufficient_hot_funds(self, outputs):
    """
    Example: self.sufficient_hot_funds([(address, amount), ...])
    Returns: bool
    """
    available = self.get_wallet_balance()
    txfeebuffer = self.get_transaction_fee_buffer()
    required = sum(map(lambda o: o["amount"] + txfeebuffer, outputs))
    return available >= required

  def get_wallet_balance(self):
    return sum(map(self.get_balance, self.get_wallet_addresses()))

  def get_address_balances(self):
    """ Returns: sorted([(address, balance), ...]) """
    get_balance = self.get_balance
    balances = map(lambda a: (a, get_balance(a)), self.get_wallet_addresses())
    balances = filter(lambda b: b[1] != Decimal("0.0"), balances)
    return sorted(balances, key=lambda b: b[1])

  def address_in_wallet(self, address):
    return bool(self.get_private_key(address))

  def get_private_key(self, address):
    raise NotImplementedError

  def get_chain_height(self):
    raise NotImplementedError

  def get_tx_height(self, txid):
    raise NotImplementedError

  def get_balance(self, address):
    raise NotImplementedError

  def get_wallet_addresses(self):
    raise NotImplementedError

  def get_transaction_fee_buffer(self):
    """ Minimum wallet balance required to cover a transaction fee. """
    raise NotImplementedError

  def get_received(self, address):
    raise NotImplementedError

  def get_receives(self, address):
    """ Get a list of transactions where this address received assets.
    Returns: [
      { 
        "txid" : txid, 
        "address" : address,
        "asset" : asset,
        "amount" : amount, 
        "timereceived" : unixtime,
        "confirmations" : confirmations
      }, 
      ...
    ] 
    """
    raise NotImplementedError

  def send(self, outputs):
    """
    Example: self.send([{"destination" : address, "amount" : amount}, ...])
    Returns: { address : PaymentLog, ... }
    """
    raise NotImplementedError

  def new_address(self):
    raise NotImplementedError

  def validate(self, address):
    raise NotImplementedError

  def get_qrcode_address_data(self, address):
    raise NotImplementedError

  def get_qrcode_request_data(self, address, amount):
    raise NotImplementedError

  def get_address_link(self, address):
    raise NotImplementedError

  def get_transaction_link(self, txid):
    raise NotImplementedError

