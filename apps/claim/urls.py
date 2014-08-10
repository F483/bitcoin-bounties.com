# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from django.conf.urls import patterns, include, url
from apps.common.utils.urls import arg_id, arg_slug, SLUG

B = arg_id("bounty_id")
C = arg_id("claim_id")

urlpatterns = patterns('apps.claim.views',
  url(r'^create/%s$' % B,             'create'),
  url(r'^%s/edit$' % C,               'edit'),
  url(r'^%s/change/address$' % C,     'change_address'),
  url(r'^%s/accept$' % C,             'accept'),
  url(r'^%s/declare/winner$' % C,     'declare_winner'),
)

