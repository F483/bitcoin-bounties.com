# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from django.contrib import admin
from apps.claim.models import Claim
from apps.claim.models import Accepted

admin.site.register(Claim)
admin.site.register(Accepted)

