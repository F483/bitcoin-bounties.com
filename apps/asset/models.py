# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from decimal import Decimal
from django.db.models import Model
from django.db.models import DateTimeField
from django.db.models import DecimalField
from django.db.models import CharField
from django.db.models import IntegerField
from django.db.models import ManyToManyField
from django.db.models import ForeignKey
from django.utils.translation import ugettext as _

class PaymentLog(Model):

  asset = CharField(max_length=100)
  address = CharField(max_length=100)
  txid = CharField(max_length=100)
  chainheight = IntegerField()

  # METADATA
  created_on = DateTimeField(auto_now_add=True)

  @property
  def transaction(self):
    from apps.asset import control
    am = control.get_manager(self.asset)
    return am.get_receive(self.address, self.txid)

  @property
  def amount(self):
    transaction = self.transaction
    return transaction and transaction["amount"] or Decimal("0.0")

  @property
  def confirmations(self):
    transaction = self.transaction
    return transaction and transaction["confirmations"] or 0
  
  def __unicode__(self):
    return "asset: %s, amount: %s, address: %s, confirmations: %s, txid: %s" % (
      self.asset, self.amount, self.address, self.confirmations, self.txid
    )

class ColdStorage(Model):

  asset = CharField(max_length=100)
  address = CharField(max_length=100)
  payments = ManyToManyField(
    'asset.PaymentLog',
    related_name="coldstorage_payments",
    null=True, blank=True
  )

  # METADATA
  created_on = DateTimeField(auto_now_add=True)
  created_by = ForeignKey('auth.User', related_name="coldstorages_created")

  @property
  def imported(self):
    from apps.asset import control
    am = control.get_manager(self.asset)
    return am.address_in_wallet(self.address)

  @property
  def amount(self):
    if self.imported:
      from apps.asset import control
      am = control.get_manager(self.asset)
      return am.get_balance(self.address)
    else:
      return Decimal(sum(map(lambda p: p.amount, self.payments.all())))


  def __unicode__(self):
    from apps.asset.templatetags.asset_tags import render_asset
    return "%s %s (%s)" % (
      self.address, 
      render_asset(self.amount, self.asset),
      self.imported and _("IMPORTED") or _("COLD")
    )

  class Meta:
    unique_together = (("asset", "address"),)
    ordering = ["created_on"]
