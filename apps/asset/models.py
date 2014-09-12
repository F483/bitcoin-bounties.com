# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from decimal import Decimal
from django.db.models import Model
from django.db.models import DateTimeField
from django.db.models import DecimalField
from django.db.models import CharField
from django.db.models import IntegerField
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

