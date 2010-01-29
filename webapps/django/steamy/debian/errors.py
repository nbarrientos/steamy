# -*- coding: utf-8 -*-
#
# Nacho Barrientos Arias <nacho@debian.org>
#
# License: MIT

class SPARQLQueryProcessorError(Exception):
    def __str__(self):
        return "Unexpected error processing the query, please report."

    def __eq__(self, other):
        return self.__class__ == other.__class__

class SPARQLQueryProcessorEndpointNotFoundError(SPARQLQueryProcessorError):
    def __str__(self):
        return "Endpoint not found. Try again later."

class SPARQLQueryProcessorQueryBadFormedError(SPARQLQueryProcessorError):
    def __str__(self):
        return "Query bad formed."

class SPARQLQueryProcessorUnacceptableQueryFormatError(SPARQLQueryProcessorError):
    def __str__(self):
        return "Unknown query type. Only SELECT queries are supported."

class UnexpectedSituationError(Exception):
    pass

class SPARQLQueryBuilderError(Exception):
    def __str__(self):
        return "Unexpected error building the query, please report."

    def __eq__(self, other):
        return self.__class__ == other.__class__

class SPARQLQueryBuilderUnexpectedFieldValueError(SPARQLQueryBuilderError):
    def __init__(self, field):
        self.field = field

    def __str__(self):
        return "Unexpected form value parsing '%s'" % self.field

class SPARQLQueryBuilderPackageNameSchemeError(SPARQLQueryBuilderError):
    def __str__(self):
        return "Unrecognized package naming scheme" 
