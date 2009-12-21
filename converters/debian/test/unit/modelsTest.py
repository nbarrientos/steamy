import unittest

from models import VersionNumber

class VersionNumberTest(unittest.TestCase):
  
  def setUp(self):
    self.raw = "1:2.6-1"
    self.baseURI = "http://debian.org/"
    self.vn = VersionNumber(self.baseURI)
  
  def tearDown(self):
    pass

  def testInit(self):
    self.assertEqual(self.baseURI, self.vn.baseURI)

  def testToString(self):
    self.vn.epoch = 0
    self.vn.upstreamVersion = "2.6+svn20080304"
    self.vn.debianRevision = "1.1"
    self.assertEqual("VersionNumber(epoch=0, upstream=2.6+svn20080304, debian=1.1)",\
                    str(self.vn))
