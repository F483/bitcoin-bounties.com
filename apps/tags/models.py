# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from django.db.models import Model
from django.db.models import CharField

class Tag(Model):

  text = CharField(max_length=100, unique=True)

  def __unicode__(self):
    return self.text

