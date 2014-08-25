#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014 Fabian Barkhau <fabian.barkhau@gmail.com>                  
# License: MIT (see LICENSE.TXT file) 

from os import path
from setuptools import setup, find_packages

with open(path.join(path.abspath(path.dirname(__file__)), 'README.md')) as f:
  README = f.read()

setup(
  name='bitcoin-bounties',
  license = "MIT",
  author='Fabian Barkhau',
  author_email='fabian.barkhau@gmail.com',
  maintainer='Fabian Barkhau',
  maintainer_email='fabian.barkhau@gmail.com',
  version='1.0.0',
  description='Place and collect bounties in bitcoin.',
  long_description=README,
  classifiers=["Programming Language :: Python"],
  url='https://bitcoin-bounties.com',
  keywords='bitcoin bounties',
  packages=find_packages(),
  include_package_data=True,
  zip_safe=False,
  install_requires=[ # TODO add newest tested versions and use virtualenv !
    'Markdown',
    'bleach',
    'Unidecode',
    'Fuzzy',
    'python-bitcoinrpc',
    'python-bitcoinaddress',
    'django-rosetta',
    'django-bootstrap-form',
    'django-pagination',
    'django-allauth',
    'Django',
  ],
  dependency_links=[],
  #test_suite="tests",
)

