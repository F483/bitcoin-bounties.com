# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from django.http import HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from apps.common.utils.templates import render_response

@require_http_methods(['GET'])
def render_template(request, template, context=None):
  return render_response(request, template, context and context or {})

@require_http_methods(['GET'])
def redirect_to(request, url):
  return HttpResponseRedirect(url)

