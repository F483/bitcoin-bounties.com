# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from apps.common.utils.models import get_object_or_none
from apps.claim.models import Claim
from apps.claim.models import Accepted
from apps.comment.models import Comment
from apps.bounty import control as bounty_control
from apps.userfund import control as userfund_control
from apps.claim import signals

def can_view_claims(user, bounty):
  if bounty.public:
    return True
  if not user.is_authenticated():
    return False
  if user.is_staff:
    return True
  if bounty.created_by == user:
    return True
  if get_object_or_none(Claim, user=user, bounty=bounty):
    return True # user has a claim for this bounty
  return False

def can_view_claim(user, claim):
  if claim.bounty.public:
    return True
  if not user.is_authenticated():
    return False
  if user.is_staff:
    return True
  if claim.user == user:
    return True
  if claim.bounty.created_by == user:
    return True
  return False

def can_comment(user, claim):
  if not user.is_authenticated():
    return False
  if user.is_staff:
    return True
  if claim.user == user:
    return True
  if claim.bounty.created_by == user:
    return True
  return False

def can_claim(user, bounty):
  if not user.is_authenticated():
    return False
  if bounty.state != "ACTIVE":
    return False # can only claim active bounties
  if get_object_or_none(Claim, user=user, bounty=bounty):
    return False # claim from user already exists
  return True

def can_edit(user, claim):
  if not user.is_authenticated():
    return False
  if claim.user != user:
    return False
  if claim.bounty.state != "ACTIVE":
    return False
  return True

def can_change_address(user, claim):
  if not user.is_authenticated():
    return False
  if claim.user != user:
    return False
  return True

def can_accept(user, claim):
  if not user.is_authenticated():
    return False
  if not userfund_control.funded_bounty(user, claim.bounty):
    return False # user did not fund bounty
  if claim.bounty.state not in ["ACTIVE", "MEDIATION"]:
    return False # invalid state
  if get_object_or_none(Accepted, user=user, claim__bounty=claim.bounty):
    return False # already accepted a claim
  return True

def get_or_404(claim_id):
  valid_states = ['PENDING', 'ACTIVE', 'MEDIATION', 'FINISHED', 'CANCELLED']
  return get_object_or_404(Claim, id=claim_id, bounty__state__in=valid_states)

def can_declare_winner(user, claim):
  if not user.is_authenticated():
    return False
  if not user.is_staff:
    return False
  if claim.bounty.state not in ["ACTIVE", "MEDIATION"]:
    return False
  return True

def declare_winner(user, claim):
  if not can_declare_winner(user, claim):
    raise PermissionDenied
  claim.successful = True
  claim.save()
  claim.bounty.state = "FINISHED"
  claim.bounty.cashed_reward = claim.bounty.display_reward # update cashe
  claim.bounty.save()
  signals.successful.send(sender=declare_winner, claim=claim)
  return claim

def accept(user, claim):
  if not can_accept(user, claim):
    raise PermissionDenied
  accepted = Accepted()
  accepted.user = user
  accepted.claim = claim
  accepted.save()
  bounty = claim.bounty
  # accept and payout if the only claim is accepted
  if bounty.private and len(Claim.objects.filter(bounty=bounty)) == 1:
    claim.successful = True
    claim.save()
    bounty.state = "FINISHED"
    bounty.cashed_reward = bounty.display_reward # update cashe
    bounty.save()
    signals.successful.send(sender=declare_winner, claim=claim)
  return claim

def edit(user, claim, description):
  if not can_edit(user, claim):
    raise PermissionDenied
  claim.description = description
  claim.save()
  return claim

def change_address(user, claim, address):
  if not can_change_address(user, claim):
    raise PermissionDenied
  claim.address = address
  claim.save()
  return claim

def create(user, bounty, description, address):
  if not can_claim(user, bounty):
    raise PermissionDenied
  claim = Claim()
  claim.user = user
  claim.bounty = bounty
  claim.address = address
  claim.description = description
  claim.save()
  bounty = claim.bounty
  bounty.cashed_claim_count = len(Claim.objects.filter(bounty=bounty))
  bounty.save()
  signals.created.send(sender=create, claim=claim)
  return claim

def comment(user, claim, text):
  if not can_comment(user, claim):
    raise PermissionDenied
  comment = Comment()
  comment.text = text
  comment.created_by = user
  comment.save()
  claim.comments.add(comment)
  return claim

