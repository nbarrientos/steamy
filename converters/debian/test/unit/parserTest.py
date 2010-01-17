# -*- coding: utf8 -*-

import unittest
import optparse

from models import *
from parsers import SourcesParser, PackagesParser, BaseParser
from errors import MissingMandatoryFieldError, ParserError
from errors import PackageDoesNotMatchRegularExpression


class SourcesParserTest(unittest.TestCase):
  def setUp(self):
    self.values = optparse.Values()
    self.values.ensure_value("regex", None)
    self.values.ensure_value("role", True)
    self.parser = SourcesParser(self.values)
    self.sourcePackage = {}
    self.sourcePackage['Package'] = "srcpkg"
    self.sourcePackage['Binary'] = "binpkg1, binpkg2"
    self.sourcePackage['Version'] = "0.5-2"
    self.sourcePackage['Build-Depends'] = "dep1 (>= 5.0.37), dep2 [!powerpc]"
    self.sourcePackage['Build-Depends-Indep'] = "dep3"
    self.sourcePackage['Build-Conflicts'] = "dep4"
    self.sourcePackage['Build-Conflicts-Indep'] = "dep5"
    self.sourcePackage['Architecture'] = "any"
    self.sourcePackage['Section'] = "games"
    self.sourcePackage['Priority'] = "optional"
    self.sourcePackage['Dm-Upload-Allowed'] = "yes"
    self.sourcePackage['Maintainer'] = "Joe Doe <joe.doe@example.com>"
    self.sourcePackage['Uploaders'] = "Alice <alice@d.o>, Bob <bob@d.o>"
    self.sourcePackage['Homepage'] = "http://www.example.org"
    self.sourcePackage['Directory'] = "pool/main/s/srcpkg"
    self.sourcePackage['Vcs-Browser'] = "http://github.com/example"
    self.sourcePackage['Vcs-Git'] = "git://github.com/example"
    self.sourcePackage['Format'] = "1.0"
    self.sourcePackage['Standards-Version'] = "1.0.1"
    self.sourcePackage['Files'] = [\
      {'md5sum': 'd7f059964', 'size': '1234', 'name': 'srcpkg_0.5-2.dsc'},
      {'md5sum': '5b32fbe56', 'size': '5678', 'name': 'srcpkg_0.5.orig.tar.gz'},
      {'md5sum': 'd7f9b6fbe', 'size': '9012', 'name': 'srcpkg_0.5-2.diff.gz'}]

  # Fields

  def testParseBinary(self):
    bins = self.parser.parseBinary(self.sourcePackage)
    self.assertEqual(2, len(bins))
    self.assertEqual("binpkg1", bins[0].package)
    self.assertEqual("0.5-2", str(bins[0].version))
    self.assertEqual("binpkg2", bins[1].package)
    self.assertEqual("0.5-2", str(bins[1].version))

  def testParseBinarySingle(self):
    self.sourcePackage['Binary'] = "binpkg"
    bin = self.parser.parseBinary(self.sourcePackage)
    self.assertEqual(1, len(bin))
    self.assertEqual("binpkg", bin[0].package)
    self.assertEqual("0.5-2", str(bin[0].version))

  def testParseSourcePackage(self):
    s = self.parser.parseSourcePackage(self.sourcePackage)
    self.assertEqual("srcpkg", s.package)
    self.assertEqual("0.5-2", str(s.version))
    self.assertEqual(2, len(s.binary))
    self.assertNotEqual(None, s.buildDepends)
    self.assertNotEqual(None, s.buildDependsIndep)
    self.assertNotEqual(None, s.buildConflicts)
    self.assertNotEqual(None, s.buildConflictsIndep)
    self.assertEqual(2, s.buildDepends.len())
    self.assertEqual(1, s.buildDependsIndep.len())
    self.assertEqual(1, s.buildConflicts.len())
    self.assertEqual(1, s.buildConflictsIndep.len())
    self.assertNotEqual(None, s.maintainer)
    self.assertNotEqual(None, s.uploaders)
    self.assertEqual(2, len(s.uploaders))
    self.assertEqual("http://www.example.org", s.homepage)
    self.assertTrue(s.dmUploadAllowed)
    self.assertNotEqual(None, s.vcs)
    self.assertEqual("1.0", str(s.format))
    self.assertEqual("1.0.1", str(s.standardsVersion))

  def testParseSourcePackageNotMatchingRegex(self):
    self.values.ensure_value("regex", "^a.*")
    self.parser.opts = self.values
    self.parser.opts.cRegex = re.compile("^a.*")
    self.assertRaises(PackageDoesNotMatchRegularExpression,\
                      self.parser.parseSourcePackage, self.sourcePackage)
   
  def testParseSourcePackageMatchingRegex(self):
    self.values.ensure_value("regex", "^src.*")
    self.parser.opts = self.values
    self.parser.opts.cRegex = re.compile("^src.*")
    s = self.parser.parseSourcePackage(self.sourcePackage)
    self.assertEqual("srcpkg", s.package)
    
  def testParseBuildDepends(self):
    deps = self.parser.parseBuildDepends(self.sourcePackage)
    self.assertEqual(2, deps.len())

  def testParseBuildDependsIndep(self):
    deps = self.parser.parseBuildDependsIndep(self.sourcePackage)
    self.assertEqual(1, deps.len())

  def testParseBuildConflicts(self):
    deps = self.parser.parseBuildConflicts(self.sourcePackage)
    self.assertEqual(1, deps.len())

  def testParseBuildConflictsIndep(self):
    deps = self.parser.parseBuildConflictsIndep(self.sourcePackage)
    self.assertEqual(1, deps.len())

  def testParseArchitecture(self):
    archs = self.parser.parseArchitecture(self.sourcePackage)
    self.assertEqual(1, len(archs))
    self.assertEqual([Architecture("any")], archs)

    self.sourcePackage['Architecture'] = "i386 amd64"
    archs = self.parser.parseArchitecture(self.sourcePackage)
    self.assertEqual(2, len(archs))
    self.assertEqual([Architecture("i386"), Architecture("amd64")], archs)

  def testParseArchitectureSeveral(self):
    self.sourcePackage['Architecture'] = "alpha amd64"
    archs = self.parser.parseArchitecture(self.sourcePackage)
    self.assertEqual(2, len(archs))
    self.assertEqual([Architecture("alpha"), Architecture("amd64")], archs)

  def testParseArchitectureMissingField(self):
    self.sourcePackage.pop('Architecture')
    self.assertRaises(MissingMandatoryFieldError,\
                      self.parser.parseArchitecture, self.sourcePackage)

  def testParseFilesAncestor(self):
    parent = Directory("test/path")
    files = self.parser.parseFiles(self.sourcePackage, parent)
    self.assertEqual(3, len(files))
    self.assertEqual("d7f059964", files[0].md5sum)
    self.assertEqual("test/path", files[0].ancestor.path)

  def testParseFilesMissingField(self):
    self.sourcePackage.pop('Files')
    self.assertRaises(MissingMandatoryFieldError,\
                      self.parser.parseFiles, self.sourcePackage, None)

  def testParseDirectory(self):
    self.assertEqual((Directory("pool/main/s/srcpkg"), AreaBox.get("main")),\
                     self.parser.parseDirectory(self.sourcePackage))

  def testParseDirectoryMissingField(self):
    self.sourcePackage.pop('Directory')
    self.assertRaises(MissingMandatoryFieldError,\
                      self.parser.parseDirectory, self.sourcePackage)

  def testParseMaintainer(self):
    maintainer = self.parser.parseMaintainer(self. sourcePackage)
    self.assertEquals("Joe Doe", maintainer.name)
    self.assertEquals("joe.doe@example.com", maintainer.email)

  def testParseMaintainerMissingField(self):
    self.sourcePackage.pop('Maintainer')
    self.assertRaises(MissingMandatoryFieldError,\
                      self.parser.parseMaintainer, self.sourcePackage)

  def testParseUploaders(self):
    uploaders = self.parser.parseUploaders(self. sourcePackage)
    self.assertEquals(2, len(uploaders))

  def testParseUploadersMissingField(self):
    self.sourcePackage.pop('Uploaders')
    self.assertEqual(None, self.parser.parseUploaders(self.sourcePackage))

  def testParseDmUploadAllowed(self):
    self.assertTrue(self.parser.parseDmUploadAllowed(self.sourcePackage))

  def testParseBuildEssentialMissingField(self):
    self.sourcePackage.pop('Dm-Upload-Allowed')
    self.assertEqual(None, self.parser.parseDmUploadAllowed(self.sourcePackage))

  def testParseFormat(self):
    self.assertEqual("1.0", self.parser.parseFormat(self.sourcePackage))
  
  def testParseFormatMissingField(self):
    self.sourcePackage.pop('Format')
    self.assertEqual(None, self.parser.parseFormat(self.sourcePackage))

  def testParseStandardsVersion(self):
    self.assertEqual("1.0.1", self.parser.parseStandardsVersion(self.sourcePackage))

  def testParseStandardsVersionMissingField(self):
    self.sourcePackage.pop('Standards-Version')
    self.assertEqual(None, self.parser.parseStandardsVersion(self.sourcePackage))

