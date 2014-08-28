# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from django.utils.safestring import mark_safe
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from apps.common.utils.templates import render_response
from apps.common.utils.models import get_object_or_none
from apps.common.utils.misc import chunks
from apps.bounty.models import Bounty
from apps.bounty import forms
from apps.bounty import control
from apps.claim.models import Claim
from apps.comment import forms as comment_forms
from apps.userfund import control as uf_control
from apps.claim import control as claim_control
from apps.search import control as search_control

####################
# BOUNTY VIEW TABS #
####################

def _view_tabs(user, bounty, active):
  details = {
    "icon_classes" : "fa fa-file-text",
    "label" : _("DETAILS"),
    "url" : bounty.url_details,
    "active" : active == "DETAILS"
  }
  funds = {
    "icon_classes" : "fa fa-bitcoin",
    "label" : _("FUNDS"),
    "url" : bounty.url_funds,
    "active" : active == "FUNDS"
  }
  claims = {
    "icon_classes" : "fa fa-hand-o-up",
    "label" : _("CLAIMS"),
    "badge" : "%s" % bounty.cashed_claim_count,
    "url" : bounty.url_claims,
    "active" : active == "CLAIMS"
  }
  comments = {
    "icon_classes" : "fa fa-comments",
    "label" : _("COMMENTS"),
    "badge" : "%s" % len(bounty.comments.all()),
    "url" : bounty.url_comments,
    "active" : active == "COMMENTS"
  }
  can_view_claims = claim_control.can_view_claims(user, bounty)
  if bounty.state == "PENDING" or not can_view_claims:
    return [details, funds, comments]
  else:
    return [details, funds, claims, comments]


###########################
# BOUNTY SEARCH LIST TABS #
###########################

def _list_tabs(active):
  return [
    {
      "icon_classes" : "fa fa-spinner",
      "label" : _("PENDING"),
      "url" : "/bounty/list/pending",
      "active" : active == "PENDING"
    },
    {
      "icon_classes" : "fa fa-bitcoin",
      "label" : _("ACTIVE"),
      "url" : "/bounty/list/active",
      "active" : active == "ACTIVE"
    },
    {
      "icon_classes" : "fa fa-gavel",
      "label" : _("MEDIATION"),
      "url" : "/bounty/list/mediation",
      "active" : active == "MEDIATION"
    },
    {
      "icon_classes" : "fa fa-archive",
      "label" : _("ARCHIVED"),
      "url" : "/bounty/list/archived",
      "active" : active == "ARCHIVED"
    },
   ]


################
# PENDING LIST #
################

def _filter_pending(bounties, search, ordering):

  if search.strip():
    bounties = bounties.filter(keywords__in=search_control.find(search))

  # ordering
  if ordering == 'REWARD_HIGHEST':
    bounties = bounties.order_by("-target_reward")
  elif ordering == 'REWARD_LOWEST':
    bounties = bounties.order_by("target_reward")
  elif ordering == 'DEADLINE_FARTHEST':
    bounties = bounties.order_by("-deadline")
  elif ordering == 'DEADLINE_NEAREST':
    bounties = bounties.order_by("deadline")
  elif ordering == 'NEWEST_BOUNTY':
    bounties = bounties.order_by("-created_on")
  elif ordering == 'OLDEST_BOUNTY':
    bounties = bounties.order_by("created_on")

  return bounties

@require_http_methods(['GET', 'POST'])
def list_pending(request):
  bounties = Bounty.objects.filter(state="PENDING")
  if request.method == "POST":
    form = forms.FilterPending(request.POST)
    if form.is_valid():
      bounties = _filter_pending(
        bounties,
        form.cleaned_data["searchtext"].strip(),
        form.cleaned_data["ordering"]
      )
  else:
    form = forms.FilterPending()
    bounties = _filter_pending(bounties, "", "REWARD_HIGHEST")
  args = {
    "list_type" : "PENDING",
    "bounties" : bounties[:20],
    "tabs" : _list_tabs("PENDING"),
    "navbar_active" : "BROWSE",
    "form" : form,
  }
  return render_response(request, 'bounty/list.html', args)


###############
# ACTIVE LIST #
###############

