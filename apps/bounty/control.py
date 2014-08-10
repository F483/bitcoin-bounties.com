# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

import datetime
from decimal import Decimal
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.exceptions import PermissionDenied
from apps.bitcoin import control as bitcoin_control
from apps.tags import control as tags_control
from apps.search import control as search_control
from apps.bounty.models import Bounty
from apps.comment.models import Comment
from apps.userfund.models import UserFund
from apps.bounty import signals
from config import settings

def can_comment(user, bounty):
  if not user.is_authenticated():
    return False
  if bounty.state == 'DELETED':
    return False
  return True

def can_edit(user, bounty):
  if not bounty.private:
    return False
  if bounty.created_by != user:
    return False
  if bounty.state != "PENDING":
    return False
  return True

def can_make_public(user, bounty):
  if not bounty.private:
    return False
  if bounty.created_by != user:
    return False
  return True

def can_declare_unresolved(user, bounty):
  if not user.is_authenticated():
    return False
  if not user.is_staff:
    return False
  if bounty.state != "MEDIATION":
    return False
  return True

def can_delete(user, bounty):
  if not user.is_authenticated():
    return False
  if not user.is_staff:
    return False
  if bounty.state not in ["PENDING", "ACTIVE", "MEDIATION"]:
    return False
  return True

def get_or_404(user, bounty_id):
  valid_states = ['PENDING', 'ACTIVE', 'MEDIATION', 'FINISHED', 'CANCELLED']
  if not user.is_authenticated():
    return get_object_or_404(Bounty, id=bounty_id, state__in=valid_states)
  elif user.is_staff:
    return get_object_or_404(Bounty, id=bounty_id)
  invested = UserFund.objects.filter(user=user)
  invested = invested.exclude(cashed_funds_received=Decimal("0.0"))
  user_invested = Q(id=bounty_id, userfunds__in=invested)
  in_valid_states = Q(id=bounty_id, state__in=valid_states)
  bounties = Bounty.objects.filter(in_valid_states | user_invested)
  if len(bounties) == 0:
    raise Http404
  return bounties[0]

def delete(user, bounty):
  if not can_delete(user, bounty):
    raise PermissionDenied
  bounty.state = "DELETED"
  bounty.cashed_reward = bounty.display_reward # update cashe
  bounty.save()
  signals.deleted.send(sender=delete, bounty=bounty)
  return bounty

def declare_unresolved(user, bounty):
  if not can_declare_unresolved(user, bounty):
    raise PermissionDenied
  bounty.state = "FINISHED"
  bounty.cashed_reward = bounty.display_reward # update cashe
  bounty.save()
  signals.unsuccessful.send(sender=declare_unresolved, bounty=bounty)
  return bounty

def cancel(user, bounty):
  if not can_edit(user, bounty):
    raise PermissionDenied
  bounty.state = "CANCELLED"
  bounty.updated_by = user
  bounty.cancelled_on = datetime.datetime.now()
  bounty.cancelled_by = user
  bounty.cashed_reward = bounty.display_reward # update cashe
  bounty.save()
  return bounty

def make_public(user, bounty):
  if not can_make_public(user, bounty):
    raise PermissionDenied
  bounty.private = False
  bounty.updated_by = user
  bounty.save()
  return bounty

def edit(user, bounty, title, description, tagsstr, target, deadline):
  if not can_edit(user, bounty):
    raise PermissionDenied
  bounty.title = title
  bounty.description = description
  bounty.deadline = deadline
  bounty.target_reward = target
  bounty.cashed_reward = target # update cashe
  bounty.updated_by = user
  bounty.save()
  bounty.tags.remove(*list(bounty.tags.all()))
  bounty.tags.add(*tags_control.update(tagsstr))
  bounty.keywords.add(*search_control.update(title + u" " + tagsstr))
  return bounty

def create(user, title, description, tagsstr, target, deadline):
  bounty = Bounty()
  bounty.title = title
  bounty.description = description
  bounty.deadline = deadline
  bounty.target_reward = target
  bounty.cashed_reward = target # update cashe
  bounty.created_by = user
  bounty.updated_by = user
  bounty.save()
  bounty.keywords.add(*search_control.update(title + u" " + tagsstr))
  bounty.tags.add(*tags_control.update(tagsstr))
  return bounty

def comment(user, bounty, text):
  if not can_comment(user, bounty):
    raise PermissionDenied
  comment = Comment()
  comment.text = text
  comment.created_by = user
  comment.save()
  bounty.comments.add(comment)
  return bounty

