import unittest

from models import *
from parser import Parser

class ParserTest(unittest.TestCase):
  
  def setUp(self):
    self.parser = Parser()
    self.binaryPackage = {}
    self.binaryPackage['Package'] = "mutt"
    self.binaryPackage['Version'] = "1:2.4+svn5677-1"
    self.binaryPackage['Depends'] = "exim4 (>> 0.5.4-5) | mail-transport-agent, mutt"
    self.binaryPackage['Recommends'] = "locales, mime-support, bastet"
  
  def tearDown(self):
    pass

  # Fields

  def testParsePackage(self):
    self.assertEqual("mutt", self.parser.parsePackage(self.binaryPackage))

  def testParseDepends(self):
    deps = self.parser.parseDepends(self.binaryPackage)
    self.assertEqual(2, deps.len())
    
  # Tools

  def testParseVersionNumberNoEpoch(self):
    ver = self.parser.parseVersionNumber("1.0-1")
    self.assertEqual(None, ver.epoch)
    self.assertEqual("1.0", ver.upstream_version)
    self.assertEqual("1", ver.debian_version)

  def testParseVersionNumberEpoch(self):
    ver = self.parser.parseVersionNumber("1:1.0+svn20080909-1.1")
    self.assertEqual("1", ver.epoch)
    self.assertEqual("1.0+svn20080909", ver.upstream_version)
    self.assertEqual("1.1", ver.debian_version)

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
    input = "exim4 (>> 0.5.4-5) | mail-transport-agent | swaml"
    ord = self.parser.parseOrConstraint(input)
    self.assertEqual(3, len(ord.constraints))
    self.assertEqual("exim4", ord.get(0).package)
    self.assertEqual(">>", ord.get(0).operator)
    self.assertEqual("mail-transport-agent", ord.get(1).package)

  def testParseConstraintSimple(self):
    input = "libgnutls13"
    d = self.parser.parseConstraint(input)
    self.assertEqual(input, d.package)
    self.assertEqual(None, d.version)
  
  def testParseConstraintComplex(self):
    input = "libidn11 (>= 0.5.18)"
    d = self.parser.parseConstraint(input)
    self.assertEqual("libidn11", d.package)
    self.assertEqual(">=", d.operator)
    self.assertEqual(None, d.version.epoch)
    self.assertEqual("0.5.18", d.version.upstream_version)
    self.assertEqual(None, d.version.debian_version)
   
  # Full Package

  def testParseBinaryPackage(self):
    p = self.parser.parseBinaryPackage(self.binaryPackage)
    self.assertEqual("mutt", p.package)
    self.assertNotEqual(None, p.depends)
    self.assertEqual(2, p.depends.len())
    self.assertEqual(3, p.recommends.len())
    self.assertEqual("2.4+svn5677", p.version.upstream_version)
    self.assertEqual("1", p.version.debian_version)
