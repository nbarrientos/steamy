# -*- coding: utf8 -*-

import unittest
import re

from mox import Mox, IgnoreArg, Regex

from rdflib import Namespace, URIRef, Literal, Variable

from debian.sparql.miniast import Triple
from debian.services import SPARQLQueryBuilder, FeedFinder
from debian.services import SPARQLQueryProcessor, RSSFeed
from debian.errors import UnexpectedFieldValueError
from debian.sparql.helpers import SelectQueryHelper

RDFS = Namespace(u"http://www.w3.org/2000/01/rdf-schema#")
DEB = Namespace(u"http://idi.fundacionctic.org/steamy/debian.owl#")
FOAF = Namespace(u"http://xmlns.com/foaf/0.1/")
RDF = Namespace(u"http://www.w3.org/1999/02/22-rdf-syntax-ns#")
DOAP = Namespace(u"http://usefulinc.com/ns/doap#")

class SPARQLQueryBuilderTest(unittest.TestCase):
    def setUp(self):
        self.builder = SPARQLQueryBuilder({})
        self.mox = Mox()

    # No optional calls in PyMox :(
    def mock_binary_search(self):
        self.builder._binary_search = lambda : True
        self.builder._extended_binary_search = lambda : False
        self.builder._source_search = lambda : False

    def mock_source_search(self):
        self.builder._binary_search = lambda : False
        self.builder._extended_binary_search = lambda : False
        self.builder._source_search = lambda : True

    def mock_extended_binary_search(self):
        self.builder._binary_search = lambda : True
        self.builder._extended_binary_search = lambda : True
        self.builder._source_search = lambda : False

    def test__searchtype_source(self):
        self.builder.params['searchtype'] = "SOURCE"
        self.assertTrue(self.builder._source_search())
        self.assertFalse(self.builder._binary_search())

    def test__searchtype_binary(self):
        self.builder.params['searchtype'] = "BINARY"
        self.assertTrue(self.builder._binary_search())
        self.assertFalse(self.builder._source_search())

    def test__searchtype_binary_description(self):
        self.builder.params['searchtype'] = "BINARYEXT"
        self.assertTrue(self.builder._binary_search())
        self.assertFalse(self.builder._source_search())

    def test__searchtype_unexpected(self):
        self.builder.params['searchtype'] = "FAIL"
        self.assertRaises(UnexpectedFieldValueError, \
            self.builder._binary_search)
        self.assertRaises(UnexpectedFieldValueError, \
            self.builder._source_search)

        self.builder.params.pop('searchtype')
        self.assertRaises(UnexpectedFieldValueError, \
            self.builder._binary_search)
        self.assertRaises(UnexpectedFieldValueError, \
            self.builder._source_search)

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
    
    def test__consume_homepage_false(self):
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
        self.mock_source_search()
        self.builder.params['filter'] = "keyword"
        self.builder.params['exactmatch'] = False
        mock = self.mox.CreateMock(SelectQueryHelper)
        mock.add_or_filter_regex({Variable("sourcename"): "keyword"})
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_filter()
        self.mox.VerifyAll()

    def test__consume_filter_source_exact(self):
        self.mock_source_search()
        self.builder.params['filter'] = "keyword"
        self.builder.params['exactmatch'] = True
        mock = self.mox.CreateMock(SelectQueryHelper)
        mock.add_or_filter_regex({Variable("sourcename"): "^keyword$"})
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_filter()

    def test__consume_filter_source_escapes(self):
        self.mock_source_search()
        self.builder.params['filter'] = "-+."
        self.builder.params['exactmatch'] = False
        mock = self.mox.CreateMock(SelectQueryHelper)
        mock.add_or_filter_regex({Variable("sourcename"): "\\\\-\\\\+\\\\."})
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_filter()

    def test__consume_filter_binary_not_exact(self):
        self.mock_binary_search()
        self.builder.params['filter'] = "keyword"
        self.builder.params['exactmatch'] = False
        mock = self.mox.CreateMock(SelectQueryHelper)
        mock.add_or_filter_regex({Variable("binaryname"): "keyword"})
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_filter()
        self.mox.VerifyAll()

    def test__consume_filter_binary_exact(self):
        self.mock_binary_search()
        self.builder.params['filter'] = "keyword"
        self.builder.params['exactmatch'] = True
        mock = self.mox.CreateMock(SelectQueryHelper)
        mock.add_or_filter_regex({Variable("binaryname"): "^keyword$"})
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_filter()
        self.mox.VerifyAll()

    def test__consume_filter_binary_desc_not_exact(self):
        self.mock_extended_binary_search()
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
        self.mock_extended_binary_search()
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

    def test__consume_priority_source_any(self):
        self.mock_source_search()
        self.builder.params['priority'] = "ANY"
        mock = self.mox.CreateMock(SelectQueryHelper)
        mock.add_variable("priority")
        triple = Triple(Variable("source"), DEB.priority, Variable("priority"))
        mock.add_optional(triple)
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_priority()
        self.mox.VerifyAll()

    def test__consume_priority_binary_any(self):
        self.mock_binary_search()
        self.builder.params['priority'] = "ANY"
        mock = self.mox.CreateMock(SelectQueryHelper)
        mock.add_variable("priority")
        triple = Triple(Variable("binary"), DEB.priority, Variable("priority"))
        mock.add_optional(triple)
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_priority()
        self.mox.VerifyAll()

    def test__consume_priority_source_selected(self):
        self.mock_source_search()
        self.builder.params['priority'] = "http://example.org/p"
        mock = self.mox.CreateMock(SelectQueryHelper)
        mock.push_triple(Variable("source"), DEB.priority, URIRef("http://example.org/p"))
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_priority()
        self.mox.VerifyAll()

    def test__consume_priority_binary_selected(self):
        self.mock_binary_search()
        self.builder.params['priority'] = "http://example.org/p"
        mock = self.mox.CreateMock(SelectQueryHelper)
        mock.push_triple(Variable("binary"), DEB.priority, URIRef("http://example.org/p"))
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_priority()
        self.mox.VerifyAll()

    def test__consume_vcs_empty(self):
        self.builder.params['vcs'] = []
        mock = self.mox.CreateMock(SelectQueryHelper)
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_vcs()
        self.mox.VerifyAll()

    def test__consume_vcs_one(self):
        self.builder.params['vcs'] = ["SVN"]
        mock = self.mox.CreateMock(SelectQueryHelper)
        mock.push_triple(Variable("source"), DEB.repository, Variable("repobnode"))
        triple = Triple(Variable("repobnode"), RDF.type, DOAP.SVNRepository) 
        mock.add_triple(triple)
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_vcs()
        self.mox.VerifyAll()

    def test__consume_vcs_several(self):
        self.builder.params['vcs'] = ["SVN", "GIT"]
        mock = self.mox.CreateMock(SelectQueryHelper)
        mock.push_triple(Variable("source"), DEB.repository, Variable("repobnode"))
        triple1 = Triple(Variable("repobnode"), RDF.type, DOAP.SVNRepository) 
        triple2 = Triple(Variable("repobnode"), RDF.type, DOAP.GitRepository) 
        mock.add_union([triple1], [triple2])
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_vcs()
        self.mox.VerifyAll()

    def test__consume_area_any(self):
        self.builder.params['area'] = "ANY"
        mock = self.mox.CreateMock(SelectQueryHelper)
        mock.push_triple_variables(Variable("source"), DEB.area,\
            Variable("area"))
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_area()
        self.mox.VerifyAll()

    def test__consume_area_selected(self):
        self.builder.params['area'] = "http://example.org/c"
        mock = self.mox.CreateMock(SelectQueryHelper)
        mock.push_triple(Variable("source"), DEB.area,\
            URIRef(self.builder.params['area']))
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_area()
        self.mox.VerifyAll()

    def test__consume_sort(self):
        self.builder.params['sort'] = "MAINTMAIL"
        self.mock_source_search()
        mock = self.mox.CreateMock(SelectQueryHelper)
        mock.set_orderby("maintmail")
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_sort()
        self.mox.VerifyAll()

        self.mock_binary_search()
        mock = self.mox.CreateMock(SelectQueryHelper)
        mock.set_orderby("maintmail")
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_sort()
        self.mox.VerifyAll()

    def test__consume_sort_error(self):
        self.builder.params['sort'] = "FAIL"
        self.assertRaises(UnexpectedFieldValueError, self.builder._consume_sort)

    def test__consume_sort_package_source(self):
        self.mock_source_search()
        self.builder.params['sort'] = "PACKAGE"
        mock = self.mox.CreateMock(SelectQueryHelper)
        mock.set_orderby("sourcename")
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_sort()
        self.mox.VerifyAll()

    def test__consume_sort_package_binary(self):
        self.mock_binary_search()
        self.builder.params['sort'] = "PACKAGE"
        mock = self.mox.CreateMock(SelectQueryHelper)
        mock.set_orderby("binaryname")
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_sort()
        self.mox.VerifyAll()

    def test__consume_maintainer_error(self):
        self.builder.params['maintainer'] = "FAIL"
        self.assertRaises(UnexpectedFieldValueError, self.builder._consume_maintainer)

    def test__consume_maintainer_all(self):
        self.builder.params['maintainer'] = "ALL"
        mock = self.mox.CreateMock(SelectQueryHelper)
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_maintainer()
        self.mox.VerifyAll()

    # TODO: Test QA, DEBIAN, TEAM

    def test__consume_comaintainer_error(self):
        self.builder.params['comaintainer'] = "FAIL"
        self.assertRaises(UnexpectedFieldValueError, self.builder._consume_comaintainer)

    def test__consume_comaintainer_all(self):
        self.builder.params['comaintainer'] = "ALL"
        mock = self.mox.CreateMock(SelectQueryHelper)
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_comaintainer()
        self.mox.VerifyAll()

    def test__consume_essential_source(self):
        self.builder.params['essential'] = True
        self.mock_source_search()
        mock = self.mox.CreateMock(SelectQueryHelper)
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_essential()
        self.mox.VerifyAll()

    def test__consume_essential_binary_disabled(self):
        self.builder.params['essential'] = False
        self.mock_binary_search()
        mock = self.mox.CreateMock(SelectQueryHelper)
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_essential()
        self.mox.VerifyAll()

    def test__consume_essential_binary_enabled(self):
        self.builder.params['essential'] = True
        self.mock_binary_search()
        mock = self.mox.CreateMock(SelectQueryHelper)
        mock.push_triple(Variable("binary"), RDF.type, DEB.EssentialBinary)
        self.builder.helper = mock 
        self.mox.ReplayAll()
        self.builder._consume_essential()
        self.mox.VerifyAll()


