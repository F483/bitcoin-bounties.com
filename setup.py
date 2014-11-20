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
  install_requires=[
    'Django==1.6',
    'Fuzzy==1.0',
    'Markdown==2.5',
    'Unidecode==0.04.16',
    'argparse==1.2.1',
    'bleach==1.4',
    'django-allauth==0.18.0',
    'django-bootstrap-form==3.1',
    'django-debug-toolbar==1.2.1',
    'django-pagination==1.0.7',
    'django-rosetta==0.7.4',
    'html4lib==0.999',
    'oauthlib==0.6.3',
    'polib==1.0.5', # because rosetta requires an old buggy version
    #'psycopg2==2.5.4', # only needed when using postgres
    'python-bitcoinaddress==0.2.2',
    'python-bitcoinrpc==0.1',
    'python-openid==1.2.5',
    'requests==2.4.1',
    'requests-oauthlib==0.4.1',
    'six==1.8.0',
    'sqlparse==0.1.11',
    'wsgiref==0.1.2',
  ],
  dependency_links=[],
  #test_suite="tests",
)


