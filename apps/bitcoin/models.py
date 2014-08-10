# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from decimal import Decimal
from django.db.models import Model
from django.db.models import ManyToManyField
from django.db.models import DateTimeField
from django.db.models import DecimalField
from django.db.models import ForeignKey
from django.db.models import BooleanField
from django.db.models import CharField
from django.utils.translation import ugettext as _

class PaymentLog(Model):

  amount = DecimalField(max_digits=512, decimal_places=256)
  account = CharField(max_length=100, blank=True) # account sent from
  address = CharField(max_length=100)
  transaction = CharField(max_length=100)
  service_fee = DecimalField(max_digits=512, decimal_places=256)
  transaction_fee = DecimalField(max_digits=512, decimal_places=256)

  # METADATA
  created_on = DateTimeField(auto_now_add=True)

  @property
  def fees(self):
    return self.service_fee + self.transaction_fee

  def __unicode__(self):
    from apps.bitcoin.templatetags.bitcoin_tags import render_bitcoin
    return "%s -> %s, %s service fee, %s transaction fee" % (
      render_bitcoin(self.amount), self.address,
      render_bitcoin(self.service_fee),
      render_bitcoin(self.transaction_fee),
    )

class ColdStorage(Model):

  address = CharField(max_length=100, unique=True)
  imported = CharField(max_length=100, blank=True) # import account
  payments = ManyToManyField(
    'bitcoin.PaymentLog',
    related_name="coldstorage_payments",
    null=True, blank=True
  )

  # METADATA
  created_on = DateTimeField(auto_now_add=True)
  created_by = ForeignKey('auth.User', related_name="coldstorages_created")
  updated_on = DateTimeField(auto_now=True)
  updated_by = ForeignKey("auth.User", related_name="coldstorages_updated")

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

