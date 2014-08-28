# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from django.db.models import Model
from django.db.models import DateTimeField
from django.db.models import DecimalField
from django.db.models import CharField
from django.utils.translation import ugettext as _

class PaymentLog(Model):

  asset = CharField(max_length=100)
  amount = DecimalField(max_digits=512, decimal_places=256)
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

