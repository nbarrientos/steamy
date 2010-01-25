# -*- coding: utf8 -*-

import unittest

from mox import Mox

from homepages.io import _alternatives
from homepages.io import TripleProcessor


class AlternativesTest(unittest.TestCase):
    def setUp(self):
        self.mox = Mox()

    def test_no_matches(self):
        processor = self.mox.CreateMock(TripleProcessor)
        source = "http://rdf.debian.net/source/src/1.0"
        uri = "http://example.org"
        expected = ["http://example.org"]
        self.mox.ReplayAll()
        self.assertEqual(expected, _alternatives(source, uri, processor))
        self.mox.VerifyAll()

    def test_match_sourceforge(self):
        processor = self.mox.CreateMock(TripleProcessor)
        source = "http://rdf.debian.net/source/src/1.0"
        uri = "http://src.sourceforge.net"
        processor.push_homepage(source, "http://sourceforge.net/projects/src")
        expected = ["http://src.sourceforge.net", "http://sourceforge.net/projects/src"]
        self.mox.ReplayAll()
        self.assertEqual(expected, _alternatives(source, uri, processor))
        self.mox.VerifyAll()

    def test_match_sourceforge_sf(self):
        processor = self.mox.CreateMock(TripleProcessor)
        source = "http://rdf.debian.net/source/src/1.0"
        uri = "http://src.sf.net"
        processor.push_homepage(source, "http://sourceforge.net/projects/src")
        expected = ["http://src.sf.net", "http://sourceforge.net/projects/src"]
        self.mox.ReplayAll()
        self.assertEqual(expected, _alternatives(source, uri, processor))
        self.mox.VerifyAll()

    def test_match_sourceforge_alioth(self):
        processor = self.mox.CreateMock(TripleProcessor)
        source = "http://rdf.debian.net/source/src/1.0"
        uri = "http://src.alioth.debian.org"
        processor.push_homepage(source, "http://alioth.debian.org/projects/src")
        expected = ["http://src.alioth.debian.org", "http://alioth.debian.org/projects/src"]
        self.mox.ReplayAll()
        self.assertEqual(expected, _alternatives(source, uri, processor))
        self.mox.VerifyAll()
