import unittest

from models import VersionNumber

class VersionNumberTest(unittest.TestCase):
  
  def setUp(self):
    self.raw = "Test raw"
    self.baseURI = "http://debian.org/"
    self.vn = VersionNumber(self.raw, self.baseURI)
  
  def tearDown(self):
    pass

  def testInit(self):
    self.assertEqual(self.raw, self.vn.raw)
    self.assertEqual(self.baseURI, self.vn.baseURI)

  def testGetEpochIfUnset(self):
    self.assertEqual(self.vn.epoch, None)
    self.assertRaises(Exception, self.vn.getEpoch)

  def testGetEpochIfSet(self):
    self.vn.epoch = "1"
    self.assertEqual(self.vn.epoch, "1")
    self.assertEqual("1", self.vn.getEpoch())

  def testToString(self):
    self.vn.epoch = 0
    self.vn.upstreamVersion = "2.6+svn20080304"
    self.vn.debianRevision = "1.1"
    self.assertEqual("VersionNumber(epoch=0, upstream=2.6+svn20080304, debian=1.1)",\
                    str(self.vn))
