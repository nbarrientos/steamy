# -*- coding: utf8 -*-

import unittest
import mox

from rdflib import Namespace, URIRef, Literal, Variable

from debian.sparql.miniast import Triple
from debian.services import SPARQLQueryBuilder
from debian.sparql.helpers import SelectQueryHelper

RDFS = Namespace(u"http://www.w3.org/2000/01/rdf-schema#")
DEB = Namespace(u"http://idi.fundacionctic.org/steamy/debian.owl#")
FOAF = Namespace(u"http://xmlns.com/foaf/0.1/")

class SPARQLQueryBuilderTest(unittest.TestCase):
    def setUp(self):
        self.builder = SPARQLQueryBuilder({})
        self.mox = mox.Mox()

    def test__consume_searchtype_source(self):
        self.builder.params['searchtype'] = "SOURCE"
        self.builder._consume_searchtype()
        self.assertTrue(self.builder.source_search)
        self.assertFalse(self.builder.binary_search)

    def test__consume_searchtype_binary(self):
        self.builder.params['searchtype'] = "BINARY"
        self.builder._consume_searchtype()
        self.assertFalse(self.builder.source_search)
        self.assertTrue(self.builder.binary_search)

    def test__consume_searchtype_binary_description(self):
        self.builder.params['searchtype'] = "BINARYEXT"
        self.builder._consume_searchtype()
        self.assertFalse(self.builder.source_search)
        self.assertTrue(self.builder.binary_search)

    def test__consume_homepage_true(self):
        self.builder.params['homepage'] = True
        mock = self.mox.CreateMock(SelectQueryHelper)
        mock.add_variable(Variable("homepage"))
        triple = Triple(\
            Variable("source"), FOAF.page, Variable("homepage"))
        mock.add_optional(triple)
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_homepage()
        self.mox.VerifyAll()
    
    def test__consume_homepage_true_false(self):
        self.builder.params['homepage'] = False
        mock = self.mox.CreateMock(SelectQueryHelper)
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_homepage()
        self.mox.VerifyAll()

    def test__consume_filter_empty(self):
        self.builder.params['filter'] = ""
        mock = self.mox.CreateMock(SelectQueryHelper)
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_filter()
        self.mox.VerifyAll()

    def test__consume_filter_source_not_exact(self):
        self.builder.source_search = True
        self.builder.params['filter'] = "keyword"
        self.builder.params['exactmatch'] = False
        mock = self.mox.CreateMock(SelectQueryHelper)
        mock.add_or_filter_regex({Variable("sourcename"): "keyword"})
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_filter()
        self.mox.VerifyAll()

    def test__consume_filter_source_exact(self):
        self.builder.source_search = True
        self.builder.params['filter'] = "keyword"
        self.builder.params['exactmatch'] = True
        mock = self.mox.CreateMock(SelectQueryHelper)
        mock.add_or_filter_regex({Variable("sourcename"): "^keyword$"})
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_filter()

    def test__consume_filter_source_escapes(self):
        self.builder.source_search = True
        self.builder.params['filter'] = "-+."
        self.builder.params['exactmatch'] = False
        mock = self.mox.CreateMock(SelectQueryHelper)
        mock.add_or_filter_regex({Variable("sourcename"): "\\\\-\\\\+\\\\."})
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_filter()

    def test__consume_filter_binary_not_exact(self):
        self.builder.binary_search = True
        self.builder.params['searchtype'] = "BINARY"
        self.builder.params['filter'] = "keyword"
        self.builder.params['exactmatch'] = False
        mock = self.mox.CreateMock(SelectQueryHelper)
        mock.add_or_filter_regex({Variable("binaryname"): "keyword"})
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_filter()
        self.mox.VerifyAll()

    def test__consume_filter_binary_exact(self):
        self.builder.binary_search = True
        self.builder.params['searchtype'] = "BINARY"
        self.builder.params['filter'] = "keyword"
        self.builder.params['exactmatch'] = True
        mock = self.mox.CreateMock(SelectQueryHelper)
        mock.add_or_filter_regex({Variable("binaryname"): "^keyword$"})
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_filter()
        self.mox.VerifyAll()

    def test__consume_filter_binary_desc_not_exact(self):
        self.builder.binary_search = True
        self.builder.params['searchtype'] = "BINARYEXT"
        self.builder.params['filter'] = "keyword"
        self.builder.params['exactmatch'] = False
        mock = self.mox.CreateMock(SelectQueryHelper)
        mock.push_triple(Variable("binary"), DEB.extendedDescription,\
            Variable("desc"))
        mock.add_or_filter_regex({Variable("binaryname"): "keyword",\
            Variable("desc"): "keyword"})
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_filter()
        self.mox.VerifyAll()

    def test__consume_filter_binary_desc_exact(self):
        self.builder.binary_search = True
        self.builder.params['searchtype'] = "BINARYEXT"
        self.builder.params['filter'] = "keyword"
        self.builder.params['exactmatch'] = True
        mock = self.mox.CreateMock(SelectQueryHelper)
        mock.push_triple(Variable("binary"), DEB.extendedDescription,\
            Variable("desc"))
        mock.add_or_filter_regex({Variable("binaryname"): "^keyword$",\
            Variable("desc"): "^keyword$"})
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_filter()
        self.mox.VerifyAll()

    def test__consume_distribution_any(self):
        self.builder.params['distribution'] = "ANY"
        mock = self.mox.CreateMock(SelectQueryHelper)
        mock.push_triple_variables(Variable("source"), DEB.distribution,\
            Variable("distribution"))
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_distribution()
        self.mox.VerifyAll()

    def test__consume_distribution_selected(self):
        self.builder.params['distribution'] = \
            "http://rdf.debian.net/distributions/distribution"
        mock = self.mox.CreateMock(SelectQueryHelper)
        mock.push_triple(Variable("source"), DEB.distribution,\
            URIRef(self.builder.params['distribution']))
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_distribution()
        self.mox.VerifyAll()
