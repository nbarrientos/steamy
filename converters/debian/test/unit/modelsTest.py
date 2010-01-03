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

class BinaryPackageTest(unittest.TestCase):
  def setUp(self):
    self.b = BinaryPackage("testpkgname", "1.0-1")

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
    self.b.ancestor = BinaryPackage("parent", "4:4.5")
  
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
    b = SourcePackage("testpkgname", "1.0-1")
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

class FileTest(unittest.TestCase):
  def setUp(self):
    self.f = File('filename', '35dsfsd', '3435')
    self.f.ancestor = Directory("test/path")

  def testEq(self):
    self.assertEqual(self.f,\
              File('filename', '35dsfsd', '3435'))
    self.assertNotEqual(self.f,\
              File('filename', '35dsfsr', '3435'))

  def testAsURIAncestor(self):
    baseURI = "http://example.org"
    expected = baseURI + "/path/test/path/filename"
    self.assertEqual(expected, self.f.asURI(baseURI))

  def testAsURINoAncestor(self):
    baseURI = "http://example.org"
    self.f.ancestor = None
    self.assertRaises(AttributeError, self.f.asURI, baseURI)

  def testAsLabelAncestor(self):
    self.assertEqual("File: filename", self.f.asLabel())

class DirectoryTest(unittest.TestCase):
  def setUp(self):
    self.d = Directory("test/path")

  def testEq(self):
    self.assertEqual(self.d, Directory("test/path"))
    self.assertNotEqual(self.d, Directory("other/path"))

  def testAsURI(self):
    self.assertEqual("b/path/test/path", self.d.asURI("b"))

  def testAsLabel(self):
    self.assertEqual("Directory: test/path", self.d.asLabel())

class TagTest(unittest.TestCase):
  def setUp(self):
    self.t = Tag("facet", "tag")

  def testEq(self):
    self.assertEqual(self.t, Tag("facet", "tag"))
    self.assertNotEqual(self.t, Tag("facet", "gat"))
    self.assertNotEqual(self.t, Tag("tecaf", "tag"))

  def testAsURI(self):
    self.assertEqual("b/tag/facet/tag", self.t.asURI("b"))

  def testAsLabel(self):
    self.assertEqual("Tag: facet::tag", self.t.asLabel())

class SectionTest(unittest.TestCase):
  def setUp(self):
    self.s = Section("name")

  def testEq(self):
    self.assertEqual(self.s, Section("name"))
    self.assertNotEqual(self.s, Section("othername"))

  def testAsURI(self):
    self.assertEqual("b/section/name", self.s.asURI("b"))

  def testAsLabel(self):
    self.assertEqual("Section: name", self.s.asLabel())

class PriorityTest(unittest.TestCase):
  def setUp(self):
    self.p = Priority("name")

  def testEq(self):
    self.assertEqual(self.p, Priority("name"))
    self.assertNotEqual(self.p, Priority("othername"))

  def testAsURI(self):
    self.assertEqual("b/priority/name", self.p.asURI("b"))

  def testAsLabel(self):
    self.assertEqual("Priority: name", self.p.asLabel())

class ContributorTest(unittest.TestCase):
  def setUp(self):
    self.c = Contributor("Name Surname", "mail@example.com")

  def testInit(self):
    self.assertEqual("Name Surname", self.c.name)
    self.assertEqual("mail@example.com", self.c.email)
    
  def testAsLabel(self):
    self.assertEqual("Contributor: Name Surname <mail@example.com>",\
                     self.c.asLabel())

class AreaTest(unittest.TestCase):
  def setUp(self):
    self.a = Area("main")

  def testHasInstance(self):
    self.assertTrue(Area("main").hasInstance())
    self.assertTrue(Area("contrib").hasInstance())
    self.assertTrue(Area("non-free").hasInstance())

  def testEq(self):
    self.assertNotEqual(Area("name"), self.a)
    self.assertEqual(Area("main"), self.a)

class ToolsTest(unittest.TestCase):
  def setUp(self):
    self.name1 = "Debian Cool Team"
    self.email1 = "team@lists.debian.org"
    self.name2 = "Debian X Strike Force"
    self.email2 = "debian-x@lists.debian.org"
    self.name3 = "Debian Love Maintainers"
    self.email3 = "pkg-love-maintainers@lists.alioth.debian.org"
    self.name4 = "Jon Doe"
    self.email4 = "jon@debian.org"
    self.name5 = "Jon Team"
    self.email5 = "jon@gmail.com"
    self.name6 = "Debian Forensics"
    self.email6 = "forensics-devel@lists.alioth.debian.org"
  
  def testGuessRole(self):
    self.assertEqual(Team, guessRole(self.name1, self.email1).__class__)
    self.assertEqual(Team, guessRole(self.name2, self.email2).__class__)
    self.assertEqual(Team, guessRole(self.name3, self.email3).__class__)
    self.assertEqual(Human, guessRole(self.name4, self.email4).__class__)
    self.assertEqual(Human, guessRole(self.name5, self.email5).__class__)
    self.assertEqual(Team, guessRole(self.name6, self.email6).__class__)

  def testRating(self):
    self.assertEqual(3, teamRating(self.name1, self.email1))
    self.assertEqual(0, humanRating(self.name1, self.email1))

    self.assertEqual(3, teamRating(self.name2, self.email2))
    self.assertEqual(0, humanRating(self.name2, self.email2))

    self.assertEqual(4, teamRating(self.name3, self.email3))
    self.assertEqual(0, humanRating(self.name3, self.email3))

    self.assertEqual(0, teamRating(self.name4, self.email4))
    self.assertEqual(1, humanRating(self.name4, self.email4))
    
    self.assertEqual(1, teamRating(self.name5, self.email5))
    self.assertEqual(1, humanRating(self.name5, self.email5))
