# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from django.contrib import admin
from apps.bitcoin.models import PaymentLog
from apps.bitcoin.models import ColdStorage

admin.site.register(PaymentLog)
admin.site.register(ColdStorage)

