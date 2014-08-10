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
from apps.userfund import forms
from apps.userfund import control
from apps.bounty import control as bounty_control

@login_required
@require_http_methods(['GET', 'POST'])
def setrefund(request, bounty_id):
  bounty = bounty_control.get_or_404(request.user, bounty_id)
  userfund = control.get(request.user, bounty)
  if not control.can_fund(request.user, bounty):
    raise PermissionDenied
  if request.method == "POST":
    form = forms.SetRefund(request.POST, userfund=userfund)
    if form.is_valid():
      control.set_refund(
        request.user, bounty, form.cleaned_data["address"].strip()
      )
      return HttpResponseRedirect(bounty.url_funds)
  else:
    form = forms.SetRefund(userfund=userfund)
  args = { 
    "form" : form, "form_title" : _("SET_REFUND_ADDRESS"),
    "form_alert_info" : _("SET_REFUND_ADDRESS_ALERT_INFO"),
    "cancel_url" : bounty.url_funds,
  }
  return render_response(request, 'site/form.html', args)

