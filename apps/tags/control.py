# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

import re
from apps.tags.models import Tag
from apps.common.utils.models import get_object_or_none

def valid_format(text):
  return bool(re.match("^[a-z]{3,20}$", text))

def tagsstr_to_taglist(tagsstr):
  tagsstr = tagsstr.replace("#", "") # remove hashtags
  tagsstr = tagsstr.lower() # only lower case
  taglist = tagsstr.split() # split by spaces
  return list(set(taglist)) # remove duplicates

def taglist_to_tagsstr(taglist):
  return " ".join(taglist)

def update(tagsstr):
  tags_strlist = tagsstr_to_taglist(tagsstr)
  tags = list(Tag.objects.filter(text__in=tags_strlist))
  existing_strlist = map(lambda tag: tag.text, tags)
  for tag_str in set(tags_strlist).difference(set(existing_strlist)):
    # TODO howto save in one query?
    tag = Tag()
    tag.text = tag_str
    tag.save()
    tags.append(tag)
  return tags


