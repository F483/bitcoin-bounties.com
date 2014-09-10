# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

import os
from django.core.management.base import NoArgsCommand, CommandError
from apps.userfund.models import UserFund
from apps.userfund import signals
from apps.bounty.models import Bounty
from apps.claim.models import Claim
from config.settings import STOP_CRONS_FILE
from apps.asset import control as asset_control

class Command(NoArgsCommand):

  help = """Refund userfunds of failed bounties."""

  def process_refunds(self):
    userfunds = UserFund.objects.all()

    # exclude ongoing bounties
    ongoing_states = ['PENDING', 'ACTIVE', 'MEDIATION']
    ongoing_bounties = Bounty.objects.filter(state__in=ongoing_states)
    userfunds = userfunds.exclude(bounty__in=ongoing_bounties)

    # exclude successful bounties not yet payed 
    successful_claims = Claim.objects.filter(successful=True, payout=None)
    successful_bounties = Bounty.objects.filter(claims__in=successful_claims)
    userfunds = userfunds.exclude(bounty__in=successful_bounties)

    # exclude without funds
    userfunds = filter(lambda uf: uf.has_min_refund_amount, userfunds)

    # email users with refunds but no refund address
    for userfund in filter(lambda uf: not bool(uf.refund_address), userfunds):
      signals.cannot_refund.send(sender=self.process_refunds, userfund=userfund)

    # refund users
    for uf in filter(lambda uf: bool(uf.refund_address), userfunds):
      outputs = [{"destination" : uf.refund_address, "amount" : uf.torefund}]
      am = asset_control.get_manager(uf.bounty.asset)
      log = am.send(outputs).get(uf.refund_address)
      if log: # may not have sent if funds in wallet but not available
        uf.refund_payments.add(log)
        signals.refunded.send(
          sender=self.process_refunds, 
          userfund=uf, 
          payment={ # mock because counterpartyd can't get unconfirmed tx :(
            "amount" : outputs[0]["amount"],
            "address" : outputs[0]["destination"],
            "asset" : uf.bounty.asset,
          }, 
        )

  def handle_noargs(self, *args, **options):
    if os.path.isfile(STOP_CRONS_FILE):
      raise CommandError('Stop crons flag is set!')
    self.process_refunds()

