# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

import os
from decimal import Decimal
from django.core.management.base import NoArgsCommand, CommandError
from apps.asset import control as asset_control
from apps.claim.models import Claim
from apps.claim import signals
from config.settings import STOP_CRONS_FILE

class Command(NoArgsCommand):

  help = """Payout successful claims."""

  def process_payouts(self):
    #claims = Claim.objects.filter(successful=True, payout=None)
    #address_claims = dict(map(lambda c: (c.address, c), claims))
    # TODO batch payments, split payments by asset
    for claim in Claim.objects.filter(successful=True, payout=None):
      am = asset_control.get_manager(claim.bounty.asset)
      reward = claim.bounty.reward
      address = claim.address
      claim.payout = am.send([(address, reward)])[address]
      claim.save()
      signals.payout.send(sender=self.process_payouts, claim=claim)

  def handle_noargs(self, *args, **options):
    if os.path.isfile(STOP_CRONS_FILE):
      raise CommandError('Stop crons flag is set!')
    self.process_payouts()

