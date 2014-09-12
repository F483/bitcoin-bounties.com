# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

import os
import datetime
from decimal import Decimal
from django.core.management.base import NoArgsCommand, CommandError
from apps.bounty.models import Bounty
from apps.bounty import control
from config.settings import STOP_CRONS_FILE

class Command(NoArgsCommand):

  help = """Update bounty.cashed_reward.
  Only updated for active bounties where funds are change often asynchronously.
  """

  def update_cashed_reward(self):
    bounties = Bounty.objects.filter(state="ACTIVE")
    for bounty in bounties:
      if bounty.display_reward > bounty.cashed_reward:
        bounty.cashed_reward = bounty.display_reward
        bounty.save()

  def handle_noargs(self, *args, **options):
    if os.path.isfile(STOP_CRONS_FILE):
      raise CommandError('Stop crons flag is set!')
    self.update_cashed_reward()

