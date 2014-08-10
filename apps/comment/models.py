# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from django.db.models import Model
from django.db.models import TextField
from django.db.models import DateTimeField
from django.db.models import ForeignKey

class Comment(Model):

  text = TextField()

  # METADATA
  created_on = DateTimeField(auto_now_add=True)
  created_by = ForeignKey('auth.User', related_name="comments")

  @property
  def url_delete(self):
    return "/comment/%s/delete" % self.id

  def __unicode__(self):
    return "%s %s" % (self.created_by, self.created_on)
