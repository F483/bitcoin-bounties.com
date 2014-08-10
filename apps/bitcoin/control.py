# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

import os
import datetime
import uuid
import bitcoinaddress
from decimal import Decimal, ROUND_DOWN
from bitcoinrpc.authproxy import AuthServiceProxy
from apps.common.utils.models import get_object_or_none
from apps.bitcoin.models import PaymentLog
from apps.bitcoin.models import ColdStorage
from apps.bitcoin import signals
from config import settings


#################
# BITCOIN UTILS #
#################

SATOSHI_PER_BTC = Decimal("100000000")
BTC_PER_SATOSHI = Decimal("0.00000001")

MBTC_PER_BTC = Decimal("1000")
BTC_PER_MBTC = Decimal("0.001")

def btc2mbtc(btc):
  return btc / BTC_PER_MBTC

def mbtc2btc(mbtc):
  return mbtc * BTC_PER_MBTC

def btc2satoshi(btc):
  return btc / BTC_PER_SATOSHI

def satoshi2btc(satoshi):
  return satoshi * BTC_PER_SATOSHI

def quantize_satoshi(btc):
  return btc.quantize(BTC_PER_SATOSHI, rounding=ROUND_DOWN)

def is_valid(address):
  return bitcoinaddress.validate(address)

def get_rpc_access():
  return AuthServiceProxy(settings.BITCOIND_RPC)


################
# COLD STORAGE #
################

def cold_storage_add(user, address):
  cs = ColdStorage()
  cs.address = address
  cs.created_by = user
  cs.updated_by = user
  cs.save()
  return cs

def cold_storage_send(amount):
  # TODO account for all bitcoind errors
  rpc = get_rpc_access()

  # get cold storage wallet
  coldstorages = ColdStorage.objects.filter(imported="")
  if len(coldstorages) == 0:
    raise Exception("No cold storage wallet!") # TODO custom Exception
  coldstorage = sorted(coldstorages, key=lambda cs: cs.received)[0]

  # send funds
  if amount > (rpc.getbalance() - settings.TRANSACTION_FEE_BUFFER):
    raise Exception("Not enough funds in hot wallet!") # TODO custom Exception
  txid = rpc.sendtoaddress(coldstorage.address, float(amount))
  txfee = rpc.gettransaction(txid)["fee"] * Decimal("-1.0")

  # correct accounts
  rpc.move(settings.ACCOUNT_COLDSTORAGE, "", float(amount))
  if txfee > Decimal("0.0"):
    rpc.move(settings.ACCOUNT_MAIN, "", float(txfee))

  # log payment
  log = PaymentLog()
  log.amount = amount
  log.account = ""
  log.address = coldstorage.address
  log.transaction = txid
  log.service_fee = Decimal("0.0")
  log.transaction_fee = txfee
  log.save()
  coldstorage.payments.add(log)

  return coldstorage

def cold_storage_import(user, private_key):
  # TODO account for all bitcoind errors
  rpc = get_rpc_access()

  # import private_key
  args = { "prefix" : settings.ACCOUNT_PREFIX, "id" : str(uuid.uuid4()) }
  account = "%(prefix)s_Import_%(id)s" % args
  rpc.importprivkey(private_key, account, False)
  address = rpc.getaddressesbyaccount(account)[0]

  # correct accounts
  amount = rpc.getbalance(account)
  if amount > Decimal("0.0"):
    rpc.move(account, settings.ACCOUNT_COLDSTORAGE, float(amount))

  # mark as imported
  coldstorage = get_object_or_none(ColdStorage, address=address) 
  if not coldstorage:
    args = (address, amount, account)
    raise Exception("IMPORTED UNKNOWN COLD STORAGE %s WITH %sBTC TO %s" % args)
  coldstorage.imported = account
  # TODO save private_key hash to be able to check if it was imported
  coldstorage.updated_by = user
  coldstorage.save()

############
# PAYMENTS #
############

def sufficient_hot_funds(rpc, src_accounts):
  available = rpc.getbalance()
  needed = sum(map(lambda a: rpc.getbalance(a), src_accounts))
  needed = needed - quantize_satoshi(needed * settings.FRACTION_FEES)
  return (available + settings.TRANSACTION_FEE_BUFFER) >= needed

