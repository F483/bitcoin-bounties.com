# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from django.dispatch import Signal
from django.dispatch import receiver
from apps.common.utils import email

successful = Signal(providing_args=["claim"])
created = Signal(providing_args=["claim"])
payout = Signal(providing_args=["claim"])

def _investor_emails(claim):
  is_investor = lambda uf: uf.user == claim.bounty.created_by or uf.received
  userfunds = filter(is_investor, claim.bounty.userfunds.all())
  return map(lambda uf: email.get_emailaddress_or_404(uf.user), userfunds)

@receiver(successful)
def on_successful_email_winning_claimant(sender, **kwargs):
  emails = [email.get_emailaddress_or_404(kwargs["claim"].user)]
  subject = "claim/email/winning_claimant_subject.txt"
  message = "claim/email/winning_claimant_message.txt"
  email.send(emails, subject, message, kwargs)

@receiver(payout)
def on_payout_email(sender, **kwargs):
  emails = [email.get_emailaddress_or_404(kwargs["claim"].user)]
  subject = "claim/email/payout_subject.txt"
  message = "claim/email/payout_message.txt"
  email.send(emails, subject, message, kwargs)

@receiver(successful)
def on_successful_email_investors(sender, **kwargs):
  emails = _investor_emails(kwargs["claim"])
  subject = "claim/email/successful_investors_subject.txt"
  message = "claim/email/successful_investors_message.txt"
  email.send(emails, subject, message, kwargs)

@receiver(created)
def on_created_email_investors(sender, **kwargs):
  emails = _investor_emails(kwargs["claim"])
  subject = "claim/email/created_investors_subject.txt"
  message = "claim/email/created_investors_message.txt"
  email.send(emails, subject, message, kwargs)

