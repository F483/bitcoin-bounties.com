# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>                  
# License: MIT (see LICENSE.TXT file) 

from django.conf.urls import patterns, include, url
from apps.common.utils.urls import arg_id, arg_slug

urlpatterns = patterns('apps.accounts.views',
  url(r'^profile/$', 'dashboard'),
)

