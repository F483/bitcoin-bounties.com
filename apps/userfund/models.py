# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from decimal import Decimal
from django.db.models import Model
from django.db.models import DateField
from django.db.models import IntegerField
from django.db.models import ForeignKey
from django.db.models import DecimalField
from django.db.models import CharField
from django.db.models import ManyToManyField
from django.utils.translation import ugettext as _
from apps.assets import control as asset_control
from config import settings

class UserFund(Model):

  user = ForeignKey("auth.User", related_name="userfunds")
  bounty = ForeignKey("bounty.Bounty", related_name="userfunds")
  funding_address = CharField(max_length=100, blank=True)
  refund_address = CharField(max_length=100, blank=True)
  refund_payments = ManyToManyField(
    'assets.PaymentLog',
    related_name="userfunds",
    null=True, blank=True
  )

  # remind user to set refund_address
  remind_count = IntegerField(default=0) 
  remind_date = DateField(null=True, blank=True) # last reminded

  # CASHED FOR VIEWS ONLY!!!
  cashed_funds_received = DecimalField(
    max_digits=512, decimal_places=256, default=Decimal("0.0")
  )

  @property
  def account(self): # bitcoind account for incoming user funding
    args = { "prefix" : settings.ACCOUNT_PREFIX, "id" : str(self.id) }
    return "%(prefix)s_UserFundIncoming_%(id)s" % args

  @property
  def balance(self):
    rpc = bitcoin_control.get_rpc_access()
    return rpc.getbalance(self.account)

  @property
  def funding(self): # address to receive funds
    rpc = bitcoin_control.get_rpc_access()
    return rpc.getaccountaddress(self.account)

  @property
  def received(self):
    """ Total funds received. """
    total = Decimal("0.0")
    for transaction in self.receive_transactions:
      total = total + transaction["amount"]
    return total

  @property
  def display_send_transactions(self):
    txlist = []
    rpc = bitcoin_control.get_rpc_access()
    for payment in self.refund_payments.all():
      tx = rpc.gettransaction(payment.transaction)
      tx["user"] = self.user   # add user for use in templates
      tx["payment"] = payment  # add payment for use in templates
      tx["type"] = _("REFUND") # add type for use in templates
      txlist.append(tx)
    return txlist

  @property
  def receive_transactions(self):
    rpc = bitcoin_control.get_rpc_access()
    txlist = rpc.listtransactions(self.account)
    txlist = filter(lambda tx: tx["category"] == "receive", txlist) # received
    txlist = filter(lambda tx: tx["confirmations"] > 0, txlist) # confirmed
    return txlist

  @property
  def display_receive_transactions(self):
    rpc = bitcoin_control.get_rpc_access()
    txlist = rpc.listtransactions(self.account)
    txlist = filter(lambda tx: tx["category"] == "receive", txlist)
    for tx in txlist:
      tx["userfund"] = self # inject userfund for use in templates
    return txlist

  def __unicode__(self):
    from apps.bitcoin.templatetags.bitcoin_tags import render_mbtc
    return "User: %s - Bounty.id: %s - %s - %s" % (
      self.user.username, self.bounty.id, render_mbtc(self.balance),
      self.refund_address and self.refund_address or "NO_REFUND_ADDRESS"
    )

