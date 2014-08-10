# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>                  
# License: MIT (see LICENSE.TXT file) 

from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
import settings

admin.autodiscover()

urlpatterns = patterns('',

  # third party urls
  url(r"^admin/doc/", include("django.contrib.admindocs.urls")),
  url(r"^admin/", include(admin.site.urls)),
  url(r'^rosetta/', include('rosetta.urls')),
  url(r'^accounts/', include('allauth.urls')),

  # bitcoin bounties urls
  url(r"^$", 'apps.bounty.views.list_active'),
  url(r"^", include("apps.site.urls")),
  url(r"^bitcoin/", include("apps.bitcoin.urls")),
  url(r"^bounty/", include("apps.bounty.urls")),
  url(r"^comment/", include("apps.comment.urls")),
  url(r"^userfund/", include("apps.userfund.urls")),
  url(r"^claim/", include("apps.claim.urls")),
  url(r"^accounts/", include("apps.accounts.urls")),
)

if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

