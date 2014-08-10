# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

import os
import datetime
from decimal import Decimal
from django.core.management.base import NoArgsCommand, CommandError
from apps.bounty.models import Bounty
from apps.bounty import control
from apps.bounty import signals
from config.settings import STOP_CRONS_FILE

class Command(NoArgsCommand):

  help = """Update bounty states."""

  def handle_noargs(self, *args, **options):
    if os.path.isfile(STOP_CRONS_FILE):
      raise CommandError('Stop crons flag is set!')
    self.process_pending()
    self.process_active()
  
  def process_active(self):
    today = datetime.datetime.now().date()
    bounties = Bounty.objects.filter(state="ACTIVE", deadline__lt=today)
    for bounty in bounties:
      if len(bounty.claims.all()) == 0:
        bounty.state = "FINISHED"
        bounty.cashed_reward = bounty.display_reward # update cashe
        bounty.save()
        signals.unsuccessful.send(sender=self.process_active, bounty=bounty)
      else:
        bounty.state = "MEDIATION"
        bounty.cashed_reward = bounty.display_reward # update cashe
        bounty.save()
        signals.mediation.send(sender=self.process_active, bounty=bounty)
  
  def process_pending(self):
    today = datetime.datetime.now().date()
    bounties = Bounty.objects.filter(state="PENDING")
    for bounty in bounties:
      funded = bounty.funds_needed <= Decimal("0")
      funding_time_passed = today > bounty.deadline
      if not funding_time_passed and funded:
        bounty.state = "ACTIVE"
        bounty.cashed_reward = bounty.display_reward # update cashe
        bounty.save()
        signals.activated.send(sender=self.process_pending, bounty=bounty)
      elif funding_time_passed:
        bounty.state = "CANCELLED"
        bounty.cashed_reward = bounty.display_reward # update cashe
        bounty.cancelled_on = datetime.datetime.now()
        bounty.save()
        signals.funding_timeout.send(sender=self.process_pending, bounty=bounty)
  
