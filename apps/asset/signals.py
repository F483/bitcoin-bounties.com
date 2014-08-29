# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from django.dispatch import Signal
from django.dispatch import receiver
from apps.common.utils import email
from django.contrib.auth.models import User

insufficent_hot_funds = Signal(providing_args=["asset"])

@receiver(insufficent_hot_funds)
def on_insufficent_hot_funds_emails(sender, **kwargs):
  superusers = User.objects.filter(is_superuser=True)
  emails = map(lambda u: email.get_emailaddress_or_404(u), superusers)
  subject = "asset/email/insufficent_hot_funds_subject.txt"
  message = "asset/email/insufficent_hot_funds_message.txt"
  email.send(emails, subject, message, kwargs)

