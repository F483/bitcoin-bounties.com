# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from django import template
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from apps.bounty import control
from apps.common.templatetags.condition_tag import condition_tag

register = template.Library()

@register.tag
@condition_tag
def if_can_edit_bounty(user, bounty):
  return control.can_edit(user, bounty)

@register.tag
@condition_tag
def if_can_make_public(user, bounty):
  return control.can_make_public(user, bounty)

@register.tag
@condition_tag
def if_can_declare_unresolved(user, bounty):
  return control.can_declare_unresolved(user, bounty)

@register.tag
@condition_tag
def if_can_delete(user, bounty):
  return control.can_delete(user, bounty)

@register.filter
def render_type(bounty):
  if bounty.public:
    result = """<i class="fa fa-globe"></i>"""
  else:
    result = """<i class="fa fa-shield"></i>"""
  return mark_safe(result)

