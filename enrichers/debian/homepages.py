#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Nacho Barrientos Arias <nacho@debian.org>
#
# License: MIT

import sys
import time
import logging
import httplib
import urllib2
import re

from sgmllib import SGMLParseError
from optparse import OptionParser
from urlparse import urljoin
from xml.sax import SAXParseException

from rdflib.Graph import ConjunctiveGraph

from tools.pool import GraphPool
from homepages.io import LinkRetrieval, TripleProcessor
from homepages.io import homepages, w3c_validator
from homepages.errors import W3CValidatorError
from homepages.models import Stats

VERSION = "beta"

class HomepageEnricher():
    def __init__(self):
        self.opts = None

    def initData(self):
        pool = GraphPool(self.opts.pool, self.opts.prefix, self.opts.basedir)
        self.triples = TripleProcessor(pool)
        self.htmlparser = LinkRetrieval()
        self.stats = Stats()

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
                      default="1", type="int",\
                      metavar="NUM", help="set graph pool size to NUM [default: %default]")
        parser.add_option("-w", "--w3c", action="store_true", dest="w3c",\
                      default=False, help="validates homeapages against validator.w3.org")
        parser.add_option("-d", "--discover", action="store_true", dest="discover",\
                      default=False, help="navigates link tags and retrieves metadata")
        parser.add_option("-s", "--sleep-time", dest="sleep",\
                      default="5", type="int",\
                      metavar="SECS", help="sleep SECS after querying validator.w3.org [default: %default]")
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
       
        self.triples.request_serialization()

        logging.info(self.stats)

    ## Logic ##

    def process_homepage(self, uri):
        self.stats.count_homepage()
        logging.info("\nProcessing '%s'" % uri)
        # Is it usable?
        try:
            stream = urllib2.urlopen(uri)
        except urllib2.URLError, e: # Includes 404
            self.stats.count_brokenhomepage()
            logging.error("'%s' is unreachable (reason: %s), skipping..." % (uri, e))
            return

        # Metainformation retrieval
        if self.opts.discover:
            logging.info("Discovering metadata...")
            self.discover(uri, stream)
        # Validation
        if self.opts.w3c:
            logging.info("Validating markup...")
            self.validate_markup(uri)
 
    def validate_markup(self, uri):
        try:
            result = w3c_validator(uri)
        except W3CValidatorError, e:
            logging.error(str(e))

        if result is True:
            logging.debug("\tValidation passed")
            self.triples.push_validation_success(uri)
            self.stats.count_validmarkup()
        else:
            logging.debug("\tValidation failed")
            self.triples.push_validation_failure(uri)

        time.sleep(self.opts.sleep)

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
        
        logging.info("\tDiscovering RSS feeds...")
        for candidate in self.htmlparser.get_rss_hrefs():
            self.discover_rss(homepage, urljoin(homepage, candidate))
        
        logging.info("\tDiscovering RDF...")
        for candidate in self.htmlparser.get_rdf_meta_hrefs():
            self.discover_meta(homepage, urljoin(homepage, candidate))

        self.htmlparser.reset()

    def discover_rss(self, homepage, feed):
        self.triples.push_alternate(homepage, feed)
        self.stats.count_feed()
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
        self.triples.push_meta(homepage, candidate)
        self.stats.count_rdf()
        logging.debug("Analyzing '%s'" % candidate)
        if re.match(r".*\.rdf$", candidate) is not None:
            graph = ConjunctiveGraph()
            try:
                graph.parse(candidate)
            except SAXParseException, e:
                self.stats.count_invalidrdf()
                logging.error("Unable to parse '%s'" % candidate)
                return
            
            self.triples.push_graph(graph)

            logging.debug("%s triples extracted and merged" % len(graph))


if __name__ == "__main__":
  HomepageEnricher().run()
