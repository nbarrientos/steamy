import logging

from SPARQLWrapper import SPARQLWrapper2
from SPARQLWrapper.sparqlexceptions import QueryBadFormed

from debian.config import SPARQL_ENDPOINT

class SPARQLQueryProcessorError(Exception):
    def __init__(self, reason):
        self.reason = reason

class SPARQLQueryProcessor():
    def _init_endpoint(self):
        self.endpoint = SPARQLWrapper2(SPARQL_ENDPOINT)

    def _query_endpoint(self, query):
        self.endpoint.setQuery(query)
        return self.endpoint.query().convert()

    def _result_as_text(self, result): # Delete me
        for var in result.variables:
            for binding in result.getValues(var):
                print binding.value

    def _result_as_html(self, result):
        pass
    
    def execute_query(self, query):
        self._init_endpoint()
        try:
            result = self._query_endpoint(query)
            self._result_as_text(result)  # Delete me
        except QueryBadFormed, e:
            raise SPARQLQueryProcessorError("Query malformed")
