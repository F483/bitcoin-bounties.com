# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from django.forms import Form
from django.forms import CharField
from django.forms import Textarea
from django.utils.translation import ugettext as _

class Comment(Form):

  text = CharField(
    label=_("COMMENT"), 
    widget=Textarea(attrs={'rows' : '3'})
  )

