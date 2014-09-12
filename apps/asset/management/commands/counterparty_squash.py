# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

import os
import datetime
from decimal import Decimal
from django.utils import timezone
from django.db.models import Q
from django.core.management.base import NoArgsCommand, CommandError
from config.settings import STOP_CRONS_FILE
from apps.common.utils.misc import parts
from apps.asset.managers.counterparty import counterpartyd_querry
from apps.asset.managers.counterparty import get_asset_names
from apps.asset import control
from apps.asset.models import PaymentLog
from apps.claim.models import Claim
from apps.userfund.models import UserFund

class Command(NoArgsCommand):

  help = """Squash counterparty asset addresses.
  Makes sure there are sufficient counterparty assets and btc in a single 
  address to cover payments.
  """

  def __init__(self, *args, **kwargs):
    super(Command, self).__init__(*args, **kwargs)
    self.bitcoinmanager = control.get_manager("BTC")
    self.dryrun = False

  def get_squash_number(self, asset):
    """ Returns: int((avg asset payouts per hour for last 24h) + 1) """
    # TODO test that it works properly
    yesterday = timezone.now() - datetime.timedelta(hours=24)
    in_payouts = Q(payouts__in=Claim.objects.filter(successful=True))
    in_refunds = Q(refunds__in=UserFund.objects.all())
    qs = PaymentLog.objects.filter(asset=asset, created_on__gte=yesterday)
    qs = qs.filter(in_payouts | in_refunds)
    return int((qs.count() / 24.0) + 1.0)

  def input_data(self):
    addresses = self.bitcoinmanager.get_wallet_addresses()
    assets = get_asset_names()
    needbtc = []
    squashable = dict(map(lambda a: (a, []), assets))
    for address in addresses:
      balances = counterpartyd_querry({
        "method": "get_balances",
        "params": {
          "filters": [
            {'field': 'address', 'op': '==', 'value': address},
          ]
        },
        "jsonrpc": "2.0",
        "id": 0,
      })['result']
      balances = filter(lambda b: b["quantity"] > Decimal("0.0"), balances)
      if not balances:
        continue
      btcneeded = Decimal("0.0005") * len(balances)
      btcbalance = self.bitcoinmanager.get_balance(address)
      if btcbalance < btcneeded:
        needbtc.append({
          "destination" : address, "amount" : btcneeded - btcbalance
        })
      else:
        for balance in balances:
          squashable[balance["asset"]].append(
            { "address" : address, "amount" : balance["quantity"]}
          )
    return needbtc, squashable

  def squash(self, asset, balances):
    am = control.get_manager(asset)
    squashto = self.get_squash_number(asset)
    balances = sorted(balances, key=lambda b: b["amount"], reverse=True)
    for balancespart in parts(balances, squashto):
      if len(balancespart) < 2:
        continue
      dest = balancespart[0]["address"]
      for balance in balancespart[1:]:
        print "SQUASH: %s %s @ %s > %s" % (
            balance["amount"], asset, balance["address"], dest
        )
        if not self.dryrun:
          am.counterpartysend(balance["address"], dest, balance["amount"])

  def handle_noargs(self, *args, **options):
    if os.path.isfile(STOP_CRONS_FILE):
      raise CommandError('Stop crons flag is set!')

    # needbtc = [{ "destination" : address, "amount" : amount }]
    # squashable = { "asset" : [{ "address" : address, "amount" : amount }] }
    needbtc, squashable = self.input_data()

    # squash asset addresses
    for asset, balances in squashable.items():
      self.squash(asset, balances)

    # make sure addresses have enough funds
    for need in needbtc:
      print "SEND NEEDED: %s BTC > %s" % (need["amount"], need["destination"])
    if not self.dryrun:
      self.bitcoinmanager.send(needbtc)

