#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Nacho Barrientos Arias <nacho@debian.org>
#
# License: MIT

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
        return "application/rdf+xml" in self.types
