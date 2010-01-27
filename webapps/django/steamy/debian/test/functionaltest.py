# -*- coding: utf8 -*-

import unittest
from django.test.client import Client

from debian.errors import SPARQLQueryProcessorError
from debian.errors import SPARQLQueryProcessorEndpointNotFoundError
from debian.errors import SPARQLQueryProcessorQueryBadFormedError 
from debian.errors import SPARQLQueryProcessorUnacceptableQueryFormatError


class FunctionalTest(unittest.TestCase):
    def setUp(self):
        self.c = Client()

    def test_index(self):
        response = self.c.get("/debian/")
        self.failUnlessEqual(response.status_code, 200)
        template_names = [x.name for x in response.template]
        self.assertTrue('debian/search.html' in template_names)
        self.assertTrue('debian/base.html' in template_names)
        self.assertTrue('debian/search/assisted-search.html' in template_names)
        self.assertTrue('debian/search/sparql.html' in template_names)
        self.assertTrue('debian/search/help.html' in template_names)
        self.assertEqual("text/html; charset=utf-8", response['Content-Type'])

    def test_index_post(self):
        response = self.c.post("/debian/")
        self.failUnlessEqual(response.status_code, 405)

    def test_results_get(self):
        response = self.c.get("/debian/results/")
        self.failUnlessEqual(response.status_code, 405)

    def test_sparql_get(self):
        response = self.c.get("/debian/sparql/")
        self.failUnlessEqual(response.status_code, 405)

    def test_binaries_post(self):
        response = self.c.post("/debian/binaries/sourcename/version/")
        self.failUnlessEqual(response.status_code, 405)

    def test_news_post(self):
        response = self.c.post("/debian/news/sourcename/")
        self.failUnlessEqual(response.status_code, 405)

    def test_allnews_get(self):
        response = self.c.get("/debian/results/news/")
        self.failUnlessEqual(response.status_code, 405)

    def test_binaries_badsourcename(self):
        response = self.c.get("/debian/binaries/%7B/1.0/")
        self.failUnlessEqual(response.status_code, 200)
        template_names = [x.name for x in response.template]
        self.assertEqual(2, len(template_names))
        self.assertTrue('debian/base.html' in template_names)
        self.assertTrue('debian/error.html' in template_names)

    def test_news_badsourcename(self):
        response = self.c.get("/debian/news/%7B/")
        self.failUnlessEqual(response.status_code, 200)
        template_names = [x.name for x in response.template]
        self.assertEqual(2, len(template_names))
        self.assertTrue('debian/base.html' in template_names)
        self.assertTrue('debian/error.html' in template_names)

    def test_assisted_search_html_source(self):
        body = {'sort': 'PACKAGE', 'priority': 'ANY', 
                'maintainer': 'ALL', 'searchtype': 'SOURCE', 
                'area': 'ANY', 'section': '', 
                'filter': '', 'comaintainer': 'ALL', 
                'distribution': 'ANY'}
        response = self.c.post("/debian/results/", body)
        template_names = [x.name for x in response.template]
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual("text/html; charset=utf-8", response['Content-Type'])
        self.assertEqual(2, len(template_names))
        self.assertTrue('debian/base.html' in template_names)
        self.assertTrue('debian/source_results.html' in template_names)

    def test_assisted_search_html_binary(self):
        body = {'sort': 'PACKAGE', 'priority': 'ANY', 
                'maintainer': 'ALL', 'searchtype': 'BINARY', 
                'area': 'ANY', 'section': '', 
                'filter': '', 'comaintainer': 'ALL', 
                'distribution': 'ANY'}
        response = self.c.post("/debian/results/", body)
        template_names = [x.name for x in response.template]
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual("text/html; charset=utf-8", response['Content-Type'])
        self.assertEqual(2, len(template_names))
        self.assertTrue('debian/base.html' in template_names)
        self.assertTrue('debian/binary_results.html' in template_names)

    def test_assisted_search_json(self):
        body = {'sort': 'PACKAGE', 'priority': 'ANY', 
                'maintainer': 'ALL', 'searchtype': 'SOURCE', 
                'area': 'ANY', 'section': '', 
                'filter': '', 'comaintainer': 'ALL', 
                'distribution': 'ANY', 'tojson': 'on'}
        response = self.c.post("/debian/results/", body)
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual("application/json", response['Content-Type'])

    def test_malformed_sparql_query(self):
        query = "SELECT * WHERE { ?s ?p }"
        body = {'ns': '', 'query': query}
        response = self.c.post("/debian/sparql/", body)
        self.failUnlessEqual(response.status_code, 200)
        template_names = [x.name for x in response.template]
        self.assertEqual(2, len(template_names))
        self.assertTrue('debian/base.html' in template_names)
        self.assertTrue('debian/error.html' in template_names)
        e = SPARQLQueryProcessorQueryBadFormedError()
        self.assertEqual(e, response.context['reason'])

    def test_malformed_sparql_query_mistyped_type(self):
        query = "SLECT * WHERE { ?s ?p ?o . }"
        body = {'ns': '', 'query': query}
        response = self.c.post("/debian/sparql/", body)
        self.failUnlessEqual(response.status_code, 200)
        template_names = [x.name for x in response.template]
        self.assertEqual(2, len(template_names))
        self.assertTrue('debian/base.html' in template_names)
        self.assertTrue('debian/error.html' in template_names)
        e = SPARQLQueryProcessorQueryBadFormedError()
        self.assertEqual(e, response.context['reason'])

    def test_malformed_sparql_query_unsupported_type(self):
        query = "CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o . }"
        body = {'ns': '', 'query': query}
        response = self.c.post("/debian/sparql/", body)
        self.failUnlessEqual(response.status_code, 200)
        template_names = [x.name for x in response.template]
        self.assertEqual(2, len(template_names))
        self.assertTrue('debian/base.html' in template_names)
        self.assertTrue('debian/error.html' in template_names)
        e = SPARQLQueryProcessorUnacceptableQueryFormatError()
        self.assertEqual(e, response.context['reason'])

    def test_malformed_sparql_query_ok(self):
        query = "SELECT * WHERE { ?s ?p ?o . }"
        body = {'ns': '', 'query': query}
        response = self.c.post("/debian/sparql/", body)
        self.failUnlessEqual(response.status_code, 200)
        template_names = [x.name for x in response.template]
        self.assertEqual(2, len(template_names))
        self.assertTrue('debian/base.html' in template_names)
        self.assertTrue('debian/results.html' in template_names)

    # Will fail in non-virtuoso stores
    def test_malformed_sparql_query_ok2(self):
        ns = "PREFIX deb:<http://idi.fundacionctic.org/steamy/debian.owl#>"
        query = """
SELECT ?s COUNT(?d) as ?c
WHERE {

?s deb:distribution ?d

} 
ORDER BY DESC(?c)"""
        body = {'ns': ns, 'query': query}
        response = self.c.post("/debian/sparql/", body)
        self.failUnlessEqual(response.status_code, 200)
        template_names = [x.name for x in response.template]
        self.assertEqual(2, len(template_names))
        self.assertTrue('debian/base.html' in template_names)
        self.assertTrue('debian/results.html' in template_names)


    def test_result_based_news(self):
        body = {'sort': 'PACKAGE', 'priority': 'ANY',
                'maintainer': 'ALL', 'searchtype': 'BINARY',
                'area': 'ANY', 'section': '',
                'filter': '', 'comaintainer': 'ALL',
                'distribution': 'ANY'}
        response = self.c.post("/debian/results/news/", body)
        template_names = [x.name for x in response.template]
        self.failUnlessEqual(response.status_code, 200)
        self.assertEqual("text/html; charset=utf-8", response['Content-Type'])
        self.assertEqual(2, len(template_names))
        self.assertTrue('debian/base.html' in template_names)
        self.assertTrue('debian/news.html' in template_names)
