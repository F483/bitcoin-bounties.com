# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from decimal import Decimal
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from apps.common.utils.templates import render_response
from apps.bounty.models import Bounty
from apps.userfund.models import UserFund
from apps.common.utils import email

@login_required
@require_http_methods(['GET'])
def dashboard(request):
  user = request.user
  ongoing = ['PENDING', 'ACTIVE', 'MEDIATION']
  archived = ['FINISHED', 'CANCELLED', 'DELETED']

  invested = UserFund.objects.filter(user=user)
  invested = invested.exclude(cashed_funds_received=Decimal("0.0"))
  filters = Q(created_by=user) | Q(userfunds__in=invested)
  bounties = set(Bounty.objects.filter(filters).order_by('-deadline')) # XXX set

  claims = user.claims.select_related("bounty").all().order_by('-created_on')
  args = { 
    "primary_email" : email.get_emailaddress_or_404(user),
    "bounties_ongoing" : filter(lambda b: b.state in ongoing, bounties), 
    "bounties_archived" : filter(lambda b: b.state in archived, bounties), 
    "claims_ongoing" : filter(lambda c: c.bounty.state in ongoing, claims), 
    "claims_archived" : filter(lambda c: c.bounty.state in archived, claims), 
  }
  return render_response(request, 'accounts/dashboard.html', args)