def _filter_active(bounties, search, claims, ordering):

  if search.strip():
    bounties = bounties.filter(keywords__in=search_control.find(search))

  # claims
  if claims == "ANY_CLAIMS":
    pass # don't filter
  elif claims == "NO_CLAIMS":
    bounties = bounties.exclude(cashed_claim_count__gt=0)
  elif claims == "HAS_CLAIMS":
    bounties = bounties.exclude(cashed_claim_count=0)

  # ordering
  if ordering == 'REWARD_HIGHEST':
    bounties = bounties.order_by("-cashed_reward")
  elif ordering == 'REWARD_LOWEST':
    bounties = bounties.order_by("cashed_reward")
  elif ordering == 'DEADLINE_FARTHEST':
    bounties = bounties.order_by("-deadline")
  elif ordering == 'DEADLINE_NEAREST':
    bounties = bounties.order_by("deadline")
  elif ordering == 'NEWEST_BOUNTY':
    bounties = bounties.order_by("-created_on")
  elif ordering == 'OLDEST_BOUNTY':
    bounties = bounties.order_by("created_on")

  return bounties

@require_http_methods(['GET', 'POST'])
def list_active(request):
  bounties = Bounty.objects.filter(state="ACTIVE")
  if request.method == "POST":
    form = forms.FilterActive(request.POST)
    if form.is_valid():
      bounties = _filter_active(
        bounties,
        form.cleaned_data["searchtext"],
        form.cleaned_data["claims"],
        form.cleaned_data["ordering"]
      )
  else:
    form = forms.FilterActive()
    bounties = _filter_active(bounties, "", "ANY_CLAIMS", "REWARD_HIGHEST")
  args = {
    "list_type" : "ACTIVE",
    "bounties" : bounties[:20],
    "tabs" : _list_tabs("ACTIVE"),
    "navbar_active" : "BROWSE",
    "form" : form,
  }
  return render_response(request, 'bounty/list.html', args)


##################
# MEDIATION LIST #
##################

def _filter_mediation(bounties, search, ordering):

  if search.strip():
    bounties = bounties.filter(keywords__in=search_control.find(search))

  # ordering
  if ordering == 'REWARD_HIGHEST':
    bounties = bounties.order_by("-cashed_reward")
  elif ordering == 'REWARD_LOWEST':
    bounties = bounties.order_by("cashed_reward")
  elif ordering == 'DEADLINE_NEAREST':
    bounties = bounties.order_by("deadline")
  elif ordering == 'DEADLINE_FARTHEST':
    bounties = bounties.order_by("-deadline")

  return bounties

@require_http_methods(['GET', 'POST'])
def list_mediation(request):
  bounties = Bounty.objects.filter(state="MEDIATION")
  if request.method == "POST":
    form = forms.FilterMediation(request.POST)
    if form.is_valid():
      bounties = _filter_mediation(
        bounties,
        form.cleaned_data["searchtext"],
        form.cleaned_data["ordering"]
      )
  else:
    form = forms.FilterMediation()
    bounties = _filter_mediation(bounties, "", "DEADLINE_NEAREST")
  args = {
    "list_type" : "MEDIATION",
    "bounties" : bounties[:20],
    "tabs" : _list_tabs("MEDIATION"),
    "navbar_active" : "BROWSE",
    "form" : form,
  }
  return render_response(request, 'bounty/list.html', args)


#################
# ARCHIVED LIST #
#################

def _filter_archived(bounties, search, date_from, date_to, outcome, ordering):

  if search.strip():
    bounties = bounties.filter(keywords__in=search_control.find(search))

  # filter deadline date_from date_to
  if date_from:
    bounties = bounties.exclude(deadline__lt=date_from)
  if date_to:
    bounties = bounties.exclude(deadline__gt=date_to)

  # outcome
  if outcome == 'ANY_OUTCOME':
    pass # don't filter
  if outcome == 'REWARDED':
    claims = Claim.objects.filter(successful=True)
    bounties = bounties.filter(state="FINISHED")
    bounties = bounties.filter(claims__in=claims)
  if outcome == 'UNREWARDED':
    claims = Claim.objects.filter(successful=True)
    bounties = bounties.filter(state="FINISHED")
    bounties = bounties.exclude(claims__in=claims)
  if outcome == 'CANCELLED':
    bounties = bounties.filter(state="CANCELLED")

  # ordering
  if ordering == 'REWARD_HIGHEST':
    bounties = bounties.order_by("-cashed_reward")
  elif ordering == 'REWARD_LOWEST':
    bounties = bounties.order_by("cashed_reward")
  elif ordering == 'NEWEST_BOUNTY':
    bounties = bounties.order_by("-created_on")
  elif ordering == 'OLDEST_BOUNTY':
    bounties = bounties.order_by("created_on")

  return bounties

