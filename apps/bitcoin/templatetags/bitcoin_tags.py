# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from django import template
from config import settings
from decimal import Decimal
from apps.common.templatetags.common_tags import gen_qrcode
from django.utils.safestring import mark_safe
from apps.bitcoin import control
from apps.common.utils.misc import chunks

register = template.Library()

@register.filter
def render_btc(btc):
  """ Display as BTC with full accuracy. """
  return "%0.8fBTC" % btc

@register.filter
def render_mbtc(btc):
  """ Display as mBTC with full accruracy. """
  mbtc = control.btc2mbtc(btc)
  return "%0.5fmBTC" % mbtc

@register.filter
def render_bitcoin(btc):
  """ Display bitcoin in the most userfriendly manner. """
  if btc < Decimal("1.0"):
    mbtc = control.btc2mbtc(btc)
    return "%0.2fmBTC" % mbtc
  else:
    return "%0.2fBTC" % btc

@register.filter
def render_address(address):
  #address = " ".join(chunks(address, 12))
  return mark_safe("""<small>%s</small>""" % address)

@register.filter
def render_address_link(address):
  return mark_safe("""
    <a href="https://blockchain.info/address/%(address)s" target="_blank">
      %(label)s
    </a>
  """ % { "address" : address, "label" : render_address(address) })

@register.filter
def render_transaction(txid):
  txid = " ".join(chunks(txid, 32))
  return mark_safe("""<small>%s</small>""" % txid)

@register.filter
def render_transaction_link(txid):
  return mark_safe("""
    <a href="https://blockchain.info/tx/%(txid)s" target="_blank">%(label)s</a>
  """ % { "txid" : txid, "label" : render_transaction(txid) })

@register.simple_tag
def gen_address_qrcode(tag_id, address):
  return gen_qrcode(5, tag_id, "bitcoin:%(address)s" % { "address" : address })

@register.simple_tag
def gen_request_qrcode(tag_id, address, amount):
  args = { "address" : address, "amount" : amount }
  data = "bitcoin:%(address)s?amount=%(amount)0.8f" % args
  return gen_qrcode(8, tag_id, data)

