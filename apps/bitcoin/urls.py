# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>                  
# License: MIT (see LICENSE.TXT file) 

from django.conf.urls import patterns, include, url
from apps.common.utils.urls import arg_id, arg_slug

urlpatterns = patterns('apps.bitcoin.views',
  url(r'^funds$',               'funds'),
  url(r'^emergencystop$',       'emergencystop'),
  url(r'^coldstorage/add$',     'cold_storage_add'),
  url(r'^coldstorage/send$',    'cold_storage_send'),
  url(r'^coldstorage/import$',  'cold_storage_import'),
)


