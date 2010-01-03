import unittest
import hashlib
import mox
import optparse

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

ALLTRIPLES = BQ + "SELECT ?x ?y ?z WHERE { ?x ?y ?z . }"

class TriplifierTest(unittest.TestCase):
  def setUp(self):
    values = optparse.Values()
    values.ensure_value("baseURI", "b")
    self.graph = ConjunctiveGraph()
    self.t = Triplifier(self.graph, values)
    self.mox = mox.Mox()

  def compareGeneratedTriples(self, expected):
    for triple in self.graph.query(ALLTRIPLES):
      self.assertTrue(triple in expected, "%s is not in" % str(triple))
  
  def testTriplifyArchitecture(self):
    arch = Architecture("testArch")
    uriref = URIRef("b/arch/testArch")
    self.assertEqual(uriref, self.t.triplifyArchitecture(arch))
    self.assertEqual(2, len(self.graph))
    expected = [(uriref, RDF.type, DEB['Architecture']),\
                (uriref, RDFS.label, Literal("Architecture: testArch"))]
    self.compareGeneratedTriples(expected)

  def testTriplifyArchitectureOntologyInstance(self):
    arch = Architecture("all")
    self.assertEqual(DEB['all'], self.t.triplifyArchitecture(arch))

  def testTriplifyVersionNumberSimple(self):
    version = VersionNumber("1.0-1")
    uriref = URIRef("b/version/1.0-1")
    self.assertEqual(uriref, self.t.triplifyVersionNumber(version))
    self.assertEqual(3, len(self.graph))
    expected = [(uriref, RDF.type, DEB['VersionNumber']),\
                (uriref, DEB['upstreamVersion'], Literal("1.0")),\
                (uriref, DEB['debianRevision'], Literal("1"))]
    self.compareGeneratedTriples(expected)

  def testTriplifyConstraintSimple(self):
    constraint = Constraint()
    constraint.package = "pkg"
    constraint.operator = ">>"
    constraint.version = VersionNumber("1.0-1")
    self.t.triplifyVersionNumber =\
        self.mockTriplifyVersionNumber(constraint.version)
    uriref = URIRef("b/constraint/%s" %\
        hashlib.sha1(constraint.package + constraint.operator +\
        str(constraint.version)).hexdigest())
    self.assertEqual(uriref, self.t.triplifyConstraint(constraint))
    self.mox.VerifyAll()
    self.assertEqual(5, len(self.graph))
    expected = [(uriref, RDF.type, DEB['SimplePackageConstraint']),\
                (uriref, RDFS.label, Literal("Constraint: pkg (>> 1.0-1)")),\
                (uriref, DEB['packageName'], Literal("pkg")),\
                (uriref, DEB['constraintOperator'], Literal(">>")),\
                (uriref, DEB['versionNumber'], URIRef("b/version/1.0-1"))]
    self.compareGeneratedTriples(expected)

  def testTriplifyOrConstraint(self):
    orconstraint = OrConstraint()
    constraint1 = Constraint()
    constraint1.package = "pkg1"
    constraint2 = Constraint()
    constraint2.package = "pkg2"
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
                (uriref, RDFS.label, Literal("BinaryBuild: pkg1 (6.7) [arch]")),\
                (uriref, DEB['installed-size'], Literal("12345")),\
                (uriref, DEB['architecture'], URIRef("b/arch/arch"))]
    self.compareGeneratedTriples(expected)

  def testTriplifyFile(self):
    f = File("testname", "hash", "size", Directory("test/path"))
    uriref = URIRef("b/path/test/path/testname")
    self.assertEqual(uriref, self.t.triplifyFile(f))
    self.assertEqual(8, len(self.graph))

  def testTriplifyTag(self):
    t = Tag("facet", "tag:tag")
    uriref = URIRef("b/tag/facet/tag:tag")
    self.assertEqual(uriref, self.t.triplifyTag(t))
    self.assertEqual(4, len(self.graph))
    expected = [(uriref, RDF.type, TAG['Tag']),\
                (uriref, RDFS.label, Literal("Tag: facet::tag:tag")),\
                (uriref, DEB['facet'], Literal("facet")),\
                (uriref, TAG['name'], Literal("tag:tag"))]
    self.compareGeneratedTriples(expected)

  def testTriplifySection(self):
    s = Section("test")
    uriref = URIRef("b/section/test")
    self.assertEqual(uriref, self.t.triplifySection(s))
    self.assertEqual(3, len(self.graph))
    expected = [(uriref, RDF.type, DEB['Section']),\
                (uriref, RDFS.label, Literal("Section: test")),\
                (uriref, DEB['sectionName'], Literal("test"))]
    self.compareGeneratedTriples(expected)

  def testTriplifyPriority(self):
    p = Priority("test")
    uriref = URIRef("b/priority/test")
    self.assertEqual(uriref, self.t.triplifyPriority(p))
    self.assertEqual(3, len(self.graph))
    expected = [(uriref, RDF.type, DEB['Priority']),\
                (uriref, RDFS.label, Literal("Priority: test")),\
                (uriref, DEB['priorityName'], Literal("test"))]
    self.compareGeneratedTriples(expected)

  def testTriplifyContributorHuman(self):
    c = Human("Jon Doe", "joe@debian.org")
    uriref = URIRef("b/people/Jon_Doe")
    self.assertEqual(uriref, self.t.triplifyContributor(c))
    self.assertEqual(4, len(self.graph))
    expected = [(uriref, RDF.type, FOAF['Person']),\
                (uriref, RDFS.label, Literal("Human: Jon Doe <joe@debian.org>")),\
                (uriref, FOAF['name'], Literal("Jon Doe")),\
                (uriref, FOAF['mbox'], Literal("joe@debian.org"))]
    self.compareGeneratedTriples(expected)

  def testTriplifyContributorTeam(self):
    c = Team("Debian Love Team", "love@lists.debian.org")
    uriref = URIRef("b/team/Debian_Love_Team")
    self.assertEqual(uriref, self.t.triplifyContributor(c))
    self.assertEqual(4, len(self.graph))
    expected = [(uriref, RDF.type, FOAF['Group']),\
                (uriref, RDFS.label, Literal("Team: Debian Love Team <love@lists.debian.org>")),\
                (uriref, FOAF['name'], Literal("Debian Love Team")),\
                (uriref, FOAF['mbox'], Literal("love@lists.debian.org"))]
    self.compareGeneratedTriples(expected)

  def testTriplifyTeamAddMemberHumanToGroup(self):
    t = Team("Debian Love Team", "love@lists.debian.org")
    h = Human("Jon Doe", "joe@debian.org")
    tRef = URIRef("b/team/Debian_Love_Team")
    hRef = URIRef("b/people/Jon_Doe")
    self.t.triplifyTeamAddMember(t,h)
    self.assertEqual(1, len(self.graph))
    expected = [(tRef, FOAF['member'], hRef)]
    self.compareGeneratedTriples(expected)

  def testTriplifyTeamAddMemberGroupToGroup(self):
    t = Team("Debian Love Team", "love@lists.debian.org")
    tRef = URIRef("b/team/Debian_Love_Team")
    self.t.triplifyTeamAddMember(t,t)
    self.assertEqual(0, len(self.graph))

  def testTriplifyArea(self):
    a = Area("main")
    self.assertEqual(DEB["main"], self.t.triplifyArea(a))

  def testTriplifyHomepage(self):
    h = "http://example.org"
    uriref = URIRef(h)
    self.assertEqual(uriref, self.t.triplifyHomepage(h))
    self.assertEqual(1, len(self.graph))
    expected = [(uriref, RDF.type, FOAF['Document'])]
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

