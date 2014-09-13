# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from decimal import Decimal
from django.db.models import Model
from django.db.models import DateField
from django.db.models import IntegerField
from django.db.models import ForeignKey
from django.db.models import DecimalField
from django.db.models import CharField
from django.db.models import ManyToManyField
from django.utils.translation import ugettext as _
from apps.common.utils.models import get_object_or_none
from config import settings

class UserFund(Model):

  user = ForeignKey("auth.User", related_name="userfunds")
  bounty = ForeignKey("bounty.Bounty", related_name="userfunds")
  funding_address = CharField(max_length=100)
  refund_address = CharField(max_length=100, blank=True)
  refund_payments = ManyToManyField(
    'asset.PaymentLog',
    related_name="refunds",
    null=True, blank=True
  )

  # remind user to set refund_address
  remind_count = IntegerField(default=0) 
  remind_date = DateField(null=True, blank=True) # last reminded

  # CASHED FOR VIEWS ONLY!!!
  cashed_funds_received = DecimalField(
    max_digits=512, decimal_places=256, default=Decimal("0.0")
  )

  @property
  def _am(self):
    from apps.asset import control as asset_control
    return asset_control.get_manager(self.bounty.asset)

  @property
  def received(self):
    """ Total funds received. """
    return self._am.get_received(self.funding_address)

  @property
  def torefund(self):

    # no refund for ongoing bounties
    if self.bounty.state in ['PENDING', 'ACTIVE', 'MEDIATION']:
      return Decimal("0.0")

    # no refund for successful bounties not yet payed 
    from apps.claim.models import Claim # avoid circular import
    claim = get_object_or_none(Claim, bounty=self.bounty, successful=True)
    if claim and not claim.payout:
      return Decimal("0.0")

    # everything <= minheight already processed
    minheight = 0
    if claim and claim.payout:
      minheight = claim.payout.chainheight
    for payment in self.refund_payments.all():
      if payment.chainheight > minheight:
        minheight = payment.chainheight

    unprocessedtx = lambda tx: self._am.get_tx_height(tx['txid']) > minheight
    txlist = filter(unprocessedtx, self.receive_transactions)
    total = Decimal(sum(map(lambda tx: tx["amount"], txlist)))
    return total - self._am.quantize(total * self.bounty.fraction_fees)

  @property
  def bound_funds(self):
    if self.bounty.state in ['PENDING', 'ACTIVE', 'MEDIATION']:
      fees = self._am.quantize(self.received * self.bounty.fraction_fees)
      return self.received - fees
    return self.torefund

  @property
  def has_min_refund_amount(self):
    return self.torefund > Decimal("0.0") # FIXME get min from asset manager

  @property
  def display_send_transactions(self):
    txlist = []
    for payment in self.refund_payments.all():
      tx = payment.transaction
      tx["user"] = self.user   # add user for use in templates
      tx["type"] = _("REFUND") # add type for use in templates
      txlist.append(tx)
    return txlist

  @property
  def receive_transactions(self):
    txlist = self._am.get_receives(self.funding_address)
    return filter(lambda tx: tx["confirmations"] > 0, txlist) # confirmed

  @property
  def display_receive_transactions(self):
    txlist = self._am.get_receives(self.funding_address)
    for tx in txlist:
      tx["user"] = self.user    # add user for use in templates
      tx["type"] = _("FUNDING") # add type for use in templates
    return txlist

  def __unicode__(self):
    from apps.asset.templatetags.asset_tags import render_asset
    return "User: %s - Bounty.id: %s - %s - %s" % (
      self.user.username, self.bounty.id, 
      render_asset(self.received, self.bounty.asset),
      self.refund_address and self.refund_address or "NO_REFUND_ADDRESS"
    )