class FeedFinderTest(unittest.TestCase):
    def setUp(self):
        self.finder = FeedFinder()
        self.mox = Mox()

    def test__fetch_feeduris(self):
        unversionedsourceuri = "http://example.org/p"
        mock = self.mox.CreateMock(SPARQLQueryProcessor)
        expectedarg = r"SELECT.+\<%s\>.+" % re.escape(unversionedsourceuri)
        mock.execute_sanitized_query(Regex(expectedarg, flags=re.DOTALL))
        binding1 = {'feeduri': {'value': "feed1"}}
        binding2 = {'feeduri': {'value': "feed2"}}
        bindings = [binding1, binding2]
        fakeresults = {'results': {'bindings': bindings}}
        self.finder.processor = mock
        self.mox.ReplayAll()
        self.finder.processor.results = fakeresults
        feeds = self.finder._fetch_feeduris(unversionedsourceuri)
        self.mox.VerifyAll()
        self.assertEqual(2, len(feeds))
        self.assertEqual("feed1", feeds[0].feeduri)
        self.assertEqual("feed2", feeds[1].feeduri)

    # This cannot never happen, homepages without alternatives
    # won't match SPARQL patterns and won't be in the result set
    def test__fetch_feeduris_no_feeduris_in_bindings(self):
        unversionedsourceuri = "http://example.org/p"
        mock = self.mox.CreateMock(SPARQLQueryProcessor)
        expectedarg = r"SELECT.+\<%s\>.+" % re.escape(unversionedsourceuri)
        mock.execute_sanitized_query(Regex(expectedarg, flags=re.DOTALL))
        binding1 = {}
        binding2 = {}
        bindings = [binding1, binding2]
        fakeresults = {'results': {'bindings': bindings}}
        self.finder.processor = mock
        self.mox.ReplayAll()
        self.finder.processor.results = fakeresults
        feeds = self.finder._fetch_feeduris(unversionedsourceuri)
        self.mox.VerifyAll()
        self.assertEqual(0, len(feeds))

    def test__fetch_feeduris_no_bindings(self):
        unversionedsourceuri = "http://example.org/p"
        mock = self.mox.CreateMock(SPARQLQueryProcessor)
        expectedarg = r"SELECT.+\<%s\>.+" % re.escape(unversionedsourceuri)
        mock.execute_sanitized_query(Regex(expectedarg, flags=re.DOTALL))
        bindings = []
        fakeresults = {'results': {'bindings': bindings}}
        self.finder.processor = mock
        self.mox.ReplayAll()
        self.finder.processor.results = fakeresults
        feeds = self.finder._fetch_feeduris(unversionedsourceuri)
        self.mox.VerifyAll()
        self.assertEqual(0, len(feeds))

    def test__fetch_feeditems(self):
        feeduri = "http://example.org/p"
        mock = self.mox.CreateMock(SPARQLQueryProcessor)
        expectedarg = r"SELECT.+\<%s\>.+" % re.escape(feeduri)
        mock.execute_sanitized_query(Regex(expectedarg, flags=re.DOTALL))
        binding1 = {'title': {'value': "title1"}, 'link': {'value': "link1"}}
        binding2 = {'title': {'value': "title2"}}
        bindings = [binding1, binding2]
        fakeresults = {'results': {'bindings': bindings}}
        self.finder.processor = mock
        self.mox.ReplayAll()
        self.finder.processor.results = fakeresults
        items = self.finder._fetch_feeditems(feeduri)
        self.mox.VerifyAll()
        self.assertEqual(2, len(items))
        self.assertEqual("title1", items[0]['title'])
        self.assertEqual("link1", items[0]['link'])
        self.assertEqual("title2", items[1]['title'])
        self.assertEqual(None, items[1]['link'])

    def test__fetch_feeditems_no_bindings(self):
        feeduri = "http://example.org/p"
        mock = self.mox.CreateMock(SPARQLQueryProcessor)
        expectedarg = r"SELECT.+\<%s\>.+" % re.escape(feeduri)
        mock.execute_sanitized_query(Regex(expectedarg, flags=re.DOTALL))
        bindings = []
        fakeresults = {'results': {'bindings': bindings}}
        self.finder.processor = mock
        self.mox.ReplayAll()
        self.finder.processor.results = fakeresults
        items = self.finder._fetch_feeditems(feeduri)
        self.mox.VerifyAll()
        self.assertEqual(0, len(items))

    def test__fill_feeds(self):
        input = [RSSFeed("uri1"), RSSFeed("uri2")]
        self.mox.StubOutWithMock(self.finder, "_fetch_feeditems")
        self.mox.StubOutWithMock(self.finder, "_fetch_feed_channel_information")
        uri1items = []
        uri2items = [{'title': "title21"}, {'title': "title22"}]
        uri1channel = {'title': "title1"}
        uri2channel = {'title': "title2"}
        self.finder._fetch_feed_channel_information("uri1").AndReturn(uri1channel)
        self.finder._fetch_feeditems("uri1").AndReturn(uri1items)
        self.finder._fetch_feed_channel_information("uri2").AndReturn(uri2channel)
        self.finder._fetch_feeditems("uri2").AndReturn(uri2items)
        self.mox.ReplayAll()
        feeds = self.finder._fill_feeds(input)
        self.assertEqual("uri1", feeds[0].feeduri)
        self.assertEqual("uri2", feeds[1].feeduri)
        self.assertEqual([], feeds[0].items)
        self.assertEqual(2, len(feeds[1].items))
        self.assertEqual("title21", feeds[1].items[0]['title'])
        self.assertEqual("title22", feeds[1].items[1]['title'])
        self.assertEqual("title1", feeds[0].channel['title'])
        self.assertEqual("title2", feeds[1].channel['title'])

    def test__fetch_feed_channel_information(self):
        feeduri = "http://example.org/p"
        mock = self.mox.CreateMock(SPARQLQueryProcessor)
        expectedarg = r"SELECT.+\<%s\>.+" % re.escape(feeduri)
        mock.execute_sanitized_query(Regex(expectedarg, flags=re.DOTALL))
        binding1 = {'title': {'value': "title1"}}
        bindings = [binding1]
        fakeresults = {'results': {'bindings': bindings}}
        self.finder.processor = mock
        self.mox.ReplayAll()
        self.finder.processor.results = fakeresults
        channel = self.finder._fetch_feed_channel_information(feeduri)
        self.mox.VerifyAll()
        self.assertEqual("title1", channel['title'])

    def test__fetch_feed_channel_information_channel_but_no_title(self):
        feeduri = "http://example.org/p"
        mock = self.mox.CreateMock(SPARQLQueryProcessor)
        expectedarg = r"SELECT.+\<%s\>.+" % re.escape(feeduri)
        mock.execute_sanitized_query(Regex(expectedarg, flags=re.DOTALL))
        binding1 = {}
        bindings = [binding1]
        fakeresults = {'results': {'bindings': bindings}}
        self.finder.processor = mock
        self.mox.ReplayAll()
        self.finder.processor.results = fakeresults
        channel = self.finder._fetch_feed_channel_information(feeduri)
        self.mox.VerifyAll()
        self.assertEqual(None, channel['title'])

    def test__fetch_feed_channel_information_no_channel(self):
        feeduri = "http://example.org/p"
        mock = self.mox.CreateMock(SPARQLQueryProcessor)
        expectedarg = r"SELECT.+\<%s\>.+" % re.escape(feeduri)
        mock.execute_sanitized_query(Regex(expectedarg, flags=re.DOTALL))
        bindings = []
        fakeresults = {'results': {'bindings': bindings}}
        self.finder.processor = mock
        self.mox.ReplayAll()
        self.finder.processor.results = fakeresults
        channel = self.finder._fetch_feed_channel_information(feeduri)
        self.mox.VerifyAll()
        self.assertEqual(None, channel)
