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
from apps.asset import control as asset_control
from config import settings

class UserFund(Model):

  user = ForeignKey("auth.User", related_name="userfunds")
  bounty = ForeignKey("bounty.Bounty", related_name="userfunds")
  funding_address = CharField(max_length=100)
  refund_address = CharField(max_length=100, blank=True)
  refund_payments = ManyToManyField(
    'asset.PaymentLog',
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
  def balance(self):
    am = asset_control.get_manager(self.bounty.asset)
    return am.get_balance(self.funding_address)

  @property
  def received(self):
    """ Total funds received. """
    am = asset_control.get_manager(self.bounty.asset)
    return am.get_received(self.funding_address)

  @property
  def display_send_transactions(self):
    return [] # FIXME return refund transactions
    txlist = []
    rpc = bitcoin_control.get_rpc_access()
    for payment in self.refund_payments.all():
      tx = rpc.gettransaction(payment.transaction)
      tx["user"] = self.user   # add user for use in templates
      tx["type"] = _("REFUND") # add type for use in templates
      txlist.append(tx)
    return txlist

  @property
  def receive_transactions(self):
    am = asset_control.get_manager(self.bounty.asset)
    txlist = am.get_receives(self.funding_address)
    return filter(lambda tx: tx["confirmations"] > 0, txlist) # confirmed

  @property
  def display_receive_transactions(self):
    am = asset_control.get_manager(self.bounty.asset)
    txlist = am.get_receives(self.funding_address)
    for tx in txlist:
      tx["user"] = self.user    # add user for use in templates
      tx["type"] = _("FUNDING") # add type for use in templates
    return txlist

  def __unicode__(self):
    from apps.asset.templatetags.asset_tags import render_asset
    return "User: %s - Bounty.id: %s - %s - %s" % (
      self.user.username, self.bounty.id, 
      render_asset(self.balance, self.bounty.asset),
      self.refund_address and self.refund_address or "NO_REFUND_ADDRESS"
    )

