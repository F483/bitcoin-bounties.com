# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

import datetime
from decimal import Decimal
from django.db.models import Model
from django.db.models import ManyToManyField
from django.db.models import ForeignKey
from django.db.models import CharField
from django.db.models import TextField
from django.db.models import BooleanField
from django.db.models import DateTimeField
from django.db.models import DateField
from django.db.models import IntegerField
from django.db.models import DecimalField
from django.utils.translation import ugettext as _
from apps.common.utils.i18n import uslugify
from apps.common.utils.models import get_object_or_none
from apps.asset import control as asset_control
from config import settings

STATE_CHOICES = [
  ('PENDING',   _('PENDING')),
  ('ACTIVE',    _('ACTIVE')),
  ('MEDIATION', _('MEDIATION')),
  ('FINISHED',  _('FINISHED')),
  ('CANCELLED', _('CANCELLED')), # cancelled by creator or not funded in time
  ('DELETED',   _('DELETED')),
]

class Bounty(Model):

  # FIELDS
  title = CharField(max_length=100)
  description = TextField()
  deadline = DateField()
  state = CharField(max_length=64, choices=STATE_CHOICES, default='PENDING')
  private = BooleanField(default=True)
  target_reward = DecimalField(max_digits=512, decimal_places=256)
  fees = DecimalField(max_digits=512, decimal_places=256)
  asset = CharField(max_length=100)

  # MANY TO MANY
  tags = ManyToManyField('tags.Tag', related_name="bounties")
  keywords = ManyToManyField('search.Keyword', related_name="bounties")
  comments = ManyToManyField(
    'comment.Comment', related_name="bounty_comments", null=True, blank=True
  )

  # METADATA
  created_on = DateTimeField(auto_now_add=True)
  created_by = ForeignKey('auth.User', related_name="bounties_created")
  updated_on = DateTimeField(auto_now=True)
  updated_by = ForeignKey("auth.User", related_name="bounties_updated")
  cancelled_on = DateTimeField(null=True, blank=True)
  cancelled_by = ForeignKey(
    "auth.User", related_name="bounties_cancelled", null=True, blank=True
  )

  # CASHED FOR VIEWS ONLY!!!
  cashed_claim_count = IntegerField(default=0)
  cashed_reward = DecimalField(
    max_digits=512, 
    decimal_places=256, 
    default=Decimal("0.0")
  )

  @property
  def fraction_reward(self): 
    return (Decimal("1.0") / (Decimal("1.0") + self.fees))

  @property
  def fraction_fees(self):
    return Decimal("1.0") - self.fraction_reward

  @property
  def funds(self):
    total = Decimal("0.0")
    for userfund in self.userfunds.all():
      total = total + userfund.balance
    return total

  @property
  def received(self):
    """ Total funds received. """
    total = Decimal("0.0")
    for userfund in self.userfunds.all():
      total = total + userfund.received
    return total

  @property
  def target_funds(self):
    amount = (self.target_reward / self.fraction_reward)
    return asset_control.get_manager(self.asset).quantize(amount)

  @property
  def funds_needed(self):
    needed = self.target_funds - self.funds
    if needed < Decimal("0.0"):
      return Decimal("0.0")
    return needed

  @property
  def funded_ratio(self):
    if not self.target_funds:
      return Decimal("1")
    return self.funds / self.target_funds

  @property
  def slug(self):
    return uslugify(self.title)

  @property
  def public(self):
    return not self.private

  @property
  def awarded(self):
    from apps.claim.models import Claim # prevent circular import ...
    return get_object_or_none(Claim, bounty=self, successful=True)

  @property
  def display_fees(self):
    if self.awarded and self.awarded.payout:
      return self.awarded.payout.fees
    funds = self.state == "PENDING" and self.target_funds or self.funds
    amount = funds * self.fraction_fees
    return asset_control.get_manager(self.asset).quantize(amount)

  @property
  def display_reward(self):
    if self.awarded and self.awarded.payout:
      return self.awarded.payout.amount
    funds = self.state == "PENDING" and self.target_funds or self.funds
    reward = funds - self.display_fees
    if self.cashed_reward > reward:
      return self.cashed_reward
    return reward

  @property
  def display_send_transactions(self):
    txlist = []
    for userfund in self.userfunds.all():
      txlist = txlist + userfund.display_send_transactions
    if self.awarded and self.awarded.payout:
      rpc = bitcoin_control.get_rpc_access()
      payment = self.awarded.payout
      tx = rpc.gettransaction(payment.transaction)
      tx["user"] = self.awarded.user  # add user for use in templates
      tx["payment"] = payment  # add payment for use in templates
      tx["type"] = _("PAYOUT") # add type for use in templates
      txlist.append(tx)
    return sorted(txlist, key=lambda tx: tx["timereceived"], reverse=True)

  @property
  def display_receive_transactions(self):
    txlist = []
    for userfund in self.userfunds.all():
      txlist = txlist + userfund.display_receive_transactions
    return sorted(txlist, key=lambda tx: tx["timereceived"], reverse=True)

  @property
  def url_funds(self):
    return "/bounty/%s/funds/%s" % (self.id, self.slug)

  @property
  def url_details(self):
    return "/bounty/%s/details/%s" % (self.id, self.slug)

  @property
  def url_claims(self):
    return "/bounty/%s/claims/%s" % (self.id, self.slug)

  @property
  def url_comments(self):
    return "/bounty/%s/comments/%s" % (self.id, self.slug)

  @property
  def url_makepublic(self):
    return "/bounty/%s/makepublic/%s" % (self.id, self.slug)

  @property
  def url_cancel(self):
    return "/bounty/%s/cancel/%s" % (self.id, self.slug)

  @property
  def url_edit(self):
    return "/bounty/%s/edit/%s" % (self.id, self.slug)

  @property
  def url_delete(self):
    return "/bounty/%s/delete/%s" % (self.id, self.slug)

  @property
  def url_declare_unresolved(self):
    return "/bounty/%s/declare/unresolved" % self.id

  @property
  def url_setrefund(self):
    return "/userfund/setrefund/%s" % self.id

  @property
  def url_claim(self):
    return "/claim/create/%s" % self.id

  def __unicode__(self):
    from apps.asset.templatetags.asset_tags import render_asset
    return "%i: %s - %s - Funds: %s - Deadline: %s - Created: %s" % (
      self.id,
      self.title, self.state,
      render_asset(self.funds),
      self.deadline,
      self.created_on
    )

