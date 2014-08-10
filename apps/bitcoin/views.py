# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from decimal import Decimal
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from apps.common.utils.templates import render_response
from apps.bitcoin import control
from apps.bitcoin import forms
from config.settings import ACCOUNT_COLDSTORAGE

@login_required
@require_http_methods(['GET'])
def emergencystop(request):
  if not request.user.is_superuser:
    raise PermissionDenied
  control.emergencystop()
  return render_response(request, 'bitcoin/emergencystop.html', {})

@require_http_methods(['GET'])
def funds(request):
  return render_response(request, 'bitcoin/funds.html', control.funds())

@login_required
@require_http_methods(['GET', 'POST'])
def cold_storage_add(request):
  if not request.user.is_superuser:
    raise PermissionDenied
  if request.method == "POST":
    form = forms.ColdStorageAdd(request.POST)
    if form.is_valid():
      control.cold_storage_add(
        request.user, 
        form.cleaned_data["address"].strip()
      )
      return HttpResponseRedirect("/bitcoin/funds")
  else:
    form = forms.ColdStorageAdd()
  args = {
    "form" : form, 
    "form_title" : _("ADD_COLD_STORAGE_WALLET"),
    "cancel_url" : "/bitcoin/funds",
  }
  return render_response(request, 'site/form.html', args)

@login_required
@require_http_methods(['GET', 'POST'])
def cold_storage_send(request):
  if not request.user.is_superuser:
    raise PermissionDenied
  if request.method == "POST":
    form = forms.ColdStorageSend(request.POST)
    if form.is_valid():
      control.cold_storage_send(form.cleaned_data["amount"])
      return HttpResponseRedirect("/bitcoin/funds")
  else:
    form = forms.ColdStorageSend()
  args = {
    "form" : form, 
    "form_title" : _("SEND_FUNDS_TO_COLD_STORAGE_WALLET"),
    "cancel_url" : "/bitcoin/funds",
  }
  return render_response(request, 'site/form.html', args)

@login_required
@require_http_methods(['GET', 'POST'])
def cold_storage_import(request):
  if not request.user.is_superuser:
    raise PermissionDenied
  if request.method == "POST":
    form = forms.ColdStorageImport(request.POST)
    if form.is_valid():
      control.cold_storage_import(
        request.user,
        form.cleaned_data["private_key"]
      )
      return HttpResponseRedirect("/bitcoin/funds")
  else:
    form = forms.ColdStorageImport()
  args = {
    "form" : form, 
    "form_title" : _("IMPORT_COLD_STORAGE_WALLET"),
    "cancel_url" : "/bitcoin/funds",
  }
  return render_response(request, 'site/form.html', args)

