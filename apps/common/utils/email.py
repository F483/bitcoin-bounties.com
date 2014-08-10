# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.core.mail import send_mail as _send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from allauth.account.models import EmailAddress

def send(recipient_list, template_subject, template_message, context):
  # TODO add i18n templates for users prefered language
  # TODO use async mail queue
  site = context["site"] = Site.objects.get_current()
  sender = settings.DEFAULT_FROM_EMAIL
  subject = render_to_string(template_subject, context) # render subject
  subject = u" ".join(subject.splitlines()).strip() # remove newlines
  subject = u"[{site}] {subject}".format(site=site.name, subject=subject) # add prefix
  message = render_to_string(template_message, context).strip()
  return _send_mail(subject, message, sender, recipient_list)

def get_emailaddress_or_404(user):
  return get_object_or_404(EmailAddress, user=user, primary=True).email

