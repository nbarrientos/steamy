import logging
import re

from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.sparqlexceptions import QueryBadFormed

from rdflib import Variable
from rdflib import Namespace, URIRef, Literal, Variable
from rdflib.sparql.bison import Parse as RdflibParse

from debian.config import *
from debian.sparql.helpers import SelectQueryHelper
from debian.sparql.miniast import Triple
from debian.errors import SPARQLQueryProcessorError

RDFS = Namespace(u"http://www.w3.org/2000/01/rdf-schema#")
FOAF = Namespace(u"http://xmlns.com/foaf/0.1/")
RDF = Namespace(u"http://www.w3.org/1999/02/22-rdf-syntax-ns#")
DEB = Namespace(u"http://idi.fundacionctic.org/steamy/debian.owl#")
NFO = Namespace(u"http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#")
TAG = Namespace(u"http://www.holygoat.co.uk/owl/redwood/0.1/tags/")
DOAP = Namespace(u"http://usefulinc.com/ns/doap#")

class Result():
    pass

class SPARQLQueryProcessor():
    def _init_endpoint(self):
        self.endpoint = SPARQLWrapper(SPARQL_ENDPOINT)
        self.endpoint.setReturnFormat(JSON)

    def _query_endpoint(self, query):
        self.endpoint.setQuery(query)
        return self.endpoint.query().convert()

    def format_source_results(self):
        resultlist = []
        for result in self.results['results']['bindings']:
            obj = Result()
            obj.sourcename = result['sourcename']['value']
            obj.sourceurilink = result['source']['value'].replace(RES_BASEURI, PUBBY_BASEURI)
            obj.usourceurilink = result['unversionedsource']['value'].replace(RES_BASEURI, PUBBY_BASEURI)
            obj.fullversion = result['fullversion']['value']
            obj.maintname = result['maintname']['value'] if 'maintname' in result else None
            obj.maintmail = result['maintmail']['value']
            obj.mainturilink = result['maint']['value'].replace(RES_BASEURI, PUBBY_BASEURI)
            obj.homepage = result['homepage']['value'] if 'homepage' in result else None
            obj.distribution = result['distribution']['value'] if 'distribution' in result else None
            obj.area = result['area']['value'] if 'area' in result else None
            obj.priority = result['priority']['value'] if 'priority' in result else None
            obj.sectionname = result['sectionname']['value']
            obj.sectionurilink = result['section']['value'].replace(RES_BASEURI, PUBBY_BASEURI)
            resultlist.append(obj)

        return resultlist

    def format_htmltable(self):
        html = "<table>"
        for var in self.results['head']['vars']:
            html = html + "<th>%s</th>" % var

        for result in self.results['results']['bindings']:
            html = html + "<tr>"
            for var in self.results['head']['vars']:
                html = html + "<td>%s</td>" % result[var]['value']
            html = html + "</tr>"

        html = html + "</table>"

        return html

    def _clean_query(self, query):
        return re.sub("LIMIT.*|OFFSET.*", "", query) + "LIMIT " + str(RESULTS_PER_PAGE)

    def execute_sanitized_query(self, query):
        self._init_endpoint()
        self.results = self._query_endpoint(query)

    def execute_query(self, query):
        query = self._clean_query(query)
        RdflibParse(query)
        self.execute_sanitized_query(query)

