# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE.TXT file)

from decimal import Decimal

def chunks(l, n):
  """ Yield successive n-sized chunks from l. """
  for i in xrange(0, len(l), n):
    yield l[i:i+n]

def parts(l, n):
  """ Split a list into n parts. """
  return [ l[i::n] for i in xrange(n) ]

def fraction(a, b):
  return b and (a / b) or Decimal("0.0")
