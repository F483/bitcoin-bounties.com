# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from django import template
from django.utils.safestring import mark_safe
from apps.common.templatetags.common_tags import gen_qrcode

register = template.Library()

@register.filter
def render_asset(amount):
  return amount

@register.filter
def render_address(address):
  #address = " ".join(chunks(address, 12))
  return mark_safe("""<small>%s</small>""" % address)

@register.simple_tag
def gen_address_qrcode(tag_id, address):
  return gen_qrcode(5, tag_id, "bitcoin:%(address)s" % { "address" : address })

@register.simple_tag
def gen_request_qrcode(tag_id, address, amount):
  args = { "address" : address, "amount" : amount }
  data = "bitcoin:%(address)s?amount=%(amount)0.8f" % args
  return gen_qrcode(8, tag_id, data)

@register.filter
def render_transaction(txid):
  txid = " ".join(chunks(txid, 32))
  return mark_safe("""<small>%s</small>""" % txid)

@register.filter
def render_transaction_link(txid):
  return mark_safe("""
    <a href="https://blockchain.info/tx/%(txid)s" target="_blank">%(label)s</a>
  """ % { "txid" : txid, "label" : render_transaction(txid) })

