import unittest
import urllib

from models import *

from errors import IndividualNotFoundException
from errors import UnavailableLanguageException

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

  def testAsLabel(self):
    v = VersionNumber("1.0-1")
    self.assertEqual("Version: 1.0-1", v.asLabel('en'))

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
    self.assertEqual("Architecture: i386", self.arch.asLabel('en'))

  def testToStr(self):
    self.assertEqual("i386", str(self.arch))

  def testEq(self):
    self.assertEqual(Architecture("i386"), Architecture("i386"))
    self.assertNotEqual(Architecture("i386"), Architecture("amd64"))

  def testHasIndividual(self):
    self.assertFalse(self.arch.hasIndividual())
    self.assertTrue(Architecture("all").hasIndividual())

class BinaryPackageTest(unittest.TestCase):
  def setUp(self):
    self.b = BinaryPackage("testpkgname", "1.0-1")

  def testAsURI(self):
    baseURI = "http://example.org"
    expected = baseURI + "/binary/testpkgname/1.0-1"
    self.assertEqual(expected, self.b.asURI(baseURI))

  def testAsLabel(self):
    self.assertEqual("Binary: testpkgname (1.0-1)", self.b.asLabel('en'))

class UnversionedBinaryPackageTest(unittest.TestCase):
  def setUp(self):
    self.ub = UnversionedBinaryPackage("name")

  def testAsURI(self):
    baseURI = "http://example.org"
    expected = baseURI + "/binary/name"
    self.assertEqual(expected, self.ub.asURI(baseURI))

  def testAsLabel(self):
    self.assertEqual("Unversioned Binary: name", self.ub.asLabel('en'))

  def testAsStr(self):
    self.assertEqual("name", self.ub.__str__())

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
    self.assertRaises(AttributeError, self.b.asLabel, 'en')

  def testAsLabelAncestor(self):
    self.assertEqual("BinaryBuild: parent (4:4.5) [testarch]",\
                     self.b.asLabel('en'))

class SourcePackageTest(unittest.TestCase):
  def testAsLabel(self):
    b = SourcePackage("testpkgname", "1.0-1")
    self.assertEqual("Source: testpkgname (1.0-1)", b.asLabel('en'))

class UnversionedSourcePackageTest(unittest.TestCase):
  def setUp(self):
    self.us = UnversionedSourcePackage("name")

  def testAsURI(self):
    baseURI = "http://example.org"
    expected = baseURI + "/source/name"
    self.assertEqual(expected, self.us.asURI(baseURI))

  def testAsLabel(self):
    self.assertEqual("Unversioned Source: name", self.us.asLabel('en'))

  def testAsLabelMissingLang(self):
    self.assertRaises(UnavailableLanguageException, self.us.asLabel, 'foo')

  def testAsStr(self):
    self.assertEqual("name", self.us.__str__())

class ConstraintTest(unittest.TestCase):
  def setUp(self):
    self.c = Constraint()
    self.c.package = "testpackage"
    self.c.operator = ">="
    self.c.version = "4:4.5"

  def testAsURI(self):
    baseURI = "http://example.org"
    expected = urllib.quote_plus("/constraint/testpackage LaterOrEqual 4:4.5", '/')
    self.assertEqual(baseURI + expected, self.c.asURI(baseURI))

    self.c.exceptin = [Architecture("i386"), Architecture("amd64")]
    expected = "/constraint/testpackage LaterOrEqual 4:4.5 ExceptIn_i386 ExceptIn_amd64"
    expected = urllib.quote_plus(expected, '/')
    self.assertEqual(baseURI + expected, self.c.asURI(baseURI))
    
    self.c.exceptin = []
    self.c.onlyin = [Architecture("a1")]
    self.c.version = "4:4.5+svn1"
    expected = "/constraint/testpackage LaterOrEqual 4:4.5+svn1 OnlyIn_a1"
    expected = urllib.quote_plus(expected, '/')
    self.assertEqual(baseURI + expected, self.c.asURI(baseURI))
    
    self.c.operator = None
    self.c.version = None
    self.c.onlyin = []
    expected = urllib.quote_plus("/constraint/testpackage", '/')
    self.assertEqual(baseURI + expected, self.c.asURI(baseURI))

  def testAsLabel(self):
    self.assertEqual("Constraint: testpackage (>= 4:4.5)",\
                     self.c.asLabel('en'))

    self.c.exceptin = [Architecture("a1"), Architecture("a2")]
    self.assertEqual("Constraint: testpackage (>= 4:4.5) !a1 !a2",\
                     self.c.asLabel('en'))

    self.c.exceptin = []
    self.c.onlyin = [Architecture("a1")]
    self.assertEqual("Constraint: testpackage (>= 4:4.5) a1",\
                     self.c.asLabel('en'))

    self.c.onlyin = []
    self.c.operator = None
    self.c.version = None
    self.assertEqual("Constraint: testpackage",\
                     self.c.asLabel('en'))

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
    self.assertEqual("File: filename", self.f.asLabel('en'))

