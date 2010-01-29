# -*- coding: utf8 -*-

import unittest

from mox import Mox
  
from SPARQLWrapper import SPARQLWrapper2

from homepages import io
from homepages.io import _alternatives
from homepages.io import TripleProcessor


class AlternativesTest(unittest.TestCase):
    def setUp(self):
        self.mox = Mox()
        self.fakedsource = "http://rdf.debian.net/source/src/1.0"
        def fake_get_sources_linked_to_homepage(uri, endpoint, graph):
            return [self.fakedsource]
        self.gslth = io._get_sources_linked_to_homepage
        io._get_sources_linked_to_homepage = \
            fake_get_sources_linked_to_homepage

    def tearDown(self):
        io._get_sources_linked_to_homepage = self.gslth

    def test_no_matches(self):
        processor = self.mox.CreateMock(TripleProcessor)
        endpoint = self.mox.CreateMock(SPARQLWrapper2)
        uri = "http://example.org"
        expected = ["http://example.org"]
        self.mox.ReplayAll()
        self.assertEqual(expected, _alternatives(uri, processor, endpoint, "graph"))
        self.mox.VerifyAll()

    def test_match_sourceforge(self):
        processor = self.mox.CreateMock(TripleProcessor)
        endpoint = self.mox.CreateMock(SPARQLWrapper2)
        uri = "http://src.sourceforge.net"
        processor.push_homepage(self.fakedsource, "http://sourceforge.net/projects/src")
        expected = ["http://src.sourceforge.net", "http://sourceforge.net/projects/src"]
        self.mox.ReplayAll()
        self.assertEqual(expected, _alternatives(uri, processor, endpoint, "graph"))
        self.mox.VerifyAll()

    def test_match_sourceforge_sf(self):
        processor = self.mox.CreateMock(TripleProcessor)
        endpoint = self.mox.CreateMock(SPARQLWrapper2)
        uri = "http://src.sf.net"
        processor.push_homepage(self.fakedsource, "http://sourceforge.net/projects/src")
        expected = ["http://src.sf.net", "http://sourceforge.net/projects/src"]
        self.mox.ReplayAll()
        self.assertEqual(expected, _alternatives(uri, processor, endpoint, "graph"))
        self.mox.VerifyAll()

    def test_match_sourceforge_alioth(self):
        processor = self.mox.CreateMock(TripleProcessor)
        endpoint = self.mox.CreateMock(SPARQLWrapper2)
        uri = "http://src.alioth.debian.org"
        processor.push_homepage(self.fakedsource, "http://alioth.debian.org/projects/src")
        expected = ["http://src.alioth.debian.org", "http://alioth.debian.org/projects/src"]
        self.mox.ReplayAll()
        self.assertEqual(expected, _alternatives(uri, processor, endpoint, "graph"))
        self.mox.VerifyAll()
