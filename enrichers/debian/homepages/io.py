#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Nacho Barrientos Arias <nacho@debian.org>
#
# License: MIT

import logging

from sgmllib import SGMLParser

from models import AlternateLink, MetaLink

# FIXME
def homepages():
    #l = ["http://www.wikier.org", "http://www.kde.org"]
    l = ["http://www.wikier.org"]

    for homepage in l:
        yield homepage

def w3c_validator(uri):
    return True  # FIXME

class LinkRetrieval(SGMLParser):
    def reset(self):
        SGMLParser.reset(self)
        self.results = []

    def start_link(self, attrs):
        rels = [value.lower() for key, value in attrs if key=='rel']
        types = [value.lower() for key, value in attrs if key=='type']
        hrefs = [value for key, value in attrs if key=='href']
        if 'alternate' in rels:
            self.results.append(AlternateLink(types, hrefs))
            logging.debug("Appended alternate: types=%s hrefs=%s" % \
                         (types, hrefs))
        if 'meta' in rels:
            self.results.append(MetaLink(types, hrefs))
            logging.debug("Appended meta: types=%s hrefs=%s" % \
                         (types, hrefs))

    def get_rss_hrefs(self):
        hrefs = []
        for x in self.results: 
            if x.is_rss():
                hrefs.extend(x.hrefs)
        return hrefs

    def get_rdf_meta_hrefs(self):
        hrefs = []
        for x in self.results:
            if x.is_meta_rdf():
                hrefs.extend(x.hrefs)
        return hrefs
