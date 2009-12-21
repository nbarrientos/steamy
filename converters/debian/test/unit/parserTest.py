import unittest

from models import *
from parser import Parser

class ParserTest(unittest.TestCase):
  
  def setUp(self):
    self.parser = Parser()
    self.binaryPackage = {}
    self.binaryPackage['Package'] = "mutt"
    self.binaryPackage['Depends'] = "libgnutls13"
  
  def tearDown(self):
    pass

  # Fields

  def testParsePackage(self):
    self.assertEqual("mutt", self.parser.parsePackage(self.binaryPackage))

  def testParseDepends(self):
    pass
    
  # Tools

  def testParseConstraints(self):
    input = "exim4 (>> 0.5.4-5) | mail-transport-agent, mutt"
    ors = self.parser.parseConstraints(input)
    self.assertEqual(2, len(ors.orconstraints))
    self.assertEqual(2, len(ors.get(0).constraints))
    self.assertEqual("exim4", ors.get(0).get(0).package)
    self.assertEqual(">>", ors.get(0).get(0).operator)
    self.assertEqual("mail-transport-agent", ors.get(0).get(1).package)
    self.assertEqual("mutt", ors.get(1).get(0).package)

  def testParseOrConstraint(self):
    input = "exim4 (>> 0.5.4-5) | mail-transport-agent"
    ord = self.parser.parseOrConstraint(input)
    self.assertEqual(2, len(ord.constraints))
    self.assertEqual("exim4", ord.get(0).package)
    self.assertEqual(">>", ord.get(0).operator)
    self.assertEqual("mail-transport-agent", ord.get(1).package)

  def testParseConstraintSimple(self):
    input = "libgnutls13"
    d = self.parser.parseConstraint(input)
    self.assertEqual(input, d.package)
  
  def testParseConstraintComplex(self):
    input = "libidn11 (>= 0.5.18)"
    d = self.parser.parseConstraint(input)
    self.assertEqual("libidn11", d.package)
    self.assertEqual(">=", d.operator)
    #self.assertEqual(0, d.version.epoch) # FIXME
   
  # Full Packages

  def testParseBinaryPackage(self):
    p = self.parser.parseBinaryPackage(self.binaryPackage)
    self.assertEqual("mutt", p.package)