@require_http_methods(['GET', 'POST'])
def list_archived(request):
  bounties = Bounty.objects.filter(state__in=["FINISHED", "CANCELLED"])
  if request.method == "POST":
    form = forms.FilterArchived(request.POST)
    if form.is_valid():
      bounties = _filter_archived(
        bounties,
        form.cleaned_data["searchtext"],
        form.cleaned_data["date_from"],
        form.cleaned_data["date_to"],
        form.cleaned_data["outcome"],
        form.cleaned_data["ordering"]
      )
  else:
    form = forms.FilterArchived()
    bounties = _filter_archived(
      bounties, "", None, None, "ANY_OUTCOME", "NEWEST_BOUNTY"
    )
  args = {
    "list_type" : "ARCHIVED",
    "bounties" : bounties[:20],
    "tabs" : _list_tabs("ARCHIVED"),
    "navbar_active" : "BROWSE",
    "form" : form,
  }
  return render_response(request, 'bounty/list.html', args)


###############
# EDIT BOUNTY #
###############

@login_required
@require_http_methods(['GET', 'POST'])
def edit(request, bounty_id):
  bounty = control.get_or_404(request.user, bounty_id)
  if not control.can_edit(request.user, bounty):
    raise PermissionDenied
  if request.method == "POST":
    form = forms.EditBounty(request.POST, bounty=bounty)
    if form.is_valid():
      bounty = control.edit(
        request.user, bounty,
        form.cleaned_data["title"].strip(),
        form.cleaned_data["description"].strip(),
        form.cleaned_data["tags"].strip(),
        bitcoin_control.mbtc2btc(form.cleaned_data["target"]),
        form.cleaned_data["deadline"]
      )
      return HttpResponseRedirect(bounty.url_details)
  else:
    form = forms.EditBounty(bounty=bounty)
  args = {
    "form" : form, "form_title" : _("EDIT_BOUNTY"),
    "cancel_url" : bounty.url_details,
  }
  return render_response(request, 'site/form.html', args)

@login_required
@require_http_methods(['GET', 'POST'])
def create(request):
  if request.method == "POST":
    form = forms.CreateBounty(request.POST)
    if form.is_valid():
      bounty = control.create(
        request.user,
        form.cleaned_data["title"].strip(),
        form.cleaned_data["description"].strip(),
        form.cleaned_data["tags"].strip(),
        bitcoin_control.mbtc2btc(form.cleaned_data["target"]),
        form.cleaned_data["deadline"]
      )
      return HttpResponseRedirect(bounty.url_funds)
  else:
    form = forms.CreateBounty()
  args = {
    "form" : form, "form_title" : _("CREATE_BOUNTY"),
    "cancel_url" : "/",
    "navbar_active" : "CREATE",
  }
  return render_response(request, 'site/form.html', args)

@require_http_methods(['GET', 'POST'])
def comments(request, bounty_id):
  bounty = control.get_or_404(request.user, bounty_id)
  form = None
  if control.can_comment(request.user, bounty):
    if request.method == "POST":
      form = comment_forms.Comment(request.POST)
      if form.is_valid():
        bounty = control.comment(
          request.user, bounty, form.cleaned_data["text"].strip()
        )
        return HttpResponseRedirect(bounty.url_comments)
    else:
      form = comment_forms.Comment()
  tabs = _view_tabs(request.user, bounty, "COMMENTS")
  args = { "bounty" : bounty, "tabs" : tabs, "form" : form }
  return render_response(request, 'bounty/view/comments.html', args)

@require_http_methods(['GET'])
def details(request, bounty_id):
  bounty = control.get_or_404(request.user, bounty_id)
  tabs = _view_tabs(request.user, bounty, "DETAILS")
  args = { "bounty" : bounty, "tabs" : tabs }
  return render_response(request, 'bounty/view/details.html', args)

