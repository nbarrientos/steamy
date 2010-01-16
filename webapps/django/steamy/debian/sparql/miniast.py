# -*- coding: utf8 -*-

class SelectQuery():
    def __init__(self, distinct=False):
        self.variables = []
        self.fromgraph = None
        self.distinct = distinct
        self.whereclause = WhereClause()
        self.orderby = None
        self.modifiers = []
 

class WhereClause():
    def __init__(self):
        self.stmts = []


class Optional():
    def __init__(self, triples):
        self.stmts = triples


class Union():
    def __init__(self):
        self.graphpatterns = []


class Filter():
    def __init__(self, expr):
        self.expr = expr


class BinaryExpression():
    def __init__(self, lhs, operator, rhs):
        self.lhs = lhs
        self.operator = operator
        self.rhs = rhs

    def __str__(self):
        return "[%s %s %s]" % (self.lhs, self.operator, self.rhs)

    def __eq__(self, other):
        return self.lhs == other.lhs and \
                self.operator == other.operator and \
                self.rhs == other.rhs

class UnaryExpression():
    def __init__(self, expr, operator):
        self.expr = expr
        self.operator = operator


class FunCall():
    def __init__(self, function, args):
        self.function = function
        self.args = args

    def __str__(self):
        return "%s(%s)" % (self.function, self.args)

    def __eq__(self, other):
        return self.function == other.function and self.args == other.args

class Triple():
    def __init__(self, subject=None, property=None, object=None):
        self.subject = subject
        self.property = property
        self.object = object

    def __eq__(self, other):
        return self.subject.__eq__(other.subject) \
                and self.property.__eq__(other.property) \
                and self.object.__eq__(other.object)

class Limit():
    def __init__(self, value):
        self.value = value

class Offset():
    def __init__(self, value):
        self.value = value

class Orderby():
    def __init__(self, variable):
        self.variable = variable
