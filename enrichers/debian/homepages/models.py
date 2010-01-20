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
    def is_rss(self):
        return "application/rss+xml" in self.types

class MetaLink(Link):
    def is_meta_rdf(self):
        return "application/rdf+xml" in self.types or \
            reduce(lambda x, y: x or y, [re.match(r".*\.rdf$", x) is not None for x in self.hrefs])

class Stats():
    def __init__(self):
        self.homepages = 0
        self.broken_homepages = 0
        self.w3cok = 0
        self.feeds = 0
        self.rdf = 0

    def count_homepage(self):
        self.homepages += 1

    def count_brokenhomepage(self):
        self.broken_homepages += 1

    def count_rdf(self):
        self.rdf += 1

    def count_feed(self):
        self.feeds += 1

    def count_validmarkup(self):
        self.w3cok += 1
    
    def __str__(self):
        return """\n\nStats:
\t* Total websites count: %s
\t* Non-respoding websites: %s
\t* Valid markups: %s
\t* RSS feeds processed: %s
\t* RDF files fetched: %s""" % \
        (self.homepages, self.broken_homepages, self.w3cok, self.feeds, self.rdf)
