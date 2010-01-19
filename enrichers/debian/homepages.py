#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Nacho Barrientos Arias <nacho@debian.org>
#
# License: MIT

import sys
import logging
import httplib
import urllib2
import re

from sgmllib import SGMLParseError
from optparse import OptionParser
from urlparse import urljoin
from xml.sax import SAXParseException

from rdflib.Graph import ConjunctiveGraph
from rdflib import Namespace, URIRef, Literal, BNode

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
        self.htmlparser = LinkRetrieval()

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

        for homepage in homepages(self.opts.endpoint):
            self.process_homepage(homepage)
       
        if self.pool.count_triples() > 0:
            logging.info("Serializing graphs...")
            self.pool.serialize()

    ## Logic ##

    def process_homepage(self, uri):
        logging.info("\nProcessing '%s'" % uri)
        # Is it usable?
        try:
            stream = urllib2.urlopen(uri)
        except urllib2.URLError, e: # Includes 404
            logging.error("'%s' is unreachable (reason: %s), skipping..." % (uri, e))
            return

        logging.debug("Host seems active and web server is not returning 404")
        # Metainformation retrieval
        if self.opts.discover:
            logging.info("Extracting metadata from '%s'" % uri)
            self.discover(uri, stream)
        # Validation
        if self.opts.w3c:
            logging.info("Validating '%s' markup" % uri)
            self.validate_markup(uri)
 
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

    def discover(self, homepage, stream):
        try:
            self.htmlparser.feed(stream.read())
        except SGMLParseError, e:
            logging.error("Parser error (%s). Skipping '%s'..." % (e, homepage))
            self.htmlparser.reset()
            return
        finally:
            stream.close()

        self.htmlparser.close()
        
        logging.info("Discovering data from RSS feeds...")
        for candidate in self.htmlparser.get_rss_hrefs():
            self.discover_rss(homepage, urljoin(homepage, candidate))
        
        logging.info("Discovering data from meta headers...")
        for candidate in self.htmlparser.get_rdf_meta_hrefs():
            self.discover_meta(homepage, urljoin(homepage, candidate))

        self.htmlparser.reset()

    def discover_rss(self, homepage, feed):
        self.pool.add_triple((URIRef(homepage), XHV.alternate, URIRef(feed)))
        self.pool.add_triple((URIRef(feed), RDFS.type, FOAF.Document))
        logging.debug("Trying to determine RSS feed format for uri '%s'" % feed)
        
        # TODO: Determine RSS format:
        # 1.0: RDF - get, parse and merge graph
        # 2.0: XML - get, transform and merge graph

        #graph = ConjunctiveGraph()
        #try:
        #    graph.parse(feed, format="xml")
        #    #self.pool.merge_graph(graph)
        #except SAXParseException:
        #    logging.debug("'%s' does not look like RDF" % feed)

        #logging.debug("Looks like it is RDF (RSS 1.x)")
        #logging.debug("Got %s triples from '%s'" % (len(graph), feed))

    def discover_meta(self, homepage, candidate):
        self.pool.add_triple((URIRef(homepage), XHV.meta, URIRef(candidate)))
        self.pool.add_triple((URIRef(candidate), RDFS.type, FOAF.Document))
        logging.debug("Analyzing '%s'" % candidate)
        # FIXME

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
