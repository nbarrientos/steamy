#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Nacho Barrientos Arias <nacho@debian.org>
#
# License: MIT

import sys
import logging
import random

from optparse import OptionParser

from SPARQLWrapper import SPARQLWrapper2
from debian_bundle.changelog import Version
from rdflib import Namespace, URIRef
from rdflib.Graph import ConjunctiveGraph

VERSION = "0.1alpha"

DEB = Namespace(u"http://idi.fundacionctic.org/steamy/debian.owl#")

class GraphPool():
  def __init__(self, size, prefix, base):
    self.prefix = "%s/%s" % (base, prefix)
    self.pool = [ConjunctiveGraph() for i in range(int(size))]
    for graph in self.pool:
      graph.bind("deb", DEB)

  def addTriple(self, triple):
    self.pool[int(random.uniform(0, len(self.pool)))].add(triple)

  def countTriples(self):
    return sum([len(i) for i in self.pool])

  def serialize(self):
    for i in range(len(self.pool)): # I'm sorry :(    
      try:
        f = open("%s-%d.rdf" % (self.prefix, i), "w")
        f.write(self.pool[i].serialize())
        f.close()
      except IOError, e:
        logging.error("Serialization failed: %s (does base dir exist?)", e)

class ConstraintResolver():
  def __init__(self):
    self.opts = None

  def initData(self):
    self.endpoint = SPARQLWrapper2(self.opts.endpoint)
    self.pool = GraphPool(self.opts.pool, self.opts.prefix, self.opts.basedir)

  def parseArgs(self):
    parser = OptionParser(usage="%prog [options]", version="%prog " + VERSION)
    parser.add_option("-e", "--endpoint", dest="endpoint",\
                      metavar="URI", help="use URI as SPARQL endpoint")
    parser.add_option("-o", "--output-prefix", dest="prefix",\
                      default="Safisfies",\
                      metavar="PREFIX", help="dump output to PREFIX-{index}.rdf [default: %default]")
    parser.add_option("-b", "--base-dir", dest="basedir",\
                      default=".",\
                      metavar="DIR", help="use DIR as base directory to store output files [default: %default]")
    parser.add_option("-p", "--pool-size", dest="pool",\
                      default="1",\
                      metavar="NUM", help="set graph pool size to NUM [default: %default]")
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
          { ?ub deb:version ?b . } # Straight
          UNION 
          { ?b deb:provides ?or . # Through provides
            ?or deb:alternative ?a .
            ?a deb:package ?ub . }
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
    (self.pool.countTriples(), counter))

    self.pool.serialize()
    
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
    self.pool.addTriple((URIRef(binaryPackage), DEB['satisfies'], URIRef(constraint)))

if __name__ == "__main__":
  ConstraintResolver().run()
