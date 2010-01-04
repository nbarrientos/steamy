#!/usr/bin/python
# -*- coding: utf8 -*-

from distutils.core import setup

setup(name='romeo',
      version='1.0alpha',
      description='RDFizer for Debian Packages Archive',
      author='Nacho Barrientos Arias',
      author_email='nacho@debian.org',
      py_modules=['decorators', 'parsers', 'export', 'errors', 'models', 'launcher'],
      scripts=['romeo']
      )

