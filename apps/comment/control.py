# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from django.core.exceptions import PermissionDenied

def can_delete(user, comment):
  if not user.is_authenticated():
    return False
  if not user.is_staff:
    return False
  return True

def delete(user, comment):
  if not can_delete(user, comment):
    raise PermissionDenied
  comment.delete()