@require_http_methods(['GET'])
def funds(request, bounty_id):
  bounty = control.get_or_404(request.user, bounty_id)
  loggedin = request.user.is_authenticated()
  args = {
    "userfund" : loggedin and uf_control.get(request.user, bounty) or None,
    "bounty" : bounty, "tabs" : _view_tabs(request.user, bounty, "FUNDS"),
  }
  return render_response(request, 'bounty/view/funds.html', args)

@require_http_methods(['GET', 'POST'])
def claim(request, bounty_id, claim_id=None):
  bounty = control.get_or_404(request.user, bounty_id)
  if not claim_control.can_view_claims(request.user, bounty):
    raise PermissionDenied
  claims = bounty.claims.all()

  # get selected claim
  claim = None
  if claim_id:
    claim = get_object_or_404(Claim, id=claim_id, bounty=bounty)
  if not claim and len(claims) > 0: # set default claim when none given
    if request.user.is_authenticated(): # default to users claim if it exists
      claim = get_object_or_none(Claim, bounty=bounty, user=request.user)
    if not claim: # default to first claim if user does not have a claim
      claim = claims[0]

  # save comment
  form = None
  if claim and claim_control.can_comment(request.user, claim):
    if request.method == "POST":
      form = comment_forms.Comment(request.POST)
      if form.is_valid():
        claim = claim_control.comment(
          request.user, claim, form.cleaned_data["text"].strip()
        )
        return HttpResponseRedirect(claim.url_details)
    else:
      form = comment_forms.Comment()

  tabs = _view_tabs(request.user, bounty, "CLAIMS")
  args = {
    "tabs" : tabs, "bounty" : bounty, "claim" : claim,
    "claims" : claims, "form" : form
  }
  return render_response(request, 'bounty/view/claims.html', args)

@login_required
@require_http_methods(['GET', 'POST'])
def make_public(request, bounty_id):
  bounty = control.get_or_404(request.user, bounty_id)
  if request.method == "POST":
    bounty = control.make_public(request.user, bounty)
    return HttpResponseRedirect(bounty.url_details)
  args = {
    "form_title" : _("MAKE_BOUNTY_PUBLIC"),
    "form_alert_info" : mark_safe(_("MAKE_BOUNTY_PUBLIC_ALERT_INFO")),
    "cancel_url" : bounty.url_details,
  }
  return render_response(request, 'site/form.html', args)

@login_required
@require_http_methods(['GET', 'POST'])
def cancel(request, bounty_id):
  bounty = control.get_or_404(request.user, bounty_id)
  if request.method == "POST":
    bounty = control.cancel(request.user, bounty)
    return HttpResponseRedirect(bounty.url_details)
  args = {
    "form_title" : _("CANCEL_BOUNTY"),
    "form_alert_info" : mark_safe(_("CANCEL_BOUNTY_ALERT_INFO")),
    "cancel_url" : bounty.url_details,
  }
  return render_response(request, 'site/form.html', args)

@login_required
@require_http_methods(['GET', 'POST'])
def declare_unresolved(request, bounty_id):
  bounty = control.get_or_404(request.user, bounty_id)
  if request.method == "POST":
    bounty = control.declare_unresolved(request.user, bounty)
    return HttpResponseRedirect(bounty.url_details)
  args = {
    "form_title" : _("DECLARE_UNRESOLVED"),
    "form_alert_info" : mark_safe(_("DECLARE_UNRESOLVED_ALERT_INFO")),
    "cancel_url" : bounty.url_details,
  }
  return render_response(request, 'site/form.html', args)

@login_required
@require_http_methods(['GET', 'POST'])
def delete(request, bounty_id):
  bounty = control.get_or_404(request.user, bounty_id)
  if request.method == "POST":
    bounty = control.delete(request.user, bounty)
    return HttpResponseRedirect("/bounty/deleted")
  args = {
    "form_title" : _("DELETE_BOUNTY"),
    "form_alert_info" : mark_safe(_("DELETE_BOUNTY_ALERT_INFO")),
    "cancel_url" : bounty.url_details,
  }
  return render_response(request, 'site/form.html', args)

@login_required
@require_http_methods(['GET'])
def deleted(request):
  return render_response(request, 'bounty/deleted.html', {})

