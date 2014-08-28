# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from django import template
from django.utils.safestring import mark_safe
from apps.common.templatetags.common_tags import gen_qrcode
from apps.asset import control as asset_control

register = template.Library()

@register.filter
def render_asset(amount, asset):
  fs = "%0." + str(asset_control.get_manager(asset).decimal_places) + "f%s"
  return fs % (amount, asset)

@register.filter
def render_address(address):
  return mark_safe("""<small>%s</small>""" % address)

@register.simple_tag
def gen_address_qrcode(tag_id, address, asset):
  am = asset_control.get_manager(asset)
  return gen_qrcode(5, tag_id, am.get_qrcode_address_data(address))

@register.simple_tag
def gen_request_qrcode(tag_id, address, amount, asset):
  am = asset_control.get_manager(asset)
  return gen_qrcode(8, tag_id, am.get_qrcode_request_data(address, amount))

@register.filter
def render_transaction(txid):
  txid = " ".join(chunks(txid, 32))
  return mark_safe("""<small>%s</small>""" % txid)

@register.filter
def render_transaction_link(txid, asset):
  am = asset_control.get_manager(asset)
  return mark_safe('<a href="%(link)s" target="_blank">%(label)s</a>' % { 
    "link" : am.get_transaction_link(txid), 
    "label" : render_transaction(txid) 
  })

