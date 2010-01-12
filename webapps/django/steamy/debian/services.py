import logging
import re

from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.sparqlexceptions import QueryBadFormed

from rdflib import Variable
from rdflib import Namespace, URIRef, Literal, Variable

from debian.config import *
from debian.sparql.helpers import SelectQueryHelper
from debian.sparql.miniast import Triple

RDFS = Namespace(u"http://www.w3.org/2000/01/rdf-schema#")
FOAF = Namespace(u"http://xmlns.com/foaf/0.1/")
RDF = Namespace(u"http://www.w3.org/1999/02/22-rdf-syntax-ns#")
DEB = Namespace(u"http://idi.fundacionctic.org/steamy/debian.owl#")
NFO = Namespace(u"http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#")
TAG = Namespace(u"http://www.holygoat.co.uk/owl/redwood/0.1/tags/")
DOAP = Namespace(u"http://usefulinc.com/ns/doap#")

class SPARQLQueryProcessorError(Exception):
    def __init__(self, reason):
        self.reason = reason

class SPARQLQueryProcessor():
    def _init_endpoint(self):
        self.endpoint = SPARQLWrapper(SPARQL_ENDPOINT)
        self.endpoint.setReturnFormat(JSON)

    def _query_endpoint(self, query):
        self.endpoint.setQuery(query)
        return self.endpoint.query().convert()

    def _result_as_html(self, results):
        html = "<table>"
        for var in results['head']['vars']:
            html = html + "<th>%s</th>" % var

        for result in results['results']['bindings']:
            html = html + "<tr>"
            for var in results['head']['vars']:
                html = html + "<td>%s</td>" % result[var]['value']
            html = html + "</tr>"

        html = html + "</table>"

        return html

    def _clean_query(self, query):
        return re.sub("LIMIT.*|OFFSET.*", "", query) + "LIMIT " + str(RESULTS_PER_PAGE)

    def execute_sanitized_query(self, query):
        self._init_endpoint()
        print query
        results = self._query_endpoint(query)
        return self._result_as_html(results)

    def execute_query(self, query):
        query = self._clean_query(query)
        # TODO: Try to parse query rdflib.Parse
        return self.execute_sanitized_query(query)

class SPARQLQueryBuilder():
    def __init__(self, params):
        self.params = params
        self.helper = SelectQueryHelper()
        self.binary_search = False
        self.source_search = False

    def create_query(self):
        self._add_base_elements()
        self._consume_searchtype()
        self._consume_distribution()
        self._consume_area()
        self._consume_filter()
        self.helper.set_limit(RESULTS_PER_PAGE)
        return self.helper.__str__()

    def _add_base_elements(self):
        triple = Triple(Variable("source"), RDF.type, DEB.Source)
        self.helper.add_triple_variables(triple)
        if self.params['searchtype'] in ('BINARY', 'BINARYDESC'):
            triple = Triple(Variable("binary"), RDF.type, DEB.Binary)
            self.helper.add_triple_variables(triple)
            triple = Triple(Variable("source"), DEB.binary, Variable("binary"))
            self.helper.add_triple_variables(triple)

    def _consume_filter(self):
        filter = self.params['filter']
        if self.binary_search:
            self.helper.push_triple(\
                Variable("binary"), DEB.packageName, Variable("binaryname"))
            if self.params['searchtype'] == 'BINARYEXT':
                self.helper.push_triple(\
                    Variable("binary"), DEB.extendedDescription, Variable("desc"))
                self.helper.add_or_filter_regex(Variable("desc"), Variable("binaryname"), filter)
            else:   
                self.add_filter_regex(Variable("binaryname"), filter)
        elif self.source_search:
            self.helper.push_triple(\
                Variable("source"), DEB.packageName, Variable("sourcename"))
            self.helper.add_filter_regex(Variable("sourcename"), filter)

    def _consume_distribution(self):
        distribution = self.params['distribution']
        if distribution == 'any':
            self.helper.push_triple_variables(Variable("source"),
                DEB.distribution, Variable("distribution"))
        else:
            self.helper.push_triple_variables(Variable("source"),
                DEB.distribution, URIRef(distribution))

    def _consume_area(self):
        area = self.params['area']
        if area == 'any':
            self.helper.push_triple_variables(Variable("source"),
                DEB.area, Variable("area"))
        else:
            self.helper.push_triple_variables(Variable("source"),
                DEB.area, URIRef(area))

    def _consume_searchtype(self):
        type = self.params['searchtype']
        if type in ('BINARY', 'BINARYEXT'):
            self.binary_search = True 
        elif type in ('SOURCE'):
            self.source_search = True
