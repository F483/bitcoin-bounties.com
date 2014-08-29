# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from decimal import Decimal
from django.db.models import Model
from django.db.models import DateTimeField
from django.db.models import DecimalField
from django.db.models import CharField
from django.utils.translation import ugettext as _

class PaymentLog(Model):

  asset = CharField(max_length=100)
  address = CharField(max_length=100)
  transaction = CharField(max_length=100) # TODO rename to txid

  @property
  def transactionobj(self): # TODO rename to transaction
    from apps.asset import control
    am = control.get_manager(self.asset)
    return am.get_receive(self.address, self.transaction)

  @property
  def amount(self):
    return self.transactionobj["amount"]

  def __unicode__(self):
    return "asset: %s, address: %s, transaction: %s" % (
      self.asset, self.address, self.transaction
    )

