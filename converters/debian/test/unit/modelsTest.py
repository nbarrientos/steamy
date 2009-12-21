import unittest

from debian_bundle.changelog import Version

from models import *

class VersionTest(unittest.TestCase):
  
  def setUp(self):
    self.versionStrings = ("1.0-1","1:1.2.5+svn20091203", "1.1-1.1")
  
  def tearDown(self):
    pass

  def testToStr(self):
    for v in self.versionStrings:
      versionObject = Version(v)
      self.assertEqual(v, str(versionObject))

class ArchitectureTest(unittest.TestCase):

  def setUp(self):
    self.arch = Architecture("i386")

  def testInit(self):
    self.assertEqual("i386", self.arch.name)

  def testAsUri(self):
    baseUri = "http://example.org"
    expected = baseUri + "/arch/i386"
    self.assertEqual(expected, self.arch.asUri(baseUri))
