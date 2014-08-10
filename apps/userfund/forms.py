# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from django.forms import Form
from django.forms import CharField
from django.forms import ValidationError
from django.utils.translation import ugettext as _
from apps.bitcoin import control as bitcoin_control

class SetRefund(Form):

  address = CharField(label=_("ADDRESS"))

  def __init__(self, *args, **kwargs):
    userfund = kwargs.pop("userfund")
    super(SetRefund, self).__init__(*args, **kwargs)
    if userfund:
      self.fields["address"].initial = userfund.refund_address

  def clean_address(self):
    address = self.cleaned_data["address"]
    if not bitcoin_control.is_valid(address):
      raise ValidationError(_("ERROR_INVALID_ADDRESS"))
    return address