def makepayment(src_accounts, address):
  # TODO account for all bitcoind errors
  rpc = get_rpc_access()

  # check if enough funds in hot wallet
  if not sufficient_hot_funds(rpc, src_accounts):
    signals.insufficent_hot_funds.send(sender=makepayment)
    raise Exception("INSUFFICIENT FUNDS IN HOT WALLET")

  # pool funds to avoid race condition with any incoming transactions
  args = { "prefix" : settings.ACCOUNT_PREFIX, "id" : str(uuid.uuid4()) }
  pool_account = "%(prefix)s_Payment_%(id)s" % args
  for src_account in src_accounts:
    src_balance = rpc.getbalance(src_account)
    if src_balance > Decimal("0.0"):
      rpc.move(src_account, pool_account, float(src_balance))

  # payment
  funds = rpc.getbalance(pool_account)
  fees = quantize_satoshi(funds * settings.FRACTION_FEES)
  amount = funds - fees
  txid = rpc.sendfrom(pool_account, address, float(amount))

  # collect fees
  service_fee = rpc.getbalance(pool_account)
  rpc.move(pool_account, settings.ACCOUNT_MAIN, float(service_fee))

  # log payment
  log = PaymentLog()
  log.amount = amount
  log.account = pool_account
  log.address = address
  log.transaction = txid
  log.service_fee = service_fee
  log.transaction_fee = fees - service_fee
  log.save()

  return log

#########
# FUNDS #
#########

def funds():
  from apps.userfund.models import UserFund

  # load data
  rpc = get_rpc_access()
  balances = rpc.listaccounts()
  userfunds = UserFund.objects.select_related('bounty') # join bounty
  userfunds = userfunds.only('id','bounty__state', 'bounty__deadline') # fields
  userfunds = userfunds.all().order_by("bounty__deadline") # order for range

  # helper functions
  getfraction = lambda a, b: b and (a / b) or Decimal("0.0")
  getbalance = lambda a: balances.get(a) and balances.get(a) or Decimal("0.0")
  
  # main funds
  funds_hot = sum(map(lambda ab: ab[1], balances.items()))
  funds_cold = getbalance(settings.ACCOUNT_COLDSTORAGE) * Decimal("-1.0")
  funds_total = funds_hot + funds_cold
  funds_company = getbalance(settings.ACCOUNT_MAIN)

  # bound userfunds and uncollected fees
  hot_range_ufinfo = [] # needed for range
  buf_pending = buf_active = buf_mediation = buf_archived = Decimal("0.0")
  ucf_pending = ucf_active = ucf_mediation = ucf_archived = Decimal("0.0")
  for userfund in userfunds:
    account = userfund.account
    balance = getbalance(userfund.account)
    uncollected_fees = quantize_satoshi(balance * settings.FRACTION_FEES)
    bound_userfunds = balance - uncollected_fees
    if userfund.bounty.state == "PENDING":
      buf_pending += bound_userfunds
      ucf_pending += uncollected_fees
    elif userfund.bounty.state == "ACTIVE":
      buf_active += bound_userfunds
      ucf_active += uncollected_fees
      hot_range_ufinfo.append((bound_userfunds, userfund.bounty.deadline))
    elif userfund.bounty.state == "MEDIATION":
      buf_mediation += bound_userfunds
      ucf_mediation += uncollected_fees
    else: # ARCHIVED
      buf_archived += bound_userfunds
      ucf_archived += uncollected_fees
  funds_buf = buf_pending + buf_active + buf_mediation + buf_archived
  funds_ucf = ucf_pending + ucf_active + ucf_mediation + ucf_archived

  funds = {
    "funds_hot" : funds_hot,
    "funds_cold" : funds_cold,
    "funds_company" : funds_company,
    "funds_total" : funds_total,
    "funds_bound_userfunds" : funds_buf,
    "funds_uncollected_fees" : funds_ucf,
    "fucf_pending" : getfraction(ucf_pending, funds_total),
    "fucf_active" : getfraction(ucf_active, funds_total),
    "fucf_mediation" : getfraction(ucf_mediation, funds_total),
    "fucf_archived" : getfraction(ucf_archived, funds_total),
    "fbuf_pending" : getfraction(buf_pending, funds_total),
    "fbuf_active" : getfraction(buf_active, funds_total),
    "fbuf_mediation" : getfraction(buf_mediation, funds_total),
    "fbuf_archived" : getfraction(buf_archived, funds_total),
    "fraction_hot" : getfraction(funds_hot, funds_total),
    "fraction_cold" : getfraction(funds_cold, funds_total),
    "fraction_company" : getfraction(funds_company, funds_total),
    "fraction_bound_userfunds" : getfraction(funds_buf, funds_total),
    "fraction_uncollected_fees" : getfraction(funds_ucf, funds_total),
    "coldstorages" : ColdStorage.objects.filter(imported=""),
  }
  return funds

##################
# EMERGENCY STOP #
##################

def emergencystop():
  rpc = get_rpc_access()

  # transfer funds to cold storage
  try:
    cold_storage_send(rpc.getbalance() - settings.TRANSACTION_FEE_BUFFER)
  except:
    pass # no cold storage wallet

  # stop bitcoind
  rpc.stop()

  # set stop_crons flag
  with open(settings.STOP_CRONS_FILE, 'a'):
    os.utime(settings.STOP_CRONS_FILE, None)

  # set emergencystop flag
  with open(settings.EMERGENCY_STOP_FILE, 'a'):
    os.utime(settings.EMERGENCY_STOP_FILE, None)


