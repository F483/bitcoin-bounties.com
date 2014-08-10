# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from django.dispatch import Signal
from django.dispatch import receiver
from apps.common.utils import email

deleted = Signal(providing_args=["bounty"])
unsuccessful = Signal(providing_args=["bounty"])
funding_timeout = Signal(providing_args=["bounty"])
activated = Signal(providing_args=["bounty"])
mediation = Signal(providing_args=["bounty"])

