# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

import os
from decimal import Decimal
from django.core.management.base import NoArgsCommand, CommandError
from apps.bitcoin import control as bitcoin_control
from apps.claim.models import Claim
from apps.claim import signals
from config.settings import STOP_CRONS_FILE

class Command(NoArgsCommand):

  help = """Payout successful claims."""

  def process_payouts(self):
    for claim in Claim.objects.filter(successful=True, payout=None):
      accounts = map(lambda uf: uf.account, claim.bounty.userfunds.all())
      claim.payout = bitcoin_control.makepayment(accounts, claim.address)
      claim.save()
      signals.payout.send(sender=self.process_payouts, claim=claim)

  def handle_noargs(self, *args, **options):
    if os.path.isfile(STOP_CRONS_FILE):
      raise CommandError('Stop crons flag is set!')
    self.process_payouts()

