# -*- coding: utf8 -*-

import unittest
import mox
import optparse
from datetime import date

from rdflib.Graph import ConjunctiveGraph
from rdflib import Namespace, URIRef, BNode, Literal

from models import *
from export import Triplifier

BQ = """
PREFIX deb:<http://idi.fundacionctic.org/steamy/debian.owl#>
PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

"""

RDFS = Namespace(u"http://www.w3.org/2000/01/rdf-schema#")
FOAF = Namespace(u"http://xmlns.com/foaf/0.1/")
RDF = Namespace(u"http://www.w3.org/1999/02/22-rdf-syntax-ns#")
DEB = Namespace(u"http://idi.fundacionctic.org/steamy/debian.owl#")
TAG = Namespace(u"http://www.holygoat.co.uk/owl/redwood/0.1/tags/")
DOAP = Namespace(u"http://usefulinc.com/ns/doap#")

ALLTRIPLES = BQ + "SELECT ?x ?y ?z WHERE { ?x ?y ?z . }"

class TriplifierTest(unittest.TestCase):
  def setUp(self):
    self.values = optparse.Values()
    self.values.ensure_value("baseURI", "b")
    self.graph = ConjunctiveGraph()
    self.t = Triplifier(self.graph, self.values)
    self.mox = mox.Mox()

  def compareGeneratedTriples(self, expected):
    for triple in self.graph.query(ALLTRIPLES):
      self.assertTrue(triple in expected, "%s is not in" % str(triple))

  def testPushInitialTriples(self):
    self.values.ensure_value("distribution", "http://example.com/d")
    self.values.ensure_value("distdate", "Not used")
    self.values.ensure_value("parsedDistDate", date(1985, 07, 01))
    self.t.pushInitialTriples()
    self.assertEqual(2, len(self.graph))
    uriref = URIRef("http://example.com/d")
    expected = [(uriref, RDF.type, DEB['Distribution']),\
                (uriref, DEB['releaseDate'], Literal(date(1985, 07, 01)))]
    self.compareGeneratedTriples(expected)

  def testTriplifyArchitecture(self):
    arch = Architecture("testArch")
    uriref = URIRef("b/arch/testArch")
    self.assertEqual(uriref, self.t.triplifyArchitecture(arch))
    self.assertEqual(2, len(self.graph))
    expected = [(uriref, RDF.type, DEB['Architecture']),\
                (uriref, RDFS.label, Literal("Architecture: testArch", lang='en'))]
    self.compareGeneratedTriples(expected)

  def testTriplifyArchitectureOntologyInstance(self):
    arch = Architecture("all")
    self.assertEqual(DEB['all'], self.t.triplifyArchitecture(arch))

  def testTriplifyVersionNumberSimple(self):
    version = VersionNumber("1.0-1")
    uriref = URIRef("b/version/1.0-1")
    self.assertEqual(uriref, self.t.triplifyVersionNumber(version))
    self.assertEqual(5, len(self.graph))
    expected = [(uriref, RDF.type, DEB['VersionNumber']),\
                (uriref, RDFS.label, Literal("Version: 1.0-1", lang='en')),\
                (uriref, DEB['fullVersion'], Literal("1.0-1")),\
                (uriref, DEB['upstreamVersion'], Literal("1.0")),\
                (uriref, DEB['debianRevision'], Literal("1"))]
    self.compareGeneratedTriples(expected)

  def testTriplifyConstraintSimple(self):
    constraint = Constraint()
    constraint.package = UnversionedBinaryPackage("pkg")
    constraint.operator = ">>"
    constraint.version = VersionNumber("1.0-1")
    self.t.triplifyVersionNumber =\
        self.mockTriplifyVersionNumber(constraint.version)
    self.t.triplifyUnversionedBinaryPackage =\
        self.mockUnversionedBinaryPackage(constraint.package)
    uriref = URIRef(urllib.quote_plus("b/constraint/pkg StrictlyLater 1.0-1", "/"))
    self.assertEqual(uriref, self.t.triplifyConstraint(constraint))
    self.mox.VerifyAll()
    self.assertEqual(5, len(self.graph))
    expected = [(uriref, RDF.type, DEB['SimplePackageConstraint']),\
                (uriref, RDFS.label, Literal("Constraint: pkg (>> 1.0-1)", lang='en')),\
                (uriref, DEB['package'], URIRef("b/binary/pkg")),\
                (uriref, DEB['constraintOperator'], Literal(">>")),\
                (uriref, DEB['versionNumber'], URIRef("b/version/1.0-1"))]
    self.compareGeneratedTriples(expected)

  def testTriplifyOrConstraint(self):
    orconstraint = OrConstraint()
    constraint1 = Constraint()
    constraint1.package = UnversionedBinaryPackage("pkg1")
    constraint2 = Constraint()
    constraint2.package = UnversionedBinaryPackage("pkg2")
    orconstraint.add(constraint1)
    orconstraint.add(constraint2)
    self.t.triplifyConstraint = self.mockTriplifyConstraint([constraint1, constraint2])
    self.assertEqual(BNode, self.t.triplifyOrConstraint(orconstraint).__class__)
    self.mox.VerifyAll()
    self.assertEqual(3, len(self.graph))

  def testTriplifyBinaryPackageBuild(self):
    bs = BinaryPackage("pkg1", "6.7")
    b = BinaryPackageBuild(bs)
    b.architecture = Architecture("arch")
    b.installedSize = "12345"
    self.t.triplifyArchitecture = self.mockTriplifyArchitecture(b.architecture)
    uriref = URIRef("b/binary/pkg1/6.7/arch")
    self.assertEqual(uriref, self.t.triplifyBinaryPackageBuild(b))
    self.assertEqual(4, len(self.graph))
    expected = [(uriref, RDF.type, DEB['BinaryBuild']),\
                (uriref, RDFS.label, Literal("BinaryBuild: pkg1 (6.7) [arch]", lang='en')),\
                (uriref, DEB['installed-size'], Literal(int("12345"))),\
                (uriref, DEB['architecture'], URIRef("b/arch/arch"))]
    self.compareGeneratedTriples(expected)

  def testTriplifyFile(self):
    f = File("testname", "hash", "1234", Directory("test/path"))
    uriref = URIRef("b/path/test/path/testname")
    self.assertEqual(uriref, self.t.triplifyFile(f))
    self.assertEqual(8, len(self.graph))

  def testTriplifyTag(self):
    t = Tag("facet", "tag:tag")
    uriref = URIRef("b/tag/facet/tag%3Atag")
    self.assertEqual(uriref, self.t.triplifyTag(t))
    self.assertEqual(4, len(self.graph))
    expected = [(uriref, RDF.type, TAG['Tag']),\
                (uriref, RDFS.label, Literal("Tag: facet::tag:tag", lang='en')),\
                (uriref, DEB['facet'], Literal("facet")),\
                (uriref, TAG['name'], Literal("tag:tag"))]
    self.compareGeneratedTriples(expected)

  def testTriplifySection(self):
    s = Section("test")
    uriref = URIRef("b/section/test")
    self.assertEqual(uriref, self.t.triplifySection(s))
    self.assertEqual(3, len(self.graph))
    expected = [(uriref, RDF.type, DEB['Section']),\
                (uriref, RDFS.label, Literal("Section: test", lang='en')),\
                (uriref, DEB['sectionName'], Literal("test"))]
    self.compareGeneratedTriples(expected)

  def testTriplifyPriority(self):
    p = PriorityBox.get("optional")
    self.assertEqual(DEB["optional"], self.t.triplifyPriority(p))

  def testTriplifyContributorHuman(self):
    c = Human("Jon Doe", "joe@debian.org")
    uriref = URIRef("b/people/joe%40debian.org")
    self.assertEqual(uriref, self.t.triplifyContributor(c))
    self.assertEqual(4, len(self.graph))
    expected = [(uriref, RDF.type, FOAF['Person']),\
                (uriref, RDFS.label, Literal("Human: joe@debian.org", lang='en')),\
                (uriref, FOAF['name'], Literal("Jon Doe")),\
                (uriref, FOAF['mbox'], Literal("joe@debian.org"))]
    self.compareGeneratedTriples(expected)

  def testTriplifyContributorHumanNoName(self):
    c = Human(None, "joe@debian.org")
    uriref = URIRef("b/people/joe%40debian.org")
    self.assertEqual(uriref, self.t.triplifyContributor(c))
    self.assertEqual(3, len(self.graph))
    expected = [(uriref, RDF.type, FOAF['Person']),\
                (uriref, RDFS.label, Literal("Human: joe@debian.org", lang='en')),\
                (uriref, FOAF['mbox'], Literal("joe@debian.org"))]
    self.compareGeneratedTriples(expected)

  def testTriplifyContributorTeam(self):
    c = Team("Debian Love Team", "love@lists.debian.org")
    uriref = URIRef("b/team/love%40lists.debian.org")
    self.assertEqual(uriref, self.t.triplifyContributor(c))
    self.assertEqual(4, len(self.graph))
    expected = [(uriref, RDF.type, FOAF['Group']),\
                (uriref, RDFS.label, Literal("Team: love@lists.debian.org", lang='en')),\
                (uriref, FOAF['name'], Literal("Debian Love Team")),\
                (uriref, FOAF['mbox'], Literal("love@lists.debian.org"))]
    self.compareGeneratedTriples(expected)

  def testTriplifyTeamAddMemberHumanToGroup(self):
    t = Team("Debian Love Team", "love@lists.debian.org")
    h = Human("Jon Doe", "joe@debian.org")
    tRef = URIRef("b/team/love%40lists.debian.org")
    hRef = URIRef("b/people/joe%40debian.org")
    self.t.triplifyTeamAddMember(t,h)
    self.assertEqual(1, len(self.graph))
    expected = [(tRef, FOAF['member'], hRef)]
    self.compareGeneratedTriples(expected)

  def testTriplifyTeamAddMemberGroupToGroup(self):
    t = Team("Debian Love Team", "love@lists.debian.org")
    tRef = URIRef("b/team/Debian+Love+Team")
    self.t.triplifyTeamAddMember(t,t)
    self.assertEqual(0, len(self.graph))

  def testTriplifyArea(self):
    a = AreaBox.get("main")
    self.assertEqual(DEB["main"], self.t.triplifyArea(a))

  def testTriplifyHomepage(self):
    h = "http://example.org"
    uriref = URIRef(h)
    self.assertEqual(uriref, self.t.triplifyHomepage(h))
    self.assertEqual(1, len(self.graph))
    expected = [(uriref, RDF.type, FOAF['Document'])]
    self.compareGeneratedTriples(expected)

  def testTriplifyUnversionedSourcePackage(self):
    us = UnversionedSourcePackage("name")
    uriref = URIRef("b/source/name")
    self.assertEqual(uriref, self.t.triplifyUnversionedSourcePackage(us))
    self.assertEqual(2, len(self.graph))
    expected = [(uriref, RDF.type, DEB['UnversionedSource']),\
                (uriref, RDFS.label, Literal("Unversioned Source: name", lang='en'))]
    self.compareGeneratedTriples(expected)

  def testTriplifyUnversionedBinaryPackage(self):
    ub = UnversionedBinaryPackage("name")
    uriref = URIRef("b/binary/name")
    self.assertEqual(uriref, self.t.triplifyUnversionedBinaryPackage(ub))
    self.assertEqual(2, len(self.graph))
    expected = [(uriref, RDF.type, DEB['UnversionedBinary']),\
                (uriref, RDFS.label, Literal("Unversioned Binary: name", lang='en'))]
    self.compareGeneratedTriples(expected)

  def testTriplifyRepositoryFull(self):
    r = GitRepository("http://example.com", "git://git.example.com")
    bnode = self.t.triplifyRepository(r)
    self.assertEqual(BNode, bnode.__class__)
    self.assertEqual(5, len(self.graph))
    expected = [(bnode, RDF.type, DOAP['GitRepository']),\
                (bnode, RDFS.label, Literal("Repository: git://git.example.com", lang='en')),\
                (bnode, DOAP['location'], URIRef("git://git.example.com")),\
                (bnode, DOAP['browse'], URIRef("http://example.com")),\
                (URIRef("http://example.com"), RDF.type, FOAF['page'])]
    self.compareGeneratedTriples(expected)

  def testTriplifyRepositoryNoBrowser(self):
    r = GitRepository(None, "git://git.example.com")
    bnode = self.t.triplifyRepository(r)
    self.assertEqual(BNode, bnode.__class__)
    self.assertEqual(3, len(self.graph))
    expected = [(bnode, RDF.type, DOAP['GitRepository']),\
                (bnode, RDFS.label, Literal("Repository: git://git.example.com", lang='en')),\
                (bnode, DOAP['location'], URIRef("git://git.example.com"))]
    self.compareGeneratedTriples(expected)

  def testTriplifyRepositoryNoURI(self):
    r = GitRepository("http://example.com", None)
    bnode = self.t.triplifyRepository(r)
    self.assertEqual(BNode, bnode.__class__)
    self.assertEqual(4, len(self.graph))
    expected = [(bnode, RDF.type, DOAP['GitRepository']),\
                (bnode, RDFS.label, Literal("Repository", lang='en')),\
                (bnode, DOAP['browse'], URIRef("http://example.com")),\
                (URIRef("http://example.com"), RDF.type, FOAF['page'])]
    self.compareGeneratedTriples(expected)

  # Mocks
  def mockTriplifyVersionNumber(self, version):
    classMock = self.mox.CreateMock(Triplifier)
    classMock.triplifyVersionNumber(version)\
                                    .AndReturn(URIRef(version.asURI("b")))
    self.mox.ReplayAll()
    return classMock.triplifyVersionNumber

  def mockTriplifyConstraint(self, constraints):
    classMock = self.mox.CreateMock(Triplifier)
    for constraint in constraints:
      classMock.triplifyConstraint(constraint)\
                                      .InAnyOrder()\
                                      .AndReturn(URIRef(constraint.asURI("b")))
    self.mox.ReplayAll()
    return classMock.triplifyConstraint

  def mockTriplifyArchitecture(self, arch):
    classMock = self.mox.CreateMock(Triplifier)
    classMock.triplifyArchitecture(arch)\
                                  .AndReturn(URIRef(arch.asURI("b")))
    self.mox.ReplayAll()
    return classMock.triplifyArchitecture

  def mockUnversionedBinaryPackage(self, ubinary):
    classMock = self.mox.CreateMock(Triplifier)
    classMock.triplifyUnversionedBinaryPackage(ubinary)\
                                  .AndReturn(URIRef(ubinary.asURI("b")))
    self.mox.ReplayAll()
    return classMock.triplifyUnversionedBinaryPackage
