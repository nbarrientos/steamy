import unittest

from models import *

class VersionNumberTest(unittest.TestCase):
  def testFieldParser(self):
    v = VersionNumber("2:1.2~svn54-1.5")
    self.assertEqual("2", v.epoch)
    self.assertEqual("1.2~svn54", v.upstream_version)
    self.assertEqual("1.5", v.debian_version)

    v = VersionNumber("1.2")
    self.assertEqual(None, v.epoch)
    self.assertEqual("1.2", v.upstream_version)
    self.assertEqual(None, v.debian_version)

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

  def testComparable(self):
    v1 = VersionNumber("1.0-1")
    v2 = VersionNumber("1.0-2")
    v3 = VersionNumber("1.1-1")
    v4 = VersionNumber("1:1.0-1")
    v5 = VersionNumber("1.0-1.1")
    v6 = VersionNumber("1.0+svn1-1")

    self.assertTrue(v1 == v1)
    self.assertTrue(v1 < v2)
    self.assertTrue(v1 <= v2)
    self.assertTrue(v3 > v1)
    self.assertTrue(v1 < v4)
    self.assertTrue(v1 < v5)
    self.assertTrue(v2 < v4)
    self.assertFalse(v2 < v5)
    self.assertTrue(v1 < v6)

class ArchitectureTest(unittest.TestCase):
  def setUp(self):
    self.arch = Architecture("i386")

  def testInit(self):
    self.assertEqual("i386", self.arch.name)

  def testAsURI(self):
    baseURI = "http://example.org"
    expected = baseURI + "/arch/i386"
    self.assertEqual(expected, self.arch.asURI(baseURI))

  def testAsLabel(self):
    self.assertEqual("Architecture: i386", self.arch.asLabel())

  def testToStr(self):
    self.assertEqual("i386", str(self.arch))

  def testEq(self):
    self.assertEqual(Architecture("i386"), Architecture("i386"))
    self.assertNotEqual(Architecture("i386"), Architecture("amd64"))

  def testHasInstance(self):
    self.assertFalse(self.arch.hasInstance())
    self.assertTrue(Architecture("all").hasInstance())

class BinaryPackageLiteTest(unittest.TestCase):
  def setUp(self):
    self.b = BinaryPackageLite()
    self.b.package = "testpkgname"
    self.b.version = VersionNumber("1.0-1")

  def testAsURI(self):
    baseURI = "http://example.org"
    expected = baseURI + "/binary/testpkgname/1.0-1"
    self.assertEqual(expected, self.b.asURI(baseURI))

  def testAsLabel(self):
    self.assertEqual("Binary: testpkgname (1.0-1)", self.b.asLabel())

class BinaryPackageBuildTest(unittest.TestCase):
  def setUp(self):
    self.b = BinaryPackageBuild()
    self.b.architecture = Architecture("testarch")
    self.b.ancestor = BinaryPackageLite("parent", "4:4.5")
  
  def testAsURINoAncestor(self):
    baseURI = "http://example.org"
    self.b.ancestor = None
    self.assertRaises(AttributeError, self.b.asURI, baseURI)

  def testAsURIAncestor(self):
    baseURI = "http://example.org"
    expected = baseURI + "/binary/parent/4:4.5/testarch"
    self.assertEqual(expected, self.b.asURI(baseURI))

  def testAsLabelNoAncestor(self):
    self.b.ancestor = None
    self.assertRaises(AttributeError, self.b.asLabel)

  def testAsLabelAncestor(self):
    self.assertEqual("BinaryBuild: parent (4:4.5) [testarch]",\
                     self.b.asLabel())

class SourcePackageTest(unittest.TestCase):
   def testAsLabel(self):
    b = SourcePackage()
    b.package = "testpkgname"
    b.version = VersionNumber("1.0-1")
    self.assertEqual("Source: testpkgname (1.0-1)", b.asLabel())

class ConstraintTest(unittest.TestCase):
  def setUp(self):
    self.c = Constraint()
    self.c.package = "testpackage"
    self.c.operator = ">="
    self.c.version = "4:4.5"

  def testAsURI(self):
    baseURI = "http://example.org"
    expected = baseURI + "/constraint/" +\
               hashlib.sha1("testpackage>=4:4.5").hexdigest()
    self.assertEqual(expected, self.c.asURI(baseURI))

    self.c.operator = None
    self.c.version = None
    expected = baseURI + "/constraint/" +\
               hashlib.sha1("testpackage").hexdigest()
    self.assertEqual(expected, self.c.asURI(baseURI))

  def testAsLabel(self):
    self.assertEqual("Constraint: testpackage (>= 4:4.5)",\
                     self.c.asLabel())

    self.c.exceptin = [Architecture("a1"), Architecture("a2")]
    self.assertEqual("Constraint: testpackage (>= 4:4.5) !a1 !a2",\
                     self.c.asLabel())

    self.c.exceptin = []
    self.c.onlyin = [Architecture("a1")]
    self.assertEqual("Constraint: testpackage (>= 4:4.5) a1",\
                     self.c.asLabel())

    self.c.onlyin = []
    self.c.operator = None
    self.c.version = None
    self.assertEqual("Constraint: testpackage",\
                     self.c.asLabel())
