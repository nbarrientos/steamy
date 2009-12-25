import unittest
import hashlib

from rdflib.Graph import ConjunctiveGraph
from rdflib import Namespace, URIRef, BNode, Literal

from models import *
from export import Triplifier

BQ = """
PREFIX deb:<http://idi.fundacionctic.org/steamy/debian.owl#>
PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>

"""

RDF = Namespace(u"http://www.w3.org/1999/02/22-rdf-syntax-ns#")
DEB = Namespace(u"http://idi.fundacionctic.org/steamy/debian.owl#")

ALLTRIPLES = BQ + "SELECT ?x ?y ?z WHERE { ?x ?y ?z . }"

class TriplifierTest(unittest.TestCase):
  def setUp(self):
    self.graph = ConjunctiveGraph()
    self.t = Triplifier(self.graph, "b")
    self.base = "b"

  def compareGeneratedTriples(self, expected):
    for triple in self.graph.query(ALLTRIPLES):
      self.assertTrue(triple in expected, "%s is not in" % str(triple))
  
  def testTriplifyArchitecture(self):
    arch = Architecture("testArch")
    uriref = URIRef("b/arch/testArch")
    self.assertEqual(uriref, self.t.triplifyArchitecture(arch))
    self.assertEqual(1, len(self.graph))
    expected = [(uriref, RDF.type, DEB['Architecture'])]
    self.compareGeneratedTriples(expected)

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
    self.t.triplifyVersionNumber = self.mockTriplifyVersionNumber("b")
    uriref = URIRef("b/constraint/%s" %\
        hashlib.sha1(constraint.package + constraint.operator +\
        str(constraint.version)).hexdigest())
    self.assertEqual(uriref, self.t.triplifyConstraint(constraint))
    self.assertEqual(4, len(self.graph))
    expected = [(uriref, RDF.type, DEB['SimplePackageConstraint']),\
                (uriref, DEB['packageName'], Literal("pkg")),\
                (uriref, DEB['constraintOperator'], Literal(">>")),\
                (uriref, DEB['versionNumber'], URIRef("b/version/1.0-1"))]
    self.compareGeneratedTriples(expected)


  # Mocks

  # FIXME: Use pmock, mox, ... instead.
  def mockTriplifyVersionNumber(self, base):
    def f(version):
      return URIRef(version.asURI(base))
    return f
