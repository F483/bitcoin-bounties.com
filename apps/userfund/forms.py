# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from django.forms import Form
from django.forms import CharField
from django.forms import ValidationError
from django.utils.translation import ugettext as _
from apps.asset import control as asset_control

class SetRefund(Form):

  address = CharField(label=_("ADDRESS"))

  def __init__(self, *args, **kwargs):
    self.userfund = kwargs.pop("userfund")
    super(SetRefund, self).__init__(*args, **kwargs)
    self.fields["address"].initial = self.userfund.refund_address

  def clean_address(self):
    address = self.cleaned_data["address"]
    asset = self.userfund.bounty.asset
    if not asset_control.get_manager(asset).validate(address):
      raise ValidationError(_("ERROR_INVALID_ADDRESS"))
    return address

