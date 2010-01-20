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
import socket
import re

import feedparser
from Ft.Xml import InputSource
from Ft.Xml.Xslt import Processor

from StringIO import StringIO
from sgmllib import SGMLParseError
from optparse import OptionParser
from urlparse import urljoin
from xml.sax import SAXParseException

from rdflib.Graph import ConjunctiveGraph

from tools.pool import GraphPool
from homepages.io import LinkRetrieval, TripleProcessor
from homepages.io import homepages, w3c_validator
from homepages.errors import W3CValidatorError, RSSParsingError
from homepages.errors import RSSParsingFeedUnavailableError
from homepages.errors import RSSParsingFeedMalformedError
from homepages.errors import RSSParsingUnparseableVersionError
from homepages.errors import RDFDiscoveringError
from homepages.errors import RDFDiscoveringBrokenLinkError
from homepages.errors import RDFDiscoveringMalformedError
from homepages.models import Stats

VERSION = "beta"

# From: http://w3future.com/weblog/2002/09/
# Supports: rss094, rss20
RSS_2_RDF_XSL = "/home/nacho/steamy/git/enrichers/debian/rss2rdf.xsl"

# Grabbed from http://djpowell.net/blog/entries/Atom-RDF.html
# Supports: atom10, rss091, rss20, atom30
#RSS_ATOM_2_ATOM_RDF_XSL = \
#        "/home/nacho/steamy/git/enrichers/debian/tools/atom2rdf-16/atom2rdf-16.xsl"

class HomepageEnricher():
    def __init__(self):
        self.opts = None

    def initData(self):
        pool = GraphPool(self.opts.pool, self.opts.prefix, self.opts.basedir)
        self.triples = TripleProcessor(pool)
        self.htmlparser = LinkRetrieval()
        self.stats = Stats()
        socket.setdefaulttimeout(10)

    def parseArgs(self):
        parser = OptionParser(usage="%prog [options]", version="%prog " + VERSION)
        parser.add_option("-e", "--endpoint", dest="endpoint",\
                          metavar="URI", help="use URI as SPARQL endpoint")
        parser.add_option("-g", "--graph", dest="graph",\
                          metavar="URI", help="use URI as FROM graph")
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

        for homepage in homepages(self.opts.endpoint, self.opts.graph):
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
            try:
                self.discover_rss(homepage, urljoin(homepage, candidate))
            except RSSParsingError, e:
                logging.error("\t%s" % e)
        
        logging.info("\tDiscovering RDF...")
        for candidate in self.htmlparser.get_rdf_meta_hrefs():
            try:
                self.discover_meta(homepage, urljoin(homepage, candidate))
            except RDFDiscoveringError, e:
                logging.error("\t%s" % e)

        self.htmlparser.reset()

    def discover_rss(self, homepage, feed):
        self.triples.push_alternate(homepage, feed)
        self.stats.count_feed()
        logging.debug("\tTrying to determine RSS feed version for URI '%s'" % feed)

        parse = feedparser.parse(feed)

        if parse.status in (httplib.NOT_FOUND, httplib.GONE):
            self.stats.count_invalidfeed()
            raise RSSParsingFeedUnavailableError()
        elif parse.bozo:
            self.stats.count_invalidfeed()
            raise RSSParsingFeedMalformedError()
        else:
            graph = ConjunctiveGraph()
            if parse.version in ("rss10"):
                logging.debug("\tLooks like RDF (%s)" % parse.version)
                graph.parse(feed, format="xml")
            elif parse.version in ("rss20", "rss094"): #, ("atom10", "atom30", "rss20"):
                logging.debug("\tLooks like XML (%s)" % parse.version)
                graph.parse(StringIO(self._transform_feed(feed)), format="xml")
            else:
                self.stats.count_invalidfeed()
                raise RSSParsingUnparseableVersionError(parse.version)

            if 'link' in parse.channel:
                logging.debug("\tLinking '%s' to '%s'" % (feed, parse.channel.link))
                self.triples.push_rss_channel(feed, parse.channel.link)
                self.triples.push_graph(graph)
                logging.debug("\t%s triples extracted and merged" % len(graph))
            else:
                logging.error("\tUnable to link feed '%s' to any channel. Not merging." % feed)
        
    def discover_meta(self, homepage, candidate):
        self.triples.push_meta(homepage, candidate)
        self.stats.count_rdf()
        logging.debug("\tAnalyzing '%s'" % candidate)
        if re.match(r".*\.rdf$", candidate) is not None:
            graph = ConjunctiveGraph()
            try:
                graph.parse(candidate)
            except SAXParseException:
                self.stats.count_invalidrdf()
                raise RDFDiscoveringMalformedError()
            except urllib2.URLError:
                self.stats.count_invalidrdf()
                raise RDFDiscoveringBrokenLinkError()
            
            self.triples.push_graph(graph)
            logging.debug("\t%s triples extracted and merged" % len(graph))

    def _transform_feed(self, feeduri):
        document = InputSource.DefaultFactory.fromUri(feeduri)  
        stylesheet = InputSource.DefaultFactory.fromUri(RSS_2_RDF_XSL)
        processor = Processor.Processor()
        processor.appendStylesheet(stylesheet)
        logging.debug("\tApplying XSL transformation...")
        rdfstring = processor.run(document)
        return rdfstring


if __name__ == "__main__":
  HomepageEnricher().run()
