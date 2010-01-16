# -*- coding: utf8 -*-

import unittest

from rdflib import Namespace, URIRef, Literal, Variable

from debian.sparql.helpers import SelectQueryHelper
from debian.sparql.miniast import Triple, Optional, Filter
from debian.sparql.miniast import FunCall, BinaryExpression, UnaryExpression

RDFS = Namespace(u"http://www.w3.org/2000/01/rdf-schema#")
DEB = Namespace(u"http://idi.fundacionctic.org/steamy/debian.owl#")

class SelectQueryHelperTest(unittest.TestCase):
    def setUp(self):
        self.s = SelectQueryHelper()
        self.triple1 = Triple()
        self.triple1.subject = Variable("var1")
        self.triple1.property = RDFS.type
        self.triple1.object = DEB.Source
        self.triple2 = Triple()
        self.triple2.subject = Variable("var2")
        self.triple2.property = RDFS.type
        self.triple2.object = DEB.Binary
        self.triple3 = Triple()
        self.triple3.subject = Variable("var3")
        self.triple3.property = RDFS.type
        self.triple3.object = Variable("var4")

    def test_add_variable(self):
        self.s.add_variable("varname")
        self.s.add_variable("varname")
        self.assertEqual([Variable("varname")], self.s.query.variables)

    def test_add_triple(self):
        self.s.add_triple(self.triple1)
        self.s.add_triple(self.triple1)
        self.assertEqual(1, len(self.s.query.whereclause.stmts))
        self.assertEqual(self.triple1, self.s.query.whereclause.stmts[0])
        self.s.add_triple(self.triple2)
        self.assertEqual(2, len(self.s.query.whereclause.stmts))
        self.assertEqual(self.triple2, self.s.query.whereclause.stmts[1])

    def test_add_triple_variables(self):
        self.s.add_triple(self.triple3)
        self.assertEqual(1, len(self.s.query.whereclause.stmts))
        self.assertEqual(self.triple3, self.s.query.whereclause.stmts[0])
        varlist = [Variable("var3"), Variable("var4")]
        self.assertEqual(varlist.sort(), self.s.query.variables.sort())

    def test_push_triple(self):
        self.s.push_triple(\
            Variable("var1"), RDFS.type, DEB.Source)
        self.assertEqual(1, len(self.s.query.whereclause.stmts))
        self.assertEqual(self.triple1, self.s.query.whereclause.stmts[0])

    def test_push_triple_variables(self):
        self.s.push_triple_variables(\
            Variable("var3"), RDFS.type, Variable("var4"))
        self.assertEqual(1, len(self.s.query.whereclause.stmts))
        self.assertEqual(self.triple3, self.s.query.whereclause.stmts[0])
        varlist = [Variable("var3"), Variable("var4")]
        self.assertEqual(varlist.sort(), self.s.query.variables.sort())

    def test_add_optional(self):
        self.s.add_optional(self.triple1)
        opt1 = Optional(self.triple1)
        self.assertEqual(1, len(self.s.query.whereclause.stmts))
        self.assertEqual(opt1, self.s.query.whereclause.stmts[0])

        self.s.add_optional(self.triple1, self.triple2)
        opt2 = Optional(self.triple1, self.triple2)
        self.assertEqual(2, len(self.s.query.whereclause.stmts))
        self.assertEqual(opt2, self.s.query.whereclause.stmts[1])

    def test_add_filter(self):
        f1 = FunCall("regex", "arg1", "arg2")
        f2 = FunCall("regex", "arg3", "arg4")
        binexp = BinaryExpression(f1, "||", f2)
        self.s.add_filter(binexp)

    def test_add_union(self):
        st1 = Triple(Variable("a"), Variable("b"), Variable("c"))
        st2 = Triple(Variable("d"), Variable("e"), Variable("f"))
        gp1 = [st1, st2]
        gp2 = [st1]
        self.s.add_union(gp1, gp2)
        self.assertEqual(1, len(self.s.query.whereclause.stmts))
        self.assertEqual(2, len(self.s.query.whereclause.stmts[0].graphpatterns))
        self.assertEqual(2, len(self.s.query.whereclause.stmts[0].graphpatterns[0]))
        self.assertEqual(1, len(self.s.query.whereclause.stmts[0].graphpatterns[1]))
        self.assertRaises(Exception, self.s.add_union, gp1)

    def test_add_triple_variables(self):
        st1 = Triple(Variable("a"), Variable("b"), Variable("c"))
        self.s.add_triple_variables(st1)
        self.assertEqual(3, len(self.s.query.variables))

    def test_set_limit_and_offset(self):
        self.s.set_limit("2")
        self.s.set_offset("2")
        self.assertEqual(["2", "2"], [limit.value for limit in self.s.query.modifiers])

    def test_set_orderby(self):
        self.s.set_orderby("var")
        self.assertEqual(Variable("var"), self.s.query.orderby.variable)

    def test_set_from(self):
        uri = "http://some.where/graphs/graph"
        self.s.set_from(uri)
        self.assertEqual(URIRef(uri), self.s.query.fromgraph)

    def test_str(self):
        expected = "SELECT WHERE{}"
        self.assertEqual(expected, str(self.s))

    def test_add_or_filter_regex(self):
        self.s.add_or_filter_regex({"a": "a1", "b": "b1", "c": "c1"})
        self.assertEqual(1, len(self.s.query.whereclause.stmts))
        b2 = BinaryExpression(FunCall("regex", "c", '"c1"', '"i"'), "||",\
                              FunCall("regex", "a", '"a1"', '"i"'))
        b1 = BinaryExpression(FunCall("regex", "b", '"b1"', '"i"'), "||", b2)
        f1 = Filter(b1)
        self.assertEqual(f1, self.s.query.whereclause.stmts[0])

        self.s.add_or_filter_regex({"a": "a1"})
        fc1 = FunCall("regex", "a", '"a1"', "\"i\"")
        f2 = Filter(fc1)
        self.assertEqual(2, len(self.s.query.whereclause.stmts))
        self.assertEqual(f2, self.s.query.whereclause.stmts[1])

    def test_add_filter_notbound(self):
        self.s.add_filter_notbound(Variable("a")) 
        self.assertEqual(1, len(self.s.query.whereclause.stmts))
        u1 = UnaryExpression(FunCall("bound", Variable("a")), "!")
        f1 = Filter(u1)
        self.assertEqual(f1, self.s.query.whereclause.stmts[0])
