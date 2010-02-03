#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Nacho Barrientos Arias <nacho@debian.org>
#
# License: MIT

import re


class Link():
    def __init__(self, types, hrefs):
        self.types = types
        self.hrefs = hrefs

    def is_rss(self):
        return False

    def is_meta_rdf(self):
        return False

    def __str__(self):
        return "Types: %s Hrefs:%s" % (self.types, self.hrefs)

class AlternateLink(Link):
    # RSS auto-discovery: http://www.rssboard.org/rss-autodiscovery
    def is_rss(self):
        return "application/rss+xml" in self.types

class MetaLink(Link):
    # http://www.w3.org/TR/REC-rdf-syntax/ (Chapter 9)
    def is_meta_rdf(self):
        return "application/rdf+xml" in self.types or \
            reduce(lambda x, y: x or y, [re.match(r".*\.rdf$", x) is not None for x in self.hrefs])

class Stats():
    def __init__(self):
        self.homepages = 0
        self.broken_homepages = 0
        self.w3cok = 0
        self.feeds = 0
        self.invalidfeeds = 0
        self.rss1feeds = 0
        self.rss2feeds = 0
        self.atomfeeds = 0
        self.rdf = 0
        self.invalidrdf = 0

    def count_homepage(self):
        self.homepages += 1

    def count_brokenhomepage(self):
        self.broken_homepages += 1

    def count_rdf(self):
        self.rdf += 1

    def count_invalidrdf(self):
        self.invalidrdf += 1

    def count_feed(self):
        self.feeds += 1

    def count_rss1feed(self):
        self.rss1feeds += 1
    
    def count_rss2feed(self):
        self.rss2feeds += 1
    
    def count_atomfeed(self):
        self.atomfeeds += 1

    def count_invalidfeed(self):
        self.invalidfeeds += 1

    def count_validmarkup(self):
        self.w3cok += 1
    
    def __str__(self):
        return """\n\nStats:
\t* Total websites count: %(homepages)s (%(broken_homepages)s not responding)
\t* Valid markups: %(w3cok)s
\t* RSS feeds processed: %(feeds)s (%(invalidfeeds)s invalid)
\t\t RSS1: %(rss1feeds)s RSS2: %(rss2feeds)s Atom: %(atomfeeds)s
\t* RDF files fetched: %(rdf)s (%(invalidrdf)s invalid)""" % self.__dict__