class PackagesParserTest(unittest.TestCase):
  def setUp(self):
    self.values = optparse.Values()
    self.values.ensure_value("regex", None)
    self.parser = PackagesParser(self.values)
    self.binaryPackage = {}
    self.binaryPackage['Package'] = "mutt"
    self.binaryPackage['Version'] = "1:2.4+svn5677-1"
    self.binaryPackage['Architecture'] = "all"
    self.binaryPackage['Source'] = "muttsrc"
    self.binaryPackage['Depends'] = "exim4 (>> 0.5.4-5) | mail-transport-agent, mutt"
    self.binaryPackage['Recommends'] = "locales, mime-support, bastet"
    self.binaryPackage['Pre-Depends'] = "test"
    self.binaryPackage['Suggests'] = "test"
    self.binaryPackage['Breaks'] = "test"
    self.binaryPackage['Conflicts'] = "test"
    self.binaryPackage['Provides'] = "test"
    self.binaryPackage['Replaces'] = "test"
    self.binaryPackage['Enhances'] = "test"
    self.binaryPackage['Installed-Size'] = "108"
    self.binaryPackage['Filename'] = "pool/main/m/mutt/mutt_1:2.4+svn5677-1_all.deb"
    self.binaryPackage['MD5sum'] = "460578"
    self.binaryPackage['Size'] = "4566"
    self.binaryPackage['Tag'] = "implemented-in::python, hardware::{lap,power:apm}"
    self.binaryPackage['Section'] = "games"
    self.binaryPackage['Priority'] = "optional"
    self.binaryPackage['Essential'] = "yes"
    self.binaryPackage['Build-Essential'] = "yes"
    self.binaryPackage['Description'] = '''text-based mailreader supporting MIME, GPG, PGP and threading
 Mutt is a sophisticated text-based Mail User Agent. Some highlights:
 .
  * MIME support (including RFC1522 encoding/decoding of 8-bit message
    headers and UTF-8 support).
  * Highly configurable through easy but powerful rc file.'''

  def tearDown(self):
    pass

  # Fields

  def testParsePackage(self):
    self.assertEqual("mutt", self.parser.parsePackage(self.binaryPackage))

  def testParsePackageMissingField(self):
    self.binaryPackage.pop('Package')
    self.assertRaises(MissingMandatoryFieldError,\
                      self.parser.parsePackage, self.binaryPackage)

  def testParseDepends(self):
    deps = self.parser.parseDepends(self.binaryPackage)
    self.assertEqual(2, deps.len())

  def testParseDependsMissingField(self):
    self.binaryPackage.pop('Depends')
    self.assertEqual(None, self.parser.parseDepends(self.binaryPackage))

  def testParseRecommends(self):
    deps = self.parser.parseRecommends(self.binaryPackage)
    self.assertEqual(3, deps.len())

  def testParsePreDepends(self):
    deps = self.parser.parsePreDepends(self.binaryPackage)
    self.assertEqual(1, deps.len())

  def testParseSuggests(self):
    deps = self.parser.parseSuggests(self.binaryPackage)
    self.assertEqual(1, deps.len())

  def testParseBreaks(self):
    deps = self.parser.parseBreaks(self.binaryPackage)
    self.assertEqual(1, deps.len())

  def testParseConflicts(self):
    deps = self.parser.parseConflicts(self.binaryPackage)
    self.assertEqual(1, deps.len())

  def testParseProvides(self):
    deps = self.parser.parseProvides(self.binaryPackage)
    self.assertEqual(1, deps.len())

  def testParseReplaces(self):
    deps = self.parser.parseReplaces(self.binaryPackage)
    self.assertEqual(1, deps.len())

  def testParseEnhances(self):
    deps = self.parser.parseEnhances(self.binaryPackage)
    self.assertEqual(1, deps.len())

  def testParseInstalledSize(self):
    self.assertEqual("108", self.parser.parseInstalledSize(self.binaryPackage))

  def testParseInstalledSizeMissingField(self):
    self.binaryPackage.pop('Installed-Size')
    self.assertRaises(MissingMandatoryFieldError,\
                      self.parser.parseInstalledSize, self.binaryPackage)

  def testParseArchitecture(self):
    self.assertEqual("all", str(self.parser.parseArchitecture(self.binaryPackage)))

  def testParseArchitectureMissingField(self):
    self.binaryPackage.pop('Architecture')
    self.assertRaises(MissingMandatoryFieldError,\
                      self.parser.parseArchitecture, self.binaryPackage)

  def testParseBinaryPackageBuildWithoutAncestorReference(self):
    build = self.parser.parseBinaryPackageBuild(self.binaryPackage, None)
    self.assertEqual("all", build.architecture.name)
    self.assertEqual("108", build.installedSize)
    self.assertEqual(None, build.ancestor)

  def testParseBinaryPackageBuildWithAncestorReference(self):
    parent = BinaryPackage()
    parent.package = "testpkg"
    build = self.parser.parseBinaryPackageBuild(self.binaryPackage, parent)
    self.assertEqual("all", build.architecture.name)
    self.assertEqual("108", build.installedSize)
    self.assertEqual(parent, build.ancestor)
    self.assertEqual("testpkg", build.ancestor.package)

  def testParseBinaryPackage(self):
    p = self.parser.parseBinaryPackage(self.binaryPackage)
    self.assertEqual("mutt", p.package)
    self.assertNotEqual(None, p.depends)
    self.assertEqual("muttsrc", p.source.package)
    self.assertEqual(p.version, p.source.version)
    self.assertEqual(2, p.depends.len())
    self.assertEqual(3, p.recommends.len())
    self.assertEqual(1, p.preDepends.len())
    self.assertEqual(1, p.suggests.len())
    self.assertEqual(1, p.breaks.len())
    self.assertEqual(1, p.conflicts.len())
    self.assertEqual(1, p.provides.len())
    self.assertEqual(1, p.replaces.len())
    self.assertEqual(1, p.enhances.len())
    self.assertEqual("2.4+svn5677", p.version.upstream_version)
    self.assertEqual("1", p.version.debian_version)
    self.assertEqual("all", p.build.architecture.name)
    self.assertEqual("108", p.build.installedSize)
    self.assertEqual("mutt", p.build.ancestor.package)
    self.assertEqual("pool/main/m/mutt", p.filename.ancestor.path)
    self.assertEqual("mutt_1:2.4+svn5677-1_all.deb", p.filename.name)
    self.assertEqual("4566", p.filename.size)
    self.assertEqual("460578", p.filename.md5sum)
    self.assertEqual(3, len(p.tag))
    self.assertTrue(p.essential)
    self.assertTrue(p.buildEssential)
    self.assertTrue(len(p.ldescription) > 0)
    self.assertTrue(len(p.sdescription) > 0)

  def testParseBinaryPackageNotMatchingRegex(self):
    self.values.ensure_value("regex", "^a.*")
    self.parser.opts = self.values
    self.parser.opts.cRegex = re.compile("^a.*")
    self.assertRaises(PackageDoesNotMatchRegularExpression,\
                      self.parser.parseBinaryPackage, self.binaryPackage)
   
  def testParseBinaryPackageMatchingRegex(self):
    self.values.ensure_value("regex", "^mu.*")
    self.parser.opts = self.values
    self.parser.opts.cRegex = re.compile("^mu.*")
    p = self.parser.parseBinaryPackage(self.binaryPackage)
    self.assertEqual("mutt", p.package)
 
  def testParseFilename(self):
    expectedFile = File("mutt_1:2.4+svn5677-1_all.deb",\
                        "460578", "4566", Directory("pool/main/m/mutt"))
    file = self.parser.parseFilename(self.binaryPackage)
    self.assertEqual(expectedFile, file)

  def testParseEssential(self):
    self.assertTrue(self.parser.parseEssential(self.binaryPackage))

  def testParseEssentialMissingField(self):
    self.binaryPackage.pop('Essential')
    self.assertEqual(None, self.parser.parseEssential(self.binaryPackage))

  def testParseBuildEssential(self):
    self.assertTrue(self.parser.parseBuildEssential(self.binaryPackage))

  def testParseBuildEssentialMissingField(self):
    self.binaryPackage.pop('Build-Essential')
    self.assertEqual(None, self.parser.parseBuildEssential(self.binaryPackage))

  def testParseDescription(self) :
    expectedShort = "text-based mailreader supporting MIME, GPG, PGP and threading"
    expectedLong =\
    ''' Mutt is a sophisticated text-based Mail User Agent. Some highlights:
 .
  * MIME support (including RFC1522 encoding/decoding of 8-bit message
    headers and UTF-8 support).
  * Highly configurable through easy but powerful rc file.'''
    (short, long) = self.parser.parseDescription(self.binaryPackage)
    self.assertEqual(expectedShort, short)
    self.assertEqual(expectedLong, long)

  def testParseDescriptionEmptyExtended(self) :
    self.binaryPackage['Description'] = "text-based mailreader supporting MIME, GPG, PGP and threading"
    expectedShort = "text-based mailreader supporting MIME, GPG, PGP and threading"
    (short, long) = self.parser.parseDescription(self.binaryPackage)
    self.assertEqual(expectedShort, short)
    self.assertEqual(None, long)

  def testParseSource(self):
    binary = BinaryPackage("mutt", Version("1:2.4+svn5677-1"))
    source = self.parser.parseSource(self.binaryPackage, binary)
    self.assertEqual("muttsrc", source.package)
    self.assertEqual(Version("1:2.4+svn5677-1"), source.version)

  def testParseSourceEmpty(self):
    binary = BinaryPackage("mutt", Version("1:2.4+svn5677-1"))
    self.binaryPackage.pop("Source")
    source = self.parser.parseSource(self.binaryPackage, binary)
    self.assertEqual("mutt", source.package)
    self.assertEqual(Version("1:2.4+svn5677-1"), source.version)


