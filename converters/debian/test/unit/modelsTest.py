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

  def testAsUri(self):
    v = VersionNumber("1.0-1")
    baseUri = "http://example.org"
    expected = baseUri + "/version/1.0-1"
    self.assertEqual(expected, v.asUri(baseUri))

class ArchitectureTest(unittest.TestCase):

  def setUp(self):
    self.arch = Architecture("i386")

  def testInit(self):
    self.assertEqual("i386", self.arch.name)

  def testAsUri(self):
    baseUri = "http://example.org"
    expected = baseUri + "/arch/i386"
    self.assertEqual(expected, self.arch.asUri(baseUri))

  def testToStr(self):
    self.assertEqual("i386", str(self.arch))
