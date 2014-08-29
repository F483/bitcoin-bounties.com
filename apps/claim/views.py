# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from apps.common.utils.templates import render_response
from apps.bounty import control as bounty_control
from apps.claim import forms
from apps.claim import control

@login_required
@require_http_methods(['GET', 'POST'])
def create(request, bounty_id):
  bounty = bounty_control.get_or_404(request.user, bounty_id)
  if not control.can_claim(request.user, bounty):
    raise PermissionDenied
  if request.method == "POST":
    form = forms.Create(request.POST, bounty=bounty)
    if form.is_valid():
      claim = control.create(
        request.user, bounty,
        form.cleaned_data["description"].strip(),
        form.cleaned_data["address"].strip()
      )
      return HttpResponseRedirect(claim.url_details)
  else:
    form = forms.Create(bounty=bounty)
  args = {
    "form" : form, "form_title" : _("CLAIM_BOUNTY"),
    "cancel_url" : bounty.url_details,
  }
  return render_response(request, 'site/form.html', args)

@login_required
@require_http_methods(['GET', 'POST'])
def edit(request, claim_id):
  claim = control.get_or_404(claim_id)
  if not control.can_edit(request.user, claim):
    raise PermissionDenied
  if request.method == "POST":
    form = forms.Edit(request.POST, claim=claim)
    if form.is_valid():
      claim = control.edit(
        request.user, claim,
        form.cleaned_data["description"].strip()
      )
      return HttpResponseRedirect(claim.url_details)
  else:
    form = forms.Edit(claim=claim)
  args = {
    "form" : form, "form_title" : _("EDIT_DESCRIPTION"),
    "cancel_url" : claim.url_details,
  }
  return render_response(request, 'site/form.html', args)

@login_required
@require_http_methods(['GET', 'POST'])
def change_address(request, claim_id):
  claim = control.get_or_404(claim_id)
  if not control.can_change_address(request.user, claim):
    raise PermissionDenied
  if request.method == "POST":
    form = forms.ChangeAddress(request.POST, claim=claim)
    if form.is_valid():
      claim = control.change_address(
        request.user, claim,
        form.cleaned_data["address"].strip()
      )
      return HttpResponseRedirect(claim.url_details)
  else:
    form = forms.ChangeAddress(claim=claim)
  args = {
    "form" : form, "form_title" : _("CHANGE_ADDRESS"),
    "cancel_url" : claim.url_details,
  }
  return render_response(request, 'site/form.html', args)

@login_required
@require_http_methods(['GET', 'POST'])
def accept(request, claim_id):
  claim = control.get_or_404(claim_id)
  if not control.can_accept(request.user, claim):
    raise PermissionDenied
  if request.method == "POST":
    claim = control.accept(request.user, claim)
    return HttpResponseRedirect(claim.url_details)
  if claim.bounty.cashed_claim_count == 1 and claim.bounty.private:
    args = {
      "form_title" : _("ACCEPT_CLAIM"),
      "form_alert_info" : _("ACCEPT_CLAIM_ALERT_INFO"),
      "cancel_url" : claim.url_details,
    }
  else:
    args = {
      "form_title" : _("APPROVE_CLAIM"),
      "form_alert_info" : _("APPROVE_CLAIM_ALERT_INFO"),
      "cancel_url" : claim.url_details,
    }
  return render_response(request, 'site/form.html', args)

@login_required
@require_http_methods(['GET', 'POST'])
def declare_winner(request, claim_id):
  claim = control.get_or_404(claim_id)
  if not control.can_declare_winner(request.user, claim):
    raise PermissionDenied
  if request.method == "POST":
    claim = control.declare_winner(request.user, claim)
    return HttpResponseRedirect(claim.url_details)
  args = {
    "form_title" : _("DECLARE_WINNER"),
    "form_alert_info" : _("DECLARE_WINNER_ALERT_INFO"),
    "cancel_url" : claim.url_details,
  }
  return render_response(request, 'site/form.html', args)

