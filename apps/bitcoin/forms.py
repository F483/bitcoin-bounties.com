# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from django.forms import Form
from django.forms import CharField
from django.forms import DecimalField
from django.utils.translation import ugettext as _
from django.forms import ValidationError
from apps.bitcoin.models import ColdStorage
from apps.bitcoin import control
from config import settings

class ColdStorageAdd(Form):

  address = CharField(label=_("ADDRESS"))

  def clean_address(self):
    address = self.cleaned_data["address"]
    if not control.is_valid(address):
      raise ValidationError(_("ERROR_INVALID_ADDRESS"))
    return address

class ColdStorageSend(Form):

  amount = DecimalField(label=_("AMOUNT_BTC"), decimal_places=8)

  def clean_amount(self):
    amount = self.cleaned_data["amount"]
    amount = control.quantize_satoshi(amount)
    
    # TODO validate that amount leaves minimum funds (1 week range)
    rpc = control.get_rpc_access()
    if amount > (rpc.getbalance() - settings.TRANSACTION_FEE_BUFFER):
      raise ValidationError(_("INSUFFICIENT_HOT_FUNDS"))

    # cold storage wallet exists
    if ColdStorage.objects.filter(imported="").count() == 0:
      raise ValidationError(_("ERROR_NO_COLD_STORAGE"))

    return amount

class ColdStorageImport(Form):

  private_key = CharField(label=_("PRIVATE_KEY"))

  # TODO check if private_key was previously imported

