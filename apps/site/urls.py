# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>                  
# License: MIT (see LICENSE.TXT file) 

from django.utils.translation import ugettext as _
from django.conf.urls import patterns, include, url
from apps.common.utils.urls import arg_id, arg_slug

urlpatterns = patterns('apps.common.views',

  url(r'^terms$', 'render_template', { "template" : "site/terms.html" }),
  url(r'^about$', 'render_template', { "template" : "site/about.html" }),
  url(r'^contact$', 'render_template', { "template" : "site/contact.html" }),
  url(r'^faq$', 'render_template', { "template" : "site/faq.html" }),

)

