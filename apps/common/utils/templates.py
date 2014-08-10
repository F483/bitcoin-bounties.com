# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from django.shortcuts import render_to_response
from django.template import RequestContext

def render_response(request, template, args):
  rc = RequestContext(request)
  return render_to_response(template, args, context_instance=rc)

