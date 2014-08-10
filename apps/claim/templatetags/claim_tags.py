# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from django import template
from apps.claim import control
from apps.common.templatetags.condition_tag import condition_tag

register = template.Library()

@register.tag
@condition_tag
def if_can_claim(user, bounty):
  return control.can_claim(user, bounty)

@register.tag
@condition_tag
def if_can_view_claims(user, bounty):
  return control.can_view_claims(user, bounty)

@register.tag
@condition_tag
def if_can_view_claim(user, claim):
  return control.can_view_claim(user, claim)

@register.tag
@condition_tag
def if_can_edit_claim(user, claim):
  return control.can_edit(user, claim)

@register.tag
@condition_tag
def if_can_change_address(user, claim):
  return control.can_change_address(user, claim)

@register.tag
@condition_tag
def if_can_accept_claim(user, claim):
  return control.can_accept(user, claim)

@register.tag
@condition_tag
def if_can_declare_winner(user, claim):
  return control.can_declare_winner(user, claim)

