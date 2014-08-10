# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>                  
# License: MIT (see LICENSE.TXT file) 

from django.conf.urls import patterns, include, url
from apps.common.utils.urls import arg_id, arg_slug, SLUG

B = arg_id("bounty_id")

urlpatterns = patterns('apps.userfund.views',
  url(r'^setrefund/%s$' % B,   'setrefund'),
)

