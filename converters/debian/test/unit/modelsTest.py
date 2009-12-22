import unittest

from models import *

class VersionNumberTest(unittest.TestCase):
  
  def testFieldParser(self):
    v = VersionNumber("2:1.2~svn54-1.5")
    self.assertEqual("2", v.epoch)
    self.assertEqual("1.2~svn54", v.upstream_version)
    self.assertEqual("1.5", v.debian_version)

  def testToStr(self):
    versionStrings = ("1.0-1","1:1.2.5+svn20091203", "1.1-1.1")
    for v in versionStrings:
      versionObject = VersionNumber(v)
      self.assertEqual(v, str(versionObject))

  def testAsURI(self):
    v = VersionNumber("1.0-1")
    baseURI = "http://example.org"
    expected = baseURI + "/version/1.0-1"
    self.assertEqual(expected, v.asURI(baseURI))

class ArchitectureTest(unittest.TestCase):

  def setUp(self):
    self.arch = Architecture("i386")

  def testInit(self):
    self.assertEqual("i386", self.arch.name)

  def testAsURI(self):
    baseURI = "http://example.org"
    expected = baseURI + "/arch/i386"
    self.assertEqual(expected, self.arch.asURI(baseURI))

  def testToStr(self):
    self.assertEqual("i386", str(self.arch))

class ConstraintTest(unittest.TestCase):

  def testAsURI(self):
    c = Constraint()
    c.package = "testpackage"
    c.operator = ">>"
    c.version = "2.5-2"

    baseURI = "http://example.org"
    expected = baseURI + "/constraint/" +\
               hashlib.sha1("testpackage>>2.5-2").hexdigest()

    self.assertEqual(expected, c.asURI(baseURI))
