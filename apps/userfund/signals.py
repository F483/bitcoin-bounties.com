# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

import datetime
from django.dispatch import Signal
from django.dispatch import receiver
from apps.common.utils import email

cannot_refund = Signal(providing_args=["userfund"])
refunded = Signal(providing_args=["userfund", "payment"])

@receiver(cannot_refund)
def on_cannot_refund_email(sender, **kwargs):
  userfund = kwargs["userfund"]
  today = datetime.datetime.now().date()
  if userfund.remind_date: # user was reminded previously
    delay = 2 ** userfund.remind_count # exponential backoff avoid spamming
    next_remind_date = userfund.remind_date + datetime.timedelta(days=delay)
    if today < next_remind_date:
      return # to soon to remind user
  emails = [email.get_emailaddress_or_404(userfund.user)]
  subject = "userfund/email/cannot_refund_subject.txt"
  message = "userfund/email/cannot_refund_message.txt"
  email.send(emails, subject, message, kwargs)
  userfund.remind_count = userfund.remind_count + 1
  userfund.remind_date = today
  userfund.save()

@receiver(refunded)
def on_refunded_email(sender, **kwargs):
  emails = [email.get_emailaddress_or_404(kwargs["userfund"].user)]
  subject = "userfund/email/refunded_subject.txt"
  message = "userfund/email/refunded_message.txt"
  email.send(emails, subject, message, kwargs)

