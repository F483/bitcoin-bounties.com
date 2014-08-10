# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from unidecode import unidecode
from django.template.defaultfilters import slugify

def uslugify(ustr):
  """ because slugify is shit with unicode """
  return slugify(unidecode(ustr))


