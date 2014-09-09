# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from decimal import Decimal
from django.core.exceptions import PermissionDenied
from apps.common.utils.models import get_object_or_none
from apps.userfund.models import UserFund
from apps.asset import control as asset_control

def create(user, bounty):
  uf = UserFund()
  uf.user = user
  uf.bounty = bounty
  uf.funding_address = asset_control.get_manager(bounty.asset).new_address()
  uf.save()
  return uf

def can_fund(user, bounty):
  if not user.is_authenticated():
    return False
  return bounty.created_by == user or bounty.public

def get(user, bounty):
  if not can_fund(user, bounty):
    return None
  userfund = get_object_or_none(UserFund, user=user, bounty=bounty)
  if not userfund:
    userfund = create(user, bounty)
  return userfund

def set_refund(user, bounty, address):
  if not can_fund(user, bounty):
    raise PermissionDenied
  userfund = get(user, bounty)
  userfund.refund_address = address
  userfund.save()

def funded_bounty(user, bounty):
  userfund = get_object_or_none(UserFund, user=user, bounty=bounty)
  if userfund:
    return userfund.received > Decimal("0.0")
  return False

