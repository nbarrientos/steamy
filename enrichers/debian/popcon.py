#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Nacho Barrientos Arias <nacho@debian.org>
#
# License: MIT

import sys
import logging
import urllib
import re

from optparse import OptionParser

from rdflib import Namespace, URIRef, Literal

from tools.pool import GraphPool

VERSION = "0.1alpha"

DEB = Namespace(u"http://idi.fundacionctic.org/steamy/debian.owl#")


class PopconEnricher():
    def __init__(self):
        self.opts = None

    def _init_data(self):
        self.pool = GraphPool(self.opts.pool, self.opts.prefix, self.opts.basedir)

    def _parse_args(self):
        parser = OptionParser(usage="%prog [options]", version="%prog " + VERSION)
        parser.add_option("-b", "--base-uri", dest="baseURI",\
                          metavar="URI", help="use URI as base URI for all resources\
                          (e.g. 'http://rdf.debian.net')")
        parser.add_option("-u", "--popcon-uri", dest="popconURI",\
                          default="http://popcon.debian.org/by_inst",\
                          metavar="URI", help="use URI as popcon stats database [default: %default]")
        parser.add_option("-o", "--output-prefix", dest="prefix",\
                          default="Popcon",\
                          metavar="PREFIX", help="dump output to PREFIX-{index}.rdf [default: %default]")
        parser.add_option("-d", "--base-dir", dest="basedir",\
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

        if self.opts.verbose and self.opts.quiet:
            raise Exception("Verbose (-v) and Quiet (-q) are mutually exclusive")
        elif self.opts.baseURI is None:
            raise Exception("Required base URI is missing, did you forget -b?")
        elif self.opts.popconURI is None:
            raise Exception("Required popcon database URI is missing, did you forget -u?")

    def _config_logger(self):
        if self.opts.verbose:
            lvl = logging.DEBUG
        elif self.opts.quiet:
            lvl = logging.ERROR
        else:
            lvl = logging.INFO

        logging.basicConfig(level=lvl, format='%(message)s')

    def run(self):
        try:
            self._parse_args()
        except Exception, e:
            print >> sys.stderr, str(e)
            sys.exit(2)

        self._config_logger()
        self._init_data()
        self._process_popcon()

        if self.pool.count_triples() > 0:
            self.pool.serialize()
            logging.info("%s triples generated" % self.pool.count_triples())
        else:
            logging.error("No triples generated, something went wrong :(")

    def _process_popcon(self):
        raw = urllib.urlopen(self.opts.popconURI)
        counter = 0

        for line in raw:
            if re.match(r"#.*", line) is None:
                if re.match(r"---.*", line) is not None:
                    return
                else:
                    counter += 1
                    data = re.split("\s+", line)
                    self._register_record(*tuple(data[1:7]))
                    if counter % 500 == 0: logging.info("%s packages processed" % counter)

    def _register_record(self, binpkg, inst, vote, old, recent, nofiles):
        logging.debug("Processing package '%s'" % binpkg)

        srcref = URIRef("%s/binary/%s" % (self.opts.baseURI, binpkg))
        
        self.pool.add_triple((srcref, DEB.popconInstalled, Literal(int(inst))))
        self.pool.add_triple((srcref, DEB.popconUsedRegularly, Literal(int(vote))))
        self.pool.add_triple((srcref, DEB.popconInstalledButNotInUse, Literal(int(old))))
        self.pool.add_triple((srcref, DEB.popconUpgradedRecently, Literal(int(recent))))
        self.pool.add_triple((srcref, DEB.popconNoFiles, Literal(int(nofiles))))
        

if __name__ == "__main__":
  PopconEnricher().run()
