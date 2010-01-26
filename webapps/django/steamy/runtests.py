#!/usr/bin/python
# -*- coding: utf8 -*-

from optparse import OptionParser
import unittest
import xmlrunner

from django.core.management import setup_environ
import settings
settings.DATABASE_ENGINE = "dummy"
setup_environ(settings)

from django.test.utils import setup_test_environment
from django.test.utils import teardown_test_environment

from debian.sparql.test import helperstest, visitortest
from debian.test import servicestest, functionaltest

class TestRunner:
  def __init__(self):
    self.out = None

  def config(self):
    parser = OptionParser()
    parser.add_option("-x", "--xml", action="store_true", dest="xml",\
                      default=False, help="switch to XML output")
    parser.add_option("-o", "--output", dest="output",\
                      metavar="FILE", help="dump XML to FILE")

    (self.opts, args) = parser.parse_args()

    if self.opts.output:
      self.out = open(self.opts.output, "w")

    return self

  def run(self):
    setup_test_environment()
    suite = unittest.TestLoader().loadTestsFromModule(helperstest)
    suite.addTests(unittest.TestLoader().loadTestsFromModule(visitortest))
    suite.addTests(unittest.TestLoader().loadTestsFromModule(servicestest))
    suite.addTests(unittest.TestLoader().loadTestsFromModule(functionaltest))
    if self.opts.xml:
      xmlrunner.XMLTestRunner(self.out).run(suite)
      if self.out:
        self.out.close()
    else:
      unittest.TextTestRunner(verbosity=2).run(suite)

    teardown_test_environment()

if __name__ == '__main__':
    TestRunner().config().run()
