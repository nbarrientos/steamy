# -*- coding: utf8 -*-

from rdflib import Variable

from sparql.miniast import SelectQuery, Optional, Filter, Union
from sparql.miniast import Limit, Offset 

class SelectQueryHelper():
    def __init__(self):
        self.query = SelectQuery()

    def add_variable(self, varname):
        if not varname in self.query.variables:
            self.query.variables.append(Variable(varname))

    def add_triple(self, triple):
        if not triple in self.query.whereclause.stmts:
            self.query.whereclause.stmts.append(triple)

    def add_optional(self, triple_list):
        self.query.whereclause.stmts.append(Optional(triple_list))

    def add_filter(self, expr):
        self.query.whereclause.stmts.append(Filter(expr))

    def add_union(self, *args):
        if len(args) < 2:
            raise Exception("I need at least two graphpatterns to build an union")
        union = Union()
        for graphpattern in args:
            union.graphpatterns.append(graphpattern)
        self.query.whereclause.stmts.append(union)

    def add_triple_variables(self, triple):
        self.add_triple(triple)
        for k,v in triple.__dict__.items():
            if isinstance(v, Variable):
                self.add_variable(v)

    def set_limit(self, value):
        self.query.modifiers.append(Limit(value))

    def set_offset(self, value):
        self.query.modifiers.append(Offset(value))
