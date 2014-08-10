# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from django import template
from apps.comment import control
from apps.common.templatetags.condition_tag import condition_tag

register = template.Library()

@register.tag
@condition_tag
def if_can_delete_comment(user, comment):
  return control.can_delete(user, comment)

