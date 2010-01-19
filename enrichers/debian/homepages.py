#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Nacho Barrientos Arias <nacho@debian.org>
#
# License: MIT

import sys
import logging
import random
import urllib
import re

from optparse import OptionParser
from urlparse import urljoin
from xml.sax import SAXParseException

from rdflib.Graph import ConjunctiveGraph
from rdflib import Namespace, URIRef, Literal, BNode
from SPARQLWrapper import SPARQLWrapper2

from tools.pool import GraphPool
from homepages.io import LinkRetrieval
from homepages.io import homepages, w3c_validator
from homepages.errors import W3CValidatorError

VERSION = "beta"

RDFS = Namespace(u"http://www.w3.org/2000/01/rdf-schema#")
FOAF = Namespace(u"http://xmlns.com/foaf/0.1/")
RDF = Namespace(u"http://www.w3.org/1999/02/22-rdf-syntax-ns#")
DEB = Namespace(u"http://idi.fundacionctic.org/steamy/debian.owl#")
DOAP = Namespace(u"http://usefulinc.com/ns/doap#")
XHV = Namespace(u"http://www.w3.org/1999/xhtml/vocab#")
EARL = Namespace(u"http://www.w3.org/ns/earl#")

class HomepageEnricher():
    def __init__(self):
        self.opts = None

    def initData(self):
        self.pool = GraphPool(self.opts.pool, self.opts.prefix, self.opts.basedir)
        #self.endpoint = SPARQLWrapper2(self.opts.endpoint)

    def parseArgs(self):
        parser = OptionParser(usage="%prog [options]", version="%prog " + VERSION)
        parser.add_option("-e", "--endpoint", dest="endpoint",\
                          metavar="URI", help="use URI as SPARQL endpoint")
        parser.add_option("-o", "--output-prefix", dest="prefix",\
                      default="Meta",\
                      metavar="PREFIX", help="dump output to PREFIX-{index}.rdf [default: %default]")
        parser.add_option("-b", "--base-dir", dest="basedir",\
                      default=".",\
                      metavar="DIR", help="use DIR as base directory to store output files [default: %default]")
        parser.add_option("-p", "--pool-size", dest="pool",\
                      default="1",\
                      metavar="NUM", help="set graph pool size to NUM [default: %default]")
        parser.add_option("-w", "--w3c", action="store_true", dest="w3c",\
                      default=False, help="validates homeapages against validator.w3.org")
        parser.add_option("-d", "--discover", action="store_true", dest="discover",\
                      default=False, help="navigates link tags and retrieves metadata")
        parser.add_option("-v", "--verbose", action="store_true", dest="verbose",\
                      default=False, help="increases debug level")
        parser.add_option("-q", "--quiet", action="store_true", dest="quiet",\
                      default=False,\
                      help="decreases debug level (only errors are shown)")

        (self.opts, args) = parser.parse_args()

    #if not self.opts.endpoint:
    #  raise Exception("Cannot continue, Endpoint URI (-e) is not set.")
        if self.opts.verbose and self.opts.quiet:
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

        for homepage in homepages():
            self.process_homepage(homepage)
       
        if self.pool.count_triples() > 0:
            logging.info("Serializing graphs...")
            self.pool.serialize()

    ## Logic ##

    def process_homepage(self, uri):
        # Validation
        if self.opts.w3c:
            logging.info("Validating '%s' markup" % uri)
            self.validate_markup(uri)
        # Metainformation retrieval
        if self.opts.discover:
            logging.info("Extracting metadata from '%s'" % uri)
            self.discover(uri)

    def validate_markup(self, uri):
        try:
            result = w3c_validator(uri)
        except W3CValidatorError, e:
            logging.error(str(e))

        if result is True:
            logging.debug("Validation passed")
            self._push_validation_success(uri)
        else:
            logging.debug("Validation failed")
            self._push_validation_failure(uri)

    def discover(self, uri):
        stream = urllib.urlopen(uri)
        parser = LinkRetrieval()
        parser.feed(stream.read())
        stream.close()
        parser.close()
        # RSS processing
        logging.info("Discovering data from RSS feeds...")
        self.discover_rss(uri, map(lambda x: urljoin(uri, x), parser.get_rss_hrefs()))
        # META processing
        logging.info("Discovering data from meta headers...")
        self.discover_meta(uri, map(lambda x: urljoin(uri, x), parser.get_rdf_meta_hrefs()))

    def discover_rss(self, homepage, candidates):
        for uri in candidates:
            self.pool.add_triple((URIRef(homepage), XHV.alternate, URIRef(uri)))
            self.pool.add_triple((URIRef(uri), RDFS.type, FOAF.Document))
            logging.debug("Trying to determine RSS feed format for uri '%s'" % uri)
            graph = ConjunctiveGraph()
            try:
                graph.parse(uri, format="xml")
                #self.pool.merge_graph(graph)
            except SAXParseException:
                logging.debug("'%s' does not look like RDF" % uri)
            logging.debug("Looks like it is RDF (RSS 1.x)")
            logging.debug("Got %s triples from '%s'" % (len(graph), uri))

    def discover_meta(self, homepage, candidates):
        for uri in candidates:
            self.pool.add_triple((URIRef(homepage), XHV.meta, URIRef(uri)))
            self.pool.add_triple((URIRef(uri), RDFS.type, FOAF.Document))
            logging.debug("Analyzing '%s'" % uri)

    # Validation results helpers

    def _push_validation_success(self, uri):
        assertion = self._push_generic_validation(uri)
        result = BNode()
        self.pool.add_triple((result, EARL.outcome, EARL.passed))
        self.pool.add_triple((assertion, EARL.result, result))

    def _push_validation_failure(self, uri):
        assertion = self._push_generic_validation(uri)
        result = BNode()
        self.pool.add_triple((result, RDF.type, EARL.TestResult))
        self.pool.add_triple((result, EARL.outcome, EARL.failed))
        self.pool.add_triple((assertion, EARL.result, result))

    def _push_generic_validation(self, uri):
        assertion = BNode()
        subject = URIRef(uri)
        self.pool.add_triple((assertion, RDF.type, EARL.Assertion))
        self.pool.add_triple((subject, RDF.type, EARL.TestSubject))
        self.pool.add_triple((assertion, EARL.testCase, DEB.W3CValidationTest))
        self.pool.add_triple((assertion, EARL.subject, subject))
        self.pool.add_triple((assertion, EARL.mode, EARL.automatic))
        return assertion
        

if __name__ == "__main__":
  HomepageEnricher().run()
