# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

import os
from django.core.management.base import NoArgsCommand, CommandError
from apps.userfund.models import UserFund
from apps.asset import control as asset_control
from config.settings import STOP_CRONS_FILE

class Command(NoArgsCommand):

  help = """Update userfund cashes"""

  def update_cashed_funds_received(self):
    for userfund in UserFund.objects.all():
      am = asset_control.get_manager(userfund.bounty.asset)
      userfund.cashed_funds_received = am.get_received(userfund.funding_address)
      userfund.save()

  def handle_noargs(self, *args, **options):
    if os.path.isfile(STOP_CRONS_FILE):
      raise CommandError('Stop crons flag is set!')
    self.update_cashed_funds_received()