class SPARQLQueryBuilder():
    def __init__(self, params):
        self.params = params
        self.helper = SelectQueryHelper()
        self.binary_search = False
        self.source_search = False

    def create_query(self):
        self._consume_searchtype()
        self._add_base_elements()
        self._consume_distribution()
        self._consume_area()
        self._consume_sort()
        self._consume_homepage()
        self._consume_maintainer()
        self._consume_version()
        self._consume_priority()
        self._consume_section()
        self._consume_filter()
        self.helper.set_limit(RESULTS_PER_PAGE)
        return self.helper.__str__()

    def _add_base_elements(self):
        self.helper.push_triple_variables(\
            Variable("source"), RDF.type, DEB.Source)
        self.helper.push_triple_variables(\
            Variable("unversionedsource"), DEB.version, Variable("source"))
        self.helper.push_triple(\
            Variable("source"), DEB.maintainer, Variable("maint"))
        self.helper.add_variable("maintname")
        self.helper.add_optional(\
            Triple(Variable("maint"), FOAF.name, Variable("maintname")))
        self.helper.push_triple_variables(\
            Variable("maint"), FOAF.mbox, Variable("maintmail"))
        self.helper.push_triple_variables(\
            Variable("source"), DEB.versionNumber, Variable("version"))
        self.helper.push_triple_variables(\
            Variable("version"), DEB.fullVersion, Variable("fullversion"))
        self.helper.push_triple_variables(\
            Variable("source"), DEB.packageName, Variable("sourcename"))
        self.helper.push_triple(\
             Variable("source"), DEB.section, Variable("section"))
        self.helper.push_triple_variables(\
             Variable("section"), DEB.sectionName, Variable("sectionname"))
 
        if self.params['searchtype'] in ('BINARY', 'BINARYDESC'):
            self.helper.push_triple_variables(\
                Variable("binary"), RDF.type, DEB.Binary)
            self.helper.push_triple_variables(\
                Variable("source"), DEB.binary, Variable("binary"))
            self.helper.push_triple_variables(\
                Variable("binary"), DEB.packageName, Variable("binaryname"))

    def _consume_filter(self):
        filter = self.params['filter']
        if filter:
            if self.binary_search:
                if self.params['searchtype'] == 'BINARYEXT':
                    self.helper.push_triple(\
                        Variable("binary"), DEB.extendedDescription, Variable("desc"))
                    restrictions = {Variable("desc"): filter, Variable("binaryname"): filter}
                    self.helper.add_or_filter_regex(restrictions)
                else:   
                    self.helper.add_or_filter_regex({Variable("binaryname"): filter})
            elif self.source_search:
                self.helper.add_or_filter_regex({Variable("sourcename"): filter})

    def _consume_distribution(self):
        distribution = self.params['distribution']
        if distribution == 'ANY':
            self.helper.push_triple_variables(Variable("source"),
                DEB.distribution, Variable("distribution"))
        else:
            self.helper.push_triple(Variable("source"),
                DEB.distribution, URIRef(distribution))

    def _consume_area(self):
        area = self.params['area']
        if area == 'ANY':
            self.helper.push_triple_variables(Variable("source"),
                DEB.area, Variable("area"))
        else:
            self.helper.push_triple(Variable("source"),
                DEB.area, URIRef(area))

    def _consume_searchtype(self):
        type = self.params['searchtype']
        if type in ('BINARY', 'BINARYEXT'):
            self.binary_search = True 
        elif type in ('SOURCE'):
            self.source_search = True

    def _consume_sort(self):
        sort = self.params['sort']
        if sort == 'MAINTNAME':
            self.helper.set_orderby("maintname")
        elif sort == 'MAINTMAIL':
            self.helper.set_orderby("maintmail")
        else:
            if self.binary_search:
                self.helper.set_orderby("binaryname")
            else:
                self.helper.set_orderby("sourcename")

    def _consume_homepage(self):
       if self.params['homepage']:
           self.helper.add_variable("homepage")
           triple = Triple(\
                Variable("source"), FOAF.page, Variable("homepage"))
           self.helper.add_optional(triple)

    def _consume_maintainer(self):
        option = self.params['maintainer']
        if option == 'TEAM':
            self.helper.push_triple(Variable("maint"), RDF.type, FOAF.Group)
        elif option == 'DEBIAN':
            self.helper.add_or_filter_regex({Variable("maintmail"): "@debian.org$"}, False)
        elif option == 'QA':
            uriref = URIRef(RES_BASEURI + "/team/packages%40qa.debian.org")
            self.helper.push_triple(Variable("source"), DEB.maintainer, uriref) 

    def _consume_version(self):
        options = self.params['version']
        if 'NATIVE' in options or 'NMU' in options:
            triple = Triple(\
                Variable("version"), DEB.debianRevision, Variable("debianRevision"))
            self.helper.add_optional(triple)
        if 'NATIVE' in options:
            self.helper.add_filter_notbound(Variable("debianRevision"))
        if 'NMU' in options:
            self.helper.push_triple(\
                Variable("version"), DEB.upstreamVersion, Variable("upstreamVersion"))
            restrictions = {Variable("debianRevision"): ".*\\\..*",\
                            Variable("upstreamVersion"): ".*\\\+nmu.*"}
            self.helper.add_or_filter_regex(restrictions, False)
        if 'EPOCH' in options:
            self.helper.push_triple(Variable("version"), DEB.epoch, Variable("epoch"))

    def _consume_priority(self):
        option = self.params['priority']
        if option == 'ANY':
            self.helper.push_triple_variables(\
                Variable("source"), DEB.priority, Variable("priority"))
        else:
            self.helper.push_triple(\
                Variable("source"), DEB.priority, URIRef(option))

    def _consume_section(self):
        keyword = self.params['section']
        if keyword:
           self.helper.add_or_filter_regex({Variable("sectionname"): keyword})
