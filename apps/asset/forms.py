# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from django.forms import Form
from django.forms import CharField
from django.forms import DecimalField
from django.utils.translation import ugettext as _
from django.forms import ValidationError
from apps.asset.models import ColdStorage
from apps.asset import control

class ColdStorageAdd(Form):

  address = CharField(label=_("ADDRESS"))

  def __init__(self, *args, **kwargs):
    self.asset = kwargs.pop("asset")
    super(ColdStorageAdd, self).__init__(*args, **kwargs)

  def clean_address(self):
    am = control.get_manager(self.asset)
    address = self.cleaned_data["address"]
    if not am.validate(address):
      raise ValidationError(_("ERROR_INVALID_ADDRESS"))
    return address

class ColdStorageSend(Form):

  amount = DecimalField(label=_("AMOUNT"))

  def __init__(self, *args, **kwargs):
    self.asset = kwargs.pop("asset")
    am = control.get_manager(self.asset)
    super(ColdStorageSend, self).__init__(*args, **kwargs)
    self.fields["amount"].initial = 0.0
    self.fields["amount"].decimal_places = am.decimal_places 

  def clean_amount(self):
    am = control.get_manager(self.asset)
    amount = am.quantize(self.cleaned_data["amount"])

    # check max amount
    if amount > am.get_wallet_balance():
      raise ValidationError(_("INSUFFICIENT_HOT_FUNDS"))

    # cold storage wallet exists
    coldstorages = ColdStorage.objects.filter(asset=self.asset)
    coldstorages = filter(lambda cs: cs.imported == False, coldstorages)
    if len(coldstorages) == 0:
      raise ValidationError(_("ERROR_NO_COLD_STORAGE"))

    return amount

class ColdStorageImport(Form):

  private_key = CharField(label=_("PRIVATE_KEY"))


