import unittest

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
    self.t = Triplifier(self.graph, "base")

  def compareGeneratedTriples(self, expected):
    for triple in self.graph.query(ALLTRIPLES):
      self.assertTrue(triple in expected, "%s is not in" % str(triple))
  
  def testTriplifyArchitecture(self):
    arch = Architecture("testArch")
    uriref = URIRef("base/arch/testArch")
    self.assertEqual(uriref, self.t.triplifyArchitecture(arch))
    self.assertEqual(1, len(self.graph))
    expected = [(uriref, RDF.type, DEB['Architecture'])]
    self.compareGeneratedTriples(expected)

  def testTriplifyVersionNumberSimple(self):
    version = VersionNumber("1.0-1")
    uriref = URIRef("base/version/1.0-1")
    self.assertEqual(uriref, self.t.triplifyVersionNumber(version))
    self.assertEqual(3, len(self.graph))
    expected = [(uriref, RDF.type, DEB['VersionNumber']),\
                (uriref, DEB['upstreamVersion'], Literal("1.0")),\
                (uriref, DEB['debianRevision'], Literal("1"))]
    self.compareGeneratedTriples(expected)
