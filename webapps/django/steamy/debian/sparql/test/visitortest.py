# -*- coding: utf8 -*-

import unittest

from rdflib import Namespace, URIRef, Literal, Variable
from rdflib.sparql.bison import Parse
from rdflib.sparql.bison.Query import Query

from sparql.miniast import *
from sparql.visitor import QueryStringVisitor
from sparql.helpers import SelectQueryHelper

RDFS = Namespace(u"http://www.w3.org/2000/01/rdf-schema#")
DEB = Namespace(u"http://idi.fundacionctic.org/steamy/debian.owl#")

class VisitorTest(unittest.TestCase):
    def setUp(self):
        self.triple1 = Triple()
        self.triple1.subject = Variable("var1")
        self.triple1.property = RDFS.type
        self.triple1.object = DEB.Source
        self.triple2 = Triple()
        self.triple2.subject = URIRef("http://rdf.d.n/r")
        self.triple2.property = RDFS.type
        self.triple2.object = DEB.Binary
        self.triple3 = Triple()
        self.triple3.subject = Variable("v1")
        self.triple3.property = Variable("v2")
        self.triple3.object = Variable("v3")
        self.v = QueryStringVisitor()

    def test_visit_Variable(self):
        expected = "?s"
        self.assertEqual(expected, self.v.visit(Variable("s")))

    def test_visit_URIRef(self):
        uriref = URIRef("http://rdf.debian.net/r")
        expected = "<http://rdf.debian.net/r>"
        self.assertEqual(expected, self.v.visit(uriref))

    def test_visit_Literal(self):
        literal = Literal("Literal")
        expected = '"Literal"'
        self.assertEqual(expected, self.v.visit(literal))

    def test_visit_Triple(self):
        expected = "?var1 <http://www.w3.org/2000/01/rdf-schema#type> \
<http://idi.fundacionctic.org/steamy/debian.owl#Source>."
        self.assertEqual(expected, self.v.visit(self.triple1))

        expected = "<http://rdf.d.n/r> <http://www.w3.org/2000/01/rdf-schema#type> \
<http://idi.fundacionctic.org/steamy/debian.owl#Binary>."
        self.assertEqual(expected, self.v.visit(self.triple2))

    def test_visit_Optional(self):
        optional = Optional([self.triple3])
        expected = "OPTIONAL{?v1 ?v2 ?v3.}"
        self.assertEqual(expected, self.v.visit(optional))

        optional = Optional([self.triple3, self.triple3])
        expected = "OPTIONAL{?v1 ?v2 ?v3.?v1 ?v2 ?v3.}"
        self.assertEqual(expected, self.v.visit(optional))

    def test_visit_Filter(self):
        f1 = FunCall("regex", ["arg1", "arg2"])
        f2 = FunCall("regex", ["arg3", "arg4"])
        binexp = BinaryExpression(f1, "||", f2)
        filter = Filter(binexp)
        expected = "FILTER(regex(arg1,arg2)||regex(arg3,arg4))"
        self.assertEqual(expected, self.v.visit(filter))

    def test_visit_Union(self):
        st1 = Triple(Variable("a"), Variable("b"), Variable("c"))
        st2 = Triple(Variable("d"), Variable("e"), Variable("f"))
        gp1 = [st1, st2]
        gp2 = [st1]
        union = Union()
        union.graphpatterns.append(gp1)
        union.graphpatterns.append(gp2)
        expected = "{?a ?b ?c.?d ?e ?f.}UNION{?a ?b ?c.}"
        self.assertEqual(expected, self.v.visit(union))
        gp3 = [st1]
        union.graphpatterns.append(gp3)
        expected = "{?a ?b ?c.?d ?e ?f.}UNION{?a ?b ?c.}UNION{?a ?b ?c.}"
        self.assertEqual(expected, self.v.visit(union))

    def test_visit_SelectQuery(self):
        st2 = Triple(Variable("d"), Variable("e"), Variable("f"))
        helper = SelectQueryHelper()
        helper.add_triple_variables(st2)
        helper.add_filter(FunCall("regex", [Variable("var"), '"regex"']))
        expected = "SELECT?e?f?d WHERE{?d ?e ?f.FILTER(regex(?var,\"regex\"))}"
        result = self.v.visit(helper.query)
        self.assertEqual(expected, result) 
        self.assertEqual(Query, Parse(result).__class__)

        helper.add_optional([st2, st2])
        result = self.v.visit(helper.query)
        self.assertEqual(Query, Parse(result).__class__)

        helper.add_union([st2, st2], [st2], [st2])
        result = self.v.visit(helper.query)
        self.assertEqual(Query, Parse(result).__class__)
