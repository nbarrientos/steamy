#!/usr/bin/python
# -*- coding: utf8 -*-

from distutils.core import setup

setup(name='dear',
      version='1.0alpha',
      description='DEbian Archive Rdfizer',
      author='Nacho Barrientos Arias',
      author_email='nacho@debian.org',
      py_modules=['decorators', 'parsers', 'export', 'errors', 'models', 'launcher'],
      scripts=['dear']
      )

