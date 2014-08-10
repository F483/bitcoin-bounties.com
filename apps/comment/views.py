# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from apps.common.utils.templates import render_response
from apps.comment.models import Comment
from apps.comment import control

@login_required
@require_http_methods(['GET', 'POST'])
def delete(request, comment_id):
  return_url = request.GET.get('next', '/')
  comment = get_object_or_404(Comment, id=comment_id)
  if request.method == "POST":
    control.delete(request.user, comment)
    return HttpResponseRedirect(return_url)
  args = {
    "form_title" : _("DELETE_COMMENT"),
    "form_alert_info" : mark_safe(_("DELETE_COMMENT_ALERT_INFO")),
    "cancel_url" : return_url,
  }
  return render_response(request, 'site/form.html', args)

