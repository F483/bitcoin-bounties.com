# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from django.db.models import Model
from django.db.models import CharField

class Keyword(Model):

  text = CharField(max_length=100, unique=True)
  soundex = CharField(max_length=100)

  def __unicode__(self):
    return "%i: %s %s" % (self.id, self.soundex, self.text)