class DirectoryTest(unittest.TestCase):
  def setUp(self):
    self.d = Directory("test/path")

  def testEq(self):
    self.assertEqual(self.d, Directory("test/path"))
    self.assertNotEqual(self.d, Directory("other/path"))

  def testAsURI(self):
    self.assertEqual("b/path/test/path", self.d.asURI("b"))

  def testAsLabel(self):
    self.assertEqual("Directory: test/path", self.d.asLabel('en'))

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
    self.assertEqual("Tag: facet::tag", self.t.asLabel('en'))

class SectionTest(unittest.TestCase):
  def setUp(self):
    self.s = Section("name")

  def testEq(self):
    self.assertEqual(self.s, Section("name"))
    self.assertNotEqual(self.s, Section("othername"))

  def testAsURI(self):
    self.assertEqual("b/section/name", self.s.asURI("b"))

  def testAsLabel(self):
    self.assertEqual("Section: name", self.s.asLabel('en'))

class PriorityTest(unittest.TestCase):
  def setUp(self):
    self.p = PriorityBox.Priority("optional")

  def testEq(self):
    self.assertNotEqual(self.p, PriorityBox.Priority("optional"))

  def testAsURI(self):
    self.assertRaises(Exception, self.p.asURI, "b")

  def testAsLabel(self):
    self.assertRaises(Exception, self.p.asLabel)

class PriorityBoxTest(unittest.TestCase):
  def setUp(self):
    self.p1 = PriorityBox.get("optional")
    self.p2 = PriorityBox.get("optional")
    self.p3 = PriorityBox.get("extra")

  def testGetNotExistingIndividual(self):
    self.assertRaises(IndividualNotFoundException, PriorityBox.get, "foo")

  def testSameIDs(self):
    self.assertEqual(id(self.p1), id(self.p1))
    self.assertEqual(id(self.p1), id(self.p2))
    self.assertNotEqual(id(self.p1), id(self.p3))

class ContributorTest(unittest.TestCase):
  def setUp(self):
    self.c = Contributor("Name Surname", "mail@example.com")

  def testInit(self):
    self.assertEqual("Name Surname", self.c.name)
    self.assertEqual("mail@example.com", self.c.email)
    
  def testAsLabel(self):
    self.assertEqual("Contributor: Name Surname <mail@example.com>",\
                     self.c.asLabel('en'))

class AreaTest(unittest.TestCase):
  def setUp(self):
    self.a = AreaBox.Area("main")

  def testEq(self):
    self.assertNotEqual(AreaBox.Area("main"), self.a)

  def testAsURI(self):
    self.assertRaises(Exception, self.a.asURI, "b")

  def testAsLabel(self):
    self.assertRaises(Exception, self.a.asLabel)

class AreaBoxTest(unittest.TestCase):
  def setUp(self):
    self.p1 = AreaBox.get("main")
    self.p2 = AreaBox.get("main")
    self.p3 = AreaBox.get("contrib")

  def testGetNotExistingIndividual(self):
    self.assertRaises(IndividualNotFoundException, PriorityBox.get, "foo")

  def testSameIDs(self):
    self.assertEqual(id(self.p1), id(self.p1))
    self.assertEqual(id(self.p1), id(self.p2))
    self.assertNotEqual(id(self.p1), id(self.p3))

class RepositoryTest(unittest.TestCase):
  def setUp(self):
    self.baseRepository = Repository("http://example.com", "svn://example.com")
    self.gitRepository = GitRepository("http://example.com", "git://example.com")
    self.noURIRepository = Repository("http://example.com", None)

  def testAsLabel(self):
    self.assertEqual("Repository: svn://example.com",\
                     self.baseRepository.asLabel('en'))
    self.assertEqual("Repository",\
                     self.noURIRepository.asLabel('en'))

  def testRdfType(self):
    self.assertEqual("Repository", self.baseRepository.rdfType())
    self.assertEqual("GitRepository", self.gitRepository.rdfType())

  def testStr(self):
    expected = "Repository: <git://example.com> <http://example.com>"
    self.assertEqual(expected, str(self.gitRepository))

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

  def testencodeURI(self):
    base = "http://rdf.debian.net"
    expected1 = "http://rdf.debian.net/" + \
      urllib.quote_plus("binary/binname/3.4-2", '/')
    expected2 = "http://rdf.debian.net/" + \
      urllib.quote_plus("distribution/lenny", '/')
    expected3 = "http://rdf.debian.net/" + \
      urllib.quote_plus("foo", '/')
    self.assertEqual(expected1, encodeURI(base, "binary", "binname", "3.4-2"))
    self.assertEqual(expected2, encodeURI(base, "distribution", "lenny"))
    self.assertEqual(expected3, encodeURI(base, "foo"))
