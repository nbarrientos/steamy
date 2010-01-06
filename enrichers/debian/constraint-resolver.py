#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Nacho Barrientos Arias <nacho@debian.org>
#
# License: MIT

import sys
import logging

from optparse import OptionParser

from SPARQLWrapper import SPARQLWrapper2
from debian_bundle.changelog import Version
from rdflib import Namespace, URIRef
from rdflib.Graph import ConjunctiveGraph

VERSION = "0.1alpha"

DEB = Namespace(u"http://idi.fundacionctic.org/steamy/debian.owl#")

class ConstraintResolver():
  def __init__(self):
    self.opts = None

  def initData(self):
    self.endpoint = SPARQLWrapper2(self.opts.endpoint)
    self.graph = ConjunctiveGraph()
    self.graph.bind("deb", DEB)
    self.f = open(self.opts.output, "w")

  def parseArgs(self):
    parser = OptionParser(usage="%prog [options]", version="%prog " + VERSION)
    parser.add_option("-e", "--endpoint", dest="endpoint",\
                      metavar="URI", help="use URI as SPARQL endpoint")
    parser.add_option("-o", "--output", dest="output",\
                      default="Safisfies.rdf",\
                      metavar="FILE", help="dump output to FILE [default: %default]")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",\
                      default=False, help="increases debug level")
    parser.add_option("-q", "--quiet", action="store_true", dest="quiet",\
                      default=False,\
                      help="decreases debug level (only errors are shown)")

    (self.opts, args) = parser.parse_args()

    if not self.opts.endpoint:
      raise Exception("Cannot continue, Endpoint URI (-e) is not set.")
    elif self.opts.verbose and self.opts.quiet:
      raise Exception("Verbose (-v) and Quiet (-q) are mutually exclusive")

  def configLogger(self):
    if self.opts.verbose:
      lvl = logging.DEBUG
    elif self.opts.quiet:
      lvl = logging.ERROR
    else:
      lvl = logging.INFO

    logging.basicConfig(level=lvl, format='%(message)s')

  def run(self):
    try:
      self.parseArgs()
    except Exception, e:
      print >> sys.stderr, str(e)
      sys.exit(2)

    self.configLogger()
    self.initData()
    self.resolveConstraints()

  ##### Logic #####

  def queryEndpoint(self, query):
    self.endpoint.setQuery(query)
    return self.endpoint.query()

  def getCandidateLinksBindings(self):
    q = """
        PREFIX deb: <http://idi.fundacionctic.org/steamy/debian.owl#>
        SELECT ?b ?c ?bvn ?cvn ?op
        WHERE { 
          ?ub deb:version ?b .
          ?b deb:versionNumber ?bvn .
          ?c deb:package ?ub .
          OPTIONAL { ?c deb:versionNumber ?cvn . } .
          OPTIONAL { ?c deb:constraintOperator ?op . } .
        }
    """
    
    r = self.queryEndpoint(q)
    return r["b", "c", "bvn"]

  def resolveConstraints(self):
    counter = 0
    vcounter = 0

    for b in self.getCandidateLinksBindings():
        counter = counter + 1
        binaryPackage = b["b"].value
        constraint = b["c"].value
        binaryPackageVersion = b["bvn"].value
          
        logging.debug("\nTrying to resolve <%s> -> <%s>" % (binaryPackage, constraint))

        try:
          constraintVersion = b["cvn"].value
          constraintOperator = b["op"].value
        except KeyError:
          constraintVersion = None
          constraintOperator = None
        
        if constraintVersion and constraintOperator:
          cvObject = self.composeVersion(constraintVersion)
          bvObject = self.composeVersion(binaryPackageVersion)
          if self.isVersionedConstraintSatisfied(cvObject, bvObject, constraintOperator):
            self.satisfyConstraint(binaryPackage, constraint)
        else:
            self.satisfyConstraint(binaryPackage, constraint)

    logging.info("Satisfied %s dependencies out of %s possible matches" % \
    (len(self.graph), counter))

    self.f.write(self.graph.serialize())
    self.f.close()

  def composeVersion(self, versionURI):
    q = """
        PREFIX deb: <http://idi.fundacionctic.org/steamy/debian.owl#>
        SELECT ?v
        WHERE { 
          <%s> deb:fullVersion ?v .
        }
    """ % versionURI
    r = self.queryEndpoint(q)

    v = r["v"][0]["v"].value

    return Version(v)

  def isVersionedConstraintSatisfied(self, constraintVersion, packageVersion, op):
    mappings = {'=':'==', '>>':'>', '<<':'<', '<':'<=', '>':'>='}
    if op in mappings:
      op = mappings[op]

    return eval("packageVersion %s constraintVersion" % op)

  def satisfyConstraint(self, binaryPackage, constraint):
    logging.debug("True! Adding <%s> deb:satisfies <%s>" % \
    (binaryPackage, constraint))
    self.graph.add((URIRef(binaryPackage), DEB['satisfies'], URIRef(constraint)))

if __name__ == "__main__":
  ConstraintResolver().run()
