# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

import bleach
import markdown
import datetime
from django import template
from django.utils.safestring import mark_safe
from apps.common.templatetags.condition_tag import condition_tag

register = template.Library()

@register.simple_tag
def gen_qrcode(typenumber, tag_id, data):
  return """
    <div id="%(id)s"></div>
    <script type="text/javascript">
      append_qrcode(%(typenumber)s,"%(id)s","%(data)s");
    </script>
  """ % { "id" : tag_id, "data" : data, "typenumber" : typenumber }

@register.simple_tag
def render_button(label, url, button_classes, icon_classes=None):
  args = { 
    "label" : label, "url" : url, 
    "button_classes" : button_classes, 
    "icon_classes" : icon_classes 
  }
  if icon_classes:
    return """
      <a href="%(url)s" class="%(button_classes)s">
        <i class="%(icon_classes)s"></i> %(label)s
      </a>
    """ % args
  return """<a href="%(url)s" class="%(button_classes)s">%(label)s</a>""" % args

@register.simple_tag
def render_button_edit(label, url, button_classes):
  return render_button(label, url, button_classes, "fa fa-pencil")

@register.simple_tag
def render_button_delete(label, url, button_classes):
  return render_button(label, url, button_classes, "fa fa-trash-o")

@register.simple_tag
def render_button_cancel(label, url, button_classes):
  return render_button(label, url, button_classes, "fa fa-minus-circle")

@register.simple_tag
def render_boolean(value):
  if value:
    return """<i class="fa fa-check"></i>"""
  else:
    return """<i class="fa fa-times"></i>"""

@register.filter
def render_markdown(usertext):
  tags = [
    'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'h1', 'h2', 'h3', 
    'h4', 'h5', 'h6', 'hr', 'i', 'img', 'li', 'ol', 'p', 'pre', 'strong', 'ul'
  ]
  attributes = {
    'a': ['href', 'title'], 
    'abbr': ['title'], 
    'acronym': ['title'],
    'img' : ['src', 'alt', 'title']
  }
  html = markdown.markdown(usertext) # docs say use bleach instead of safe_mode 
  return mark_safe(bleach.clean(html, tags=tags, attributes=attributes))

@register.tag
@condition_tag
def if_user_in_group(user, groupname):
  return bool(user.groups.filter(name=groupname))

@register.filter
def mul(a, b):
  return a * b

@register.filter
def div(a, b):
  if not b:
    return b
  return a / b

@register.filter
def render_percent(ratio):
  percent = ratio * 100
  return "%0.1f%%" % percent

@register.filter
def unixtime_to_datetime(unixtime):
  return datetime.datetime.fromtimestamp(unixtime)

@register.filter
def unixtime_to_date(unixtime):
  return unixtime_to_datetime(unixtime).date()

