# -*- coding: utf8 -*-

import unittest

from rdflib import Namespace, URIRef, Literal, Variable

from sparql.helpers import SelectQueryHelper
from sparql.miniast import Triple, Optional
from sparql.miniast import FunCall, BinaryExpression

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

    def test_add_variable(self):
        self.s.add_variable("varname")
        self.s.add_variable("varname")
        self.assertEqual([Variable("varname")], self.s.query.variables)

    def test_add_triple(self):
        self.s.add_triple(self.triple1)
        self.s.add_triple(self.triple1)
        self.assertEqual(1, len(self.s.query.whereclause.stmts))
        self.s.add_triple(self.triple2)
        self.assertEqual(2, len(self.s.query.whereclause.stmts))

    def test_add_optional(self):
        self.s.add_optional([self.triple1])
        self.assertEqual(1, len(self.s.query.whereclause.stmts))
        self.assertEqual(1, len(self.s.query.whereclause.stmts[0].stmts))
        self.assertEqual(Optional, self.s.query.whereclause.stmts[0].__class__)
        self.s.add_optional([self.triple1, self.triple2])
        self.assertEqual(2, len(self.s.query.whereclause.stmts))
        self.assertEqual(2, len(self.s.query.whereclause.stmts[1].stmts))
        self.assertEqual(Optional, self.s.query.whereclause.stmts[1].__class__)

    def test_add_filter(self):
        f1 = FunCall("regex", ["arg1", "arg2"])
        f2 = FunCall("regex", ["arg3", "arg4"])
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

    def test_str(self):
        expected = "SELECT WHERE{}"
        self.assertEqual(expected, str(self.s))
