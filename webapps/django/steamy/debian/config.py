# -*- coding: utf-8 -*-
#
# Nacho Barrientos Arias <nacho@debian.org>
#
# License: MIT

#SPARQL_ENDPOINT = "http://data.fundacionctic.org/sparql"
#FROM_GRAPH = "http://data.fundacionctic.org/idi/debian"

SPARQL_ENDPOINT = "http://wopr:8890/sparql"
FROM_GRAPH = "http://wopr/debian"

#SPARQL_ENDPOINT = "http://localhost:8180/openrdf-sesame/repositories/STEAMY"
#FROM_GRAPH = None

SPARQL_PREFIXES = """
PREFIX deb:<http://idi.fundacionctic.org/steamy/debian.owl#>
PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
PREFIX nfo:<http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#>
PREFIX tag:<http://www.holygoat.co.uk/owl/redwood/0.1/tags/>
PREFIX xhv:<http://www.w3.org/1999/xhtml/vocab#>
PREFIX doap:<http://usefulinc.com/ns/doap#>
PREFIX dc:<http://purl.org/dc/terms/>
PREFIX rss:<http://purl.org/rss/1.0/>
PREFIX foaf:<http://xmlns.com/foaf/0.1/>"""

#FROM <http://data.fundacionctic.org/idi/debian>
#FROM <http://wopr/debian>
#DEFAULT_QUERY = """
#SELECT ?binaryname ?fullversion ?sourcename ?maintainername ?distribution 
#FROM <http://wopr/debian>
#WHERE {
#    ?source a deb:Source ;
#            deb:packageName ?sourcename ;
#            deb:distribution ?distribution ;
#            deb:binary ?binary ;
#            deb:maintainer ?maintainer ;
#            deb:versionNumber ?version .
#    ?binary a deb:Binary ;
#            deb:packageName ?binaryname .
#    ?version a deb:VersionNumber ;
#            deb:fullVersion ?fullversion .
#    ?maintainer foaf:name ?maintainername .
#    FILTER regex(?binaryname, "^ab.*") .
#}"""

DEFAULT_QUERY = """
SELECT
WHERE {


}"""

ONT_URI = "http://idi.fundacionctic.org/steamy/debian.owl#"
RES_BASEURI = "http://rdf.debian.net"
PUBBY_BASEURI = "http://villablino.sytes.net:8180/pubby/resource"

RESULTS_PER_PAGE = 100
