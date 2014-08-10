# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

import fuzzy
from unidecode import unidecode
from django.db.models import Q
from apps.search.models import Keyword
from apps.common.utils.models import get_object_or_none

_soundex = fuzzy.Soundex(4)

def _keyword_str_to_soundex(keyword_str):
  return _soundex(unidecode(keyword_str))

def _keywords_str_to_keyword_strlist(keywords_str):
  keywords_str = keywords_str.lower() # only lower case
  keywords_strlist = keywords_str.split() # split by spaces
  return list(set(keywords_strlist)) # remove duplicates

def _find(keywords_strlist):
  soundexlist = map(_keyword_str_to_soundex, keywords_strlist)
  textmatch = Q(text__in=keywords_strlist)
  soundexmatch = Q(soundex__in=soundexlist)
  return Keyword.objects.filter(textmatch | soundexmatch)

def find(keywords_str):
  return _find(_keywords_str_to_keyword_strlist(keywords_str))

def update(keywords_str):
  keywords_strlist = _keywords_str_to_keyword_strlist(keywords_str)
  keywords = list(_find(keywords_strlist))
  existing_strlist = map(lambda kw: kw.text, keywords)
  for keyword_str in set(keywords_strlist).difference(set(existing_strlist)):
    # TODO howto save in one query?
    keyword = Keyword()
    keyword.text = keyword_str
    keyword.soundex = _keyword_str_to_soundex(keyword_str)
    keyword.save()
    keywords.append(keyword)
  return keywords

