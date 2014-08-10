# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

import os
from django.core.management.base import NoArgsCommand, CommandError
from apps.userfund.models import UserFund
from apps.bitcoin import control as bitcoin_control
from config.settings import STOP_CRONS_FILE

class Command(NoArgsCommand):

  help = """Update userfund cashes"""

  def update_cashed_funds_received(self):
    rpc = bitcoin_control.get_rpc_access()
    for userfund in UserFund.objects.all():
      txlist = rpc.listtransactions(userfund.account)
      received = filter(lambda tx: tx['category'] == "receive", txlist)
      total = sum(map(lambda tx: tx['amount'], received))
      userfund.cashed_funds_received = total
      userfund.save()

  def handle_noargs(self, *args, **options):
    if os.path.isfile(STOP_CRONS_FILE):
      raise CommandError('Stop crons flag is set!')
    self.update_cashed_funds_received()

