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
    return transaction and transaction["amount"] or None

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
  address = CharField(max_length=100, unique=True)
  payments = ManyToManyField(
    'asset.PaymentLog',
    related_name="coldstorage_payments",
    null=True, blank=True
  )

  # METADATA
  created_on = DateTimeField(auto_now_add=True)
  created_by = ForeignKey('auth.User', related_name="coldstorages_created")
  updated_on = DateTimeField(auto_now=True)
  updated_by = ForeignKey("auth.User", related_name="coldstorages_updated")

  @property
  def imported(self):
    # TODO check if private_key in wallet
    return False

  @property
  def amount(self):
    # TODO return amount at address
    return Decimal("0.0")

  def __unicode__(self):
    from apps.bitcoin.templatetags.bitcoin_tags import render_bitcoin
    return "%s %s (%s)" % (
      self.address, 
      render_bitcoin(self.received),
      self.imported and _("IMPORTED") or _("COLD")
    )

  @property
  def received(self):
    total = Decimal("0.0")
    for payment in self.payments.all():
      total = total + payment.amount
    return total

