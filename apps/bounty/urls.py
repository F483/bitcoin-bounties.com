# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from django.conf.urls import patterns, include, url
from apps.common.utils.urls import arg_id, arg_slug, SLUG

B = arg_id("bounty_id")
C = arg_id("claim_id")

urlpatterns = patterns('apps.bounty.views',
  url(r'^list/pending$',                  'list_pending'),
  url(r'^list/active$',                   'list_active'),
  url(r'^list/mediation$',                'list_mediation'),
  url(r'^list/archived$',                 'list_archived'),

  url(r'^create$',                        'create'),
  url(r'^deleted$',                       'deleted'),
  url(r'^%s/edit/%s$' % (B, SLUG),        'edit'),
  url(r'^%s/details/%s$' % (B, SLUG),     'details'),
  url(r'^%s/funds/%s$' % (B, SLUG),       'funds'),
  url(r'^%s/claim/%s/%s$' % (B, C, SLUG), 'claim'),
  url(r'^%s/claims/%s$' % (B, SLUG),      'claim'),
  url(r'^%s/comments/%s$' % (B, SLUG),    'comments'),
  url(r'^%s/makepublic/%s$' % (B, SLUG),  'make_public'),
  url(r'^%s/cancel/%s$' % (B, SLUG),      'cancel'),
  url(r'^%s/delete/%s$' % (B, SLUG),      'delete'),
  url(r'^%s/declare/unresolved$' % B,     'declare_unresolved'),
)
