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

from tools.pool import GraphPool

VERSION = "0.1alpha"

DEB = Namespace(u"http://idi.fundacionctic.org/steamy/debian.owl#")


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
    parser.add_option("-g", "--graph", dest="graph",\
                      metavar="URI", help="use URI as FROM graph")
    parser.add_option("-o", "--output-prefix", dest="prefix",\
                      default="Satisfies",\
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
        %s
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
    """ % ("FROM <%s>" % self.opts.graph if self.opts.graph is not None else "")
    
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
    (self.pool.count_triples(), counter))

    self.pool.serialize()
    
  def composeVersion(self, versionURI):
    q = """
        PREFIX deb: <http://idi.fundacionctic.org/steamy/debian.owl#>
        SELECT ?v
        %s
        WHERE { 
          <%s> deb:fullVersion ?v .
        }
    """ % ("FROM <%s>" % self.opts.graph if self.opts.graph is not None else "", versionURI)
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
    self.pool.add_triple((URIRef(binaryPackage), DEB['satisfies'], URIRef(constraint)))

if __name__ == "__main__":
  ConstraintResolver().run()