class BaseParserTest(unittest.TestCase):
  def setUp(self):
    self.values = optparse.Values()
    self.values.ensure_value("regex", None)
    self.values.ensure_value("role", True)
    self.parser = BaseParser(self.values)

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

  def testParseVersionNumberWrongVersionNumber(self):
    self.assertRaises(ParserError, self.parser.parseVersionNumber, "_")

  def testParseConstraints(self):
    input = "exim4 (>> 0.5.4-5) | mail-transport-agent, mutt"
    ors = self.parser.parseConstraints(input)
    self.assertEqual(2, len(ors.orconstraints))
    self.assertEqual(2, len(ors.get(0).constraints))
    self.assertEqual(UnversionedBinaryPackage("exim4"), ors.get(0).get(0).package)
    self.assertEqual(">>", ors.get(0).get(0).operator)
    self.assertEqual(UnversionedBinaryPackage("mail-transport-agent"), ors.get(0).get(1).package)
    self.assertEqual(UnversionedBinaryPackage("mutt"), ors.get(1).get(0).package)
 
    input = "c1a | c1b,    c2,c3, c4,  c5"
    ors = self.parser.parseConstraints(input)
    self.assertEqual(5, len(ors.orconstraints))
    self.assertEqual(2, len(ors.get(0).constraints))

  def testParseOrConstraint(self):
    input = "exim4+r (>> 0.5.4-5) | mail-transport-agent | swaml.4"
    ord = self.parser.parseOrConstraint(input)
    self.assertEqual(3, len(ord.constraints))
    self.assertEqual(UnversionedBinaryPackage("exim4+r"), ord.get(0).package)
    self.assertEqual(">>", ord.get(0).operator)
    self.assertEqual(UnversionedBinaryPackage("mail-transport-agent"), ord.get(1).package)
    self.assertEqual(UnversionedBinaryPackage("swaml.4"), ord.get(2).package)

    input = "c1|    c2|c3 | c4"
    ord = self.parser.parseOrConstraint(input)
    self.assertEqual(4, len(ord.constraints))

  def testParseConstraintSimple(self):
    input = "libgnutls13"
    d = self.parser.parseConstraint(input)
    self.assertEqual(UnversionedBinaryPackage(input), d.package)
    self.assertEqual(None, d.version)
  
  def testParseConstraintWithVersionAndOperator(self):
    input = "libidn11 (>= 0.5.18)"
    d = self.parser.parseConstraint(input)
    self.assertEqual(UnversionedBinaryPackage("libidn11"), d.package)
    self.assertEqual(">=", d.operator)
    self.assertEqual(None, d.version.epoch)
    self.assertEqual("0.5.18", d.version.upstream_version)
    self.assertEqual(None, d.version.debian_version)

  def testParseConstraintAllOperators(self):
    input = "pkg1 (<< 1)"
    d = self.parser.parseConstraint(input)
    self.assertEqual("<<", d.operator)
    input = "pkg1 (<= 1)"
    d = self.parser.parseConstraint(input)
    self.assertEqual("<=", d.operator)
    input = "pkg1 (= 1)"
    d = self.parser.parseConstraint(input)
    self.assertEqual("=", d.operator)
    input = "pkg1 (>= 1)"
    d = self.parser.parseConstraint(input)
    self.assertEqual(">=", d.operator)
    input = "pkg1 (>> 1)"
    d = self.parser.parseConstraint(input)
    self.assertEqual(">>", d.operator)

  def testParseConstraintGuardExcept(self):
    input = "libasound2-dev [!kfreebsd-i386 !kfreebsd-amd64]"
    d = self.parser.parseConstraint(input)
    self.assertEqual(UnversionedBinaryPackage("libasound2-dev"), d.package)
    self.assertEqual(None, d.operator)
    self.assertEqual(2, len(d.exceptin))
    self.assertEqual(0, len(d.onlyin))
    expectedlist = [Architecture("kfreebsd-i386"), Architecture("kfreebsd-amd64")]
    self.assertEqual(expectedlist, d.exceptin)

  def testParseConstraintGuardOnly(self):
    input = "libasound2-dev [kfreebsd-i386]"
    d = self.parser.parseConstraint(input)
    self.assertEqual(UnversionedBinaryPackage("libasound2-dev"), d.package)
    self.assertEqual(None, d.operator)
    self.assertEqual(0, len(d.exceptin))
    self.assertEqual(1, len(d.onlyin))
    expectedlist = [Architecture("kfreebsd-i386")]
    self.assertEqual(expectedlist, d.onlyin)

  def testParseFullConstraint(self):
    input = "libidn11 (>= 0.5.18) [!kfreebsd-i386 !kfreebsd-amd64]"
    d = self.parser.parseConstraint(input)
    self.assertEqual(UnversionedBinaryPackage("libidn11"), d.package)
    self.assertEqual(">=", d.operator)
    self.assertEqual(None, d.version.epoch)
    self.assertEqual("0.5.18", d.version.upstream_version)
    self.assertEqual(None, d.version.debian_version)
    self.assertEqual(2, len(d.exceptin))
    self.assertEqual(0, len(d.onlyin))
    expectedlist = [Architecture("kfreebsd-i386"), Architecture("kfreebsd-amd64")]
    self.assertEqual(expectedlist, d.exceptin)

  def testParseMalformedConstraint(self):
    input = "()"
    self.assertRaises(ParserError, self.parser.parseConstraint, input)
    input = "(>= 6.8)"
    self.assertRaises(ParserError, self.parser.parseConstraint, input)
    input = "[]"
    self.assertRaises(ParserError, self.parser.parseConstraint, input)
    input = "[powerpc]"
    self.assertRaises(ParserError, self.parser.parseConstraint, input)
    input = "(>= 5.6) [powerpc]"
    self.assertRaises(ParserError, self.parser.parseConstraint, input)

  def testParseTags(self):
    input = "implemented-in::lisp"
    tags = self.parser.parseTags(input)
    expected = [Tag("implemented-in", "lisp")]
    self.assertEqual(1,len(tags))
    self.assertEqual(expected, tags)

    input = "implemented-in::lisp, hardware::storage"
    tags = self.parser.parseTags(input)
    expected = [Tag("implemented-in", "lisp"), Tag("hardware", "storage")]
    self.assertEqual(2,len(tags))
    self.assertEqual(expected, tags)

    input = "hardware::storage:cd"
    tags = self.parser.parseTags(input)
    expected = [Tag("hardware", "storage:cd")]
    self.assertEqual(1,len(tags))
    self.assertEqual(expected, tags)

    input = "hardware::{laptop}"
    tags = self.parser.parseTags(input)
    expected = [Tag("hardware", "laptop")]
    self.assertEqual(1,len(tags))
    self.assertEqual(expected, tags)

    input = "hardware::{laptop,power:apm}, implemented-in::lisp"
    expected = [Tag("hardware", "laptop"),\
                Tag("hardware", "power:apm"), Tag("implemented-in", "lisp")]
    tags = self.parser.parseTags(input)
    self.assertEqual(3,len(tags))
    self.assertEqual(expected, tags)

    #input = "facet::t1,     facet::t2,facet::t3"
    #tags = self.parser.parseTags(input)
    #self.assertEqual(3,len(tags))

    input = "::"
    self.assertRaises(ParserError, self.parser.parseTags, input)

    input = "hardware::"
    self.assertRaises(ParserError, self.parser.parseTags, input)

    input = "::lang:c"
    self.assertRaises(ParserError, self.parser.parseTags, input)

    input = "hardware::, ::lang:c"
    self.assertRaises(ParserError, self.parser.parseTags, input)

  def testParseSection(self):
    input = {'Section': "utils"}
    self.assertEqual(Section("utils"), self.parser.parseSection(input))

  def testParseSectionMissingField(self):
    input = {}
    self.assertEqual(None, self.parser.parseSection(input))
  
  def testParsePriority(self):
    input = {'Priority': "optional"}
    self.assertEqual(PriorityBox.get("optional"),\
                     self.parser.parsePriority(input))

  def testParsePriorityMissingField(self):
    input = {}
    self.assertEqual(None, self.parser.parsePriority(input))
  
  def testParseContributorGuessRoleOn(self):
    input = "Name Surname     <mail@example.com>"
    contributor = self.parser.parseContributor(input)
    self.assertEqual("Name Surname", contributor.name)
    self.assertEqual("mail@example.com", contributor.email)
    self.assertEqual(Human, contributor.__class__)

    input = "Name Surname (Some notes) <mail+fax@example-rt.com>"
    contributor = self.parser.parseContributor(input)
    self.assertEqual("Name Surname (Some notes)", contributor.name)
    self.assertEqual("mail+fax@example-rt.com", contributor.email)
    self.assertEqual(Human, contributor.__class__)

    input = "<mail@example.com>"
    contributor = self.parser.parseContributor(input)
    self.assertEqual(None, contributor.name)
    self.assertEqual("mail@example.com", contributor.email)
    self.assertEqual(Human, contributor.__class__)

    input = "Name Surname"
    self.assertRaises(ParserError, self.parser.parseContributor, input)

  def testParseContributorGuessRoleOff(self):
    values = optparse.Values() # Unable to reset a boolean value!
    values.ensure_value('role', False)
    self.parser.opts = values

    input = "Name Surname     <mail@example.com>"
    contributor = self.parser.parseContributor(input)
    self.assertEqual(Contributor, contributor.__class__)
    
    input = "<mail@example.com>"
    contributor = self.parser.parseContributor(input)
    self.assertEqual(None, contributor.name)
    self.assertEqual("mail@example.com", contributor.email)
    self.assertEqual(Contributor, contributor.__class__)

  def testParseContributors(self):
    input = "Name Surname <mail@example.com>"
    contributors = self.parser.parseContributors(input)
    self.assertEqual(1, len(contributors))

    input = "S P <s@p.us>,    T <n@r.es>,K R R    <p@l.de>"
    contributors = self.parser.parseContributors(input)
    self.assertEqual(3, len(contributors))

  def testParseHomepage(self):
    input = {'Homepage': "http://example.org"}
    self.assertEquals("http://example.org", self.parser.parseHomepage(input))

  def testParseArea(self):
    input = 'pool/main/f/foo'
    self.assertEquals(AreaBox.get("main"), self.parser.parseArea(input))

    input = 'pool/non-free/f/foo'
    self.assertEquals(AreaBox.get("non-free"), self.parser.parseArea(input))
    
    input = 'pool/contrib/f/foo'
    self.assertEquals(AreaBox.get("contrib"), self.parser.parseArea(input))
    
    input = 'pool/failarea/f/foo'
    self.assertRaises(ParserError, self.parser.parseArea, input)
    
    input = 'dists/slink/main/source/games'
    self.assertEquals(AreaBox.get("main"), self.parser.parseArea(input))
    
    input = 'dists/bo/non-free/source/x11'
    self.assertEquals(AreaBox.get("non-free"), self.parser.parseArea(input))
    
    input = 'dists/potato/contrib/source/games'
    self.assertEquals(AreaBox.get("contrib"), self.parser.parseArea(input))

    input = 'dists/potato/failarea/source/games'
    self.assertRaises(ParserError, self.parser.parseArea, input)

  def testParseVcs(self):
    input = {'Vcs-Browser':'http://example.com', \
    'Vcs-Git':'git://git.example.com'}
    repo = self.parser.parseVcs(input)
    self.assertNotEqual(None, repo)
    self.assertEqual("http://example.com", repo.browser)
    self.assertEqual("git://git.example.com", repo.uri)
 
    input = {'X-Vcs-Browser':'http://example.com', \
    'X-Vcs-Git':'git://git.example.com'}
    repo = self.parser.parseVcs(input)
    self.assertNotEqual(None, repo)
    self.assertEqual("http://example.com", repo.browser)
    self.assertEqual("git://git.example.com", repo.uri)
  
    input = {'Vcs-Browser':'http://example.com', \
    'Vcs-Svn':'svn://svn.example.com/repos/test'}
    repo = self.parser.parseVcs(input)
    self.assertNotEqual(None, repo)
    self.assertEqual("http://example.com", repo.browser)
    self.assertEqual("svn://svn.example.com/repos/test", repo.uri)

    input = {'Vcs-Git':'git://git.example.com'}
    repo = self.parser.parseVcs(input)
    self.assertNotEqual(None, repo)
    self.assertEqual(None, repo.browser)
    self.assertEqual("git://git.example.com", repo.uri)
 
    input = {'Vcs-Browser':'http://example.com'}
    repo = self.parser.parseVcs(input)
    self.assertNotEqual(None, repo)
    self.assertEqual("http://example.com", repo.browser)
    self.assertEqual(None, repo.uri)
    
    input = {}
    repo = self.parser.parseVcs(input)
    self.assertEqual(None, repo)
