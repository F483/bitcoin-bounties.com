# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from django.forms import Form
from django.forms import BooleanField
from django.forms import CharField
from django.forms import Textarea
from django.forms import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from apps.asset import control as asset_control

class Create(Form):

  description = CharField(
    label=_("DESCRIPTION"), 
    widget=Textarea(attrs={'class' : 'pagedownBootstrap'})
  )
  address = CharField(label=_("ADDRESS"))

  terms = BooleanField(label=mark_safe(_("ACCEPT_TERMS")), initial=False)

  def __init__(self, *args, **kwargs):
    self.bounty = kwargs.pop("bounty")
    super(Create, self).__init__(*args, **kwargs)

  def clean_address(self):
    am = asset_control.get_manager(self.bounty.asset)
    address = self.cleaned_data["address"]
    if not am.validate(address):
      raise ValidationError(_("ERROR_INVALID_ADDRESS"))
    return address

class Edit(Form):

  description = CharField(
    label=_("DESCRIPTION"), 
    widget=Textarea(attrs={'class' : 'pagedownBootstrap'})
  )

  def __init__(self, *args, **kwargs):
    self.claim = kwargs.pop("claim")
    super(Edit, self).__init__(*args, **kwargs)
    self.fields["description"].initial = self.claim.description

class ChangeAddress(Form):

  address = CharField(label=_("ADDRESS"))

  def __init__(self, *args, **kwargs):
    self.claim = kwargs.pop("claim")
    super(ChangeAddress, self).__init__(*args, **kwargs)
    self.fields["address"].initial = self.claim.address

  def clean_address(self):
    am = asset_control.get_manager(self.claim.bounty.asset)
    address = self.cleaned_data["address"]
    if not am.validate(address):
      raise ValidationError(_("ERROR_INVALID_ADDRESS"))
    return address

