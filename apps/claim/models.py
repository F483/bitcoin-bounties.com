# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from decimal import Decimal
from django.db.models import Model
from django.db.models import ManyToManyField
from django.db.models import DateTimeField
from django.db.models import BooleanField
from django.db.models import ForeignKey
from django.db.models import CharField
from django.db.models import TextField

class Claim(Model):

  user = ForeignKey("auth.User", related_name="claims")
  bounty = ForeignKey("bounty.Bounty", related_name="claims")
  description = TextField()
  address = CharField(max_length=100) # address for receiving reward
  successful = BooleanField(default=False)
  payout = ForeignKey("bitcoin.PaymentLog", null=True, blank=True)

  # MANY TO MANY
  comments = ManyToManyField(
    'comment.Comment', related_name="claim_comments", null=True, blank=True
  )

  # METADATA
  created_on = DateTimeField(auto_now_add=True)
  updated_on = DateTimeField(auto_now=True)

  @property
  def weight(self):
    """ Accepts as a fraction of total funding. """
    total_funds = Decimal("0.0")
    claim_funds = Decimal("0.0")
    userfunds = self.bounty.userfunds.all()
    accepts = self.accepts.all()
    for userfund in userfunds:
      total_funds = total_funds + userfund.received
      if len(filter(lambda a: a.user == userfund.user, accepts)):
        claim_funds = claim_funds + userfund.received
    if total_funds == Decimal("0.0"):
      return Decimal("0.0")
    return claim_funds / total_funds

  @property
  def url_details(self):
    return "/bounty/%s/claim/%s/%s" % (
      self.bounty.id, self.id, self.bounty.slug
    )

  @property
  def url_edit(self):
    return "/claim/%s/edit" % self.id

  @property
  def url_change_address(self):
    return "/claim/%s/change/address" % self.id

  @property
  def url_accept(self):
    return "/claim/%s/accept" % self.id

  @property
  def url_declare_winner(self):
    return "/claim/%s/declare/winner" % self.id

  def __unicode__(self):
    return "%i: %s - %s" % (self.id, self.user.username, str(self.successful))

  class Meta:
    unique_together = (("user", "bounty"),)
    ordering = ["created_on"]

class Accepted(Model):

  user = ForeignKey("auth.User", related_name="accepts")
  claim = ForeignKey("claim.Claim", related_name="accepts")

  # METADATA
  created_on = DateTimeField(auto_now_add=True)

  @property
  def weight(self):
    total = self.claim.bounty.received
    userfunds = self.claim.bounty.userfunds.filter(user=self.user)
    if len(userfunds) and total != Decimal("0.0"):
      return userfunds[0].received / total
    return Decimal("0.0")

  class Meta:
    unique_together = (("user", "claim"),)

