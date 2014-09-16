# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from decimal import Decimal
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from apps.common.utils.templates import render_response
from apps.asset import control
from apps.asset import forms

@require_http_methods(['GET'])
def overview(request):
  args = { "asset_chunks" : control.overview() }
  return render_response(request, 'asset/overview.html', args)

@require_http_methods(['GET'])
def coldstorage_view(request, asset):
  asset = asset.upper()
  args = { "asset" : control.details(asset) }
  return render_response(request, 'asset/coldstorage.html', args)

@require_http_methods(['GET'])
def hotwallet_view(request, asset):
  if not request.user.is_superuser:
    raise PermissionDenied
  asset = asset.upper()
  args = {
      "asset" : control.details(asset),
      "wallet" : control.get_hotwallet(asset)
  }
  return render_response(request, 'asset/hotwallet.html', args)

@login_required
@require_http_methods(['GET', 'POST'])
def coldstorage_add(request, asset):
  if not request.user.is_superuser:
    raise PermissionDenied
  cancel_url = reverse('asset_coldstorage_view', args=(asset,))
  asset = asset.upper()
  if request.method == "POST":
    form = forms.ColdStorageAdd(request.POST, asset=asset)
    if form.is_valid():
      control.cold_storage_add(
        request.user,
        asset,
        form.cleaned_data["address"].strip()
      )
      return HttpResponseRedirect(cancel_url)
  else:
    form = forms.ColdStorageAdd(asset=asset)
  args = {
    "form" : form,
    "form_title" : _("ADD_COLD_STORAGE_WALLET"),
    "cancel_url" : cancel_url,
  }
  return render_response(request, 'site/form.html', args)

@login_required
@require_http_methods(['GET', 'POST'])
def coldstorage_send(request, asset):
  if not request.user.is_superuser:
    raise PermissionDenied
  cancel_url = reverse('asset_coldstorage_view', args=(asset,))
  asset = asset.upper()
  if request.method == "POST":
    form = forms.ColdStorageSend(request.POST, asset=asset)
    if form.is_valid():
      control.cold_storage_send(asset, form.cleaned_data["amount"])
      return HttpResponseRedirect(cancel_url)
  else:
    form = forms.ColdStorageSend(asset=asset)
  args = {
    "form" : form,
    "form_title" : _("SEND_FUNDS_TO_COLD_STORAGE_WALLET"),
    "cancel_url" : cancel_url,
  }
  return render_response(request, 'site/form.html', args)

@login_required
@require_http_methods(['GET', 'POST'])
def coldstorage_import(request, asset):
  if not request.user.is_superuser:
    raise PermissionDenied
  cancel_url = reverse('asset_coldstorage_view', args=(asset,))
  asset = asset.upper()
  if request.method == "POST":
    form = forms.ColdStorageImport(request.POST)
    if form.is_valid():
      control.cold_storage_import(asset, form.cleaned_data["private_key"])
      return HttpResponseRedirect(cancel_url)
  else:
    form = forms.ColdStorageImport()
  args = {
    "form" : form,
    "form_title" : _("IMPORT_COLD_STORAGE_WALLET"),
    "cancel_url" : cancel_url,
  }
  return render_response(request, 'site/form.html', args)

@login_required
@require_http_methods(['GET', 'POST'])
def emergencystop(request):
  if not request.user.is_superuser:
    raise PermissionDenied
  if request.method == "POST":
    control.emergencystop()
    return render_response(request, 'asset/emergencystop.html', {})
  args = {
    "form_title" : _("EMERGENCY_STOP"),
    "form_alert_info" : mark_safe(_("EMERGENCY_STOP_INFO")),
    "cancel_url" : reverse('asset_overview', args=())
  }
  return render_response(request, 'site/form.html', args)

