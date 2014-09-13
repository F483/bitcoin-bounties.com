# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>                  
# License: MIT (see LICENSE.TXT file) 

from django.conf.urls import patterns, include, url
from apps.common.utils.urls import arg_id, arg_slug

A = arg_slug("asset")

urlpatterns = patterns('apps.asset.views',
  url(
    r'^overview$',
    'overview',
    name="asset_overview",
  ),
#  url(
#    r'^emergencystop$' % A,         
#    'emergencystop'
#  ),
  url(
    r'^%s/details$' % A,             
    'details',
    name="asset_details",
  ),
  url(
    r'^%s/coldstorage/add$' % A,    
    'coldstorage_add', 
    name="asset_coldstorage_add",
  ),
  url(
    r'^%s/coldstorage/send$' % A,   
    'coldstorage_send', 
    name="asset_coldstorage_send",
  ),
  url(
    r'^%s/coldstorage/import$' % A, 
    'coldstorage_import', 
    name="asset_coldstorage_import",
  ),
)


